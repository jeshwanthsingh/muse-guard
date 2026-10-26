"""Local token gate for Muse 1.4.2; only Standard Spark inference is forwarded.
New implementation. No Unfoolable code is copied here.
"""
from decimal import Decimal, ROUND_FLOOR
import http.server
import json
import os
from pathlib import Path
import threading
import urllib.request
import urllib.error

MODEL = "muse-spark-1.3"


def local_function_tools(tools):
    if not isinstance(tools,list):
        return False
    for tool in tools:
        if not isinstance(tool,dict):
            return False
        if tool.get("type") == "function":
            continue
        if tool.get("type") == "namespace" and local_function_tools(tool.get("tools")):
            continue
        return False
    return True


def response_usage(body):
    packets = []
    try:
        packets.append(json.loads(body))
    except ValueError:
        for line in body.splitlines():
            if line.startswith(b"data:"):
                try:
                    packets.append(json.loads(line[5:].strip()))
                except ValueError:
                    pass
    for packet in reversed(packets):
        if not isinstance(packet,dict):
            continue
        terminal_event = packet.get("type") in ("response.completed","response.incomplete","response.failed")
        terminal_response = packet.get("status") in ("completed","incomplete","failed")
        if not terminal_event and not terminal_response:
            continue
        response = packet.get("response",packet)
        if not isinstance(response,dict):
            continue
        usage = response.get("usage")
        if isinstance(usage,dict) and type(usage.get("input_tokens")) is int and type(usage.get("output_tokens")) is int:
            details = usage.get("input_tokens_details",{})
            cached = details.get("cached_tokens",0) if isinstance(details,dict) else None
            if (usage["input_tokens"] < 0 or usage["output_tokens"] < 0 or type(cached) is not int or
                    not 0 <= cached <= usage["input_tokens"]):
                return None
            return {"input_tokens":usage["input_tokens"],"output_tokens":usage["output_tokens"],
                    "cached_input_tokens":cached}
    return None


class TokenBudget:
    def __init__(self, limit):
        if type(limit) is not int or limit <= 0:
            raise ValueError("Invalid token budget")
        self.limit = limit
        self.reserved_tokens = 0

    def admit(self, input_tokens, requested_output):
        if type(input_tokens) is not int or input_tokens < 0 or type(requested_output) is not int or requested_output <= 0:
            raise ValueError("Invalid provider token count or output limit")
        output = min(requested_output, 2048, self.limit - self.reserved_tokens - input_tokens)
        if output < 1:
            raise ValueError("Per-run token budget exhausted")
        self.reserved_tokens += input_tokens + output
        return output


class DollarBudget:
    """Serial request quota; unknown usage never releases its reservation."""
    def __init__(self,limit):
        self.limit=Decimal(str(limit));self.spent=Decimal(0);self.pending=Decimal(0);self.unknown=False
        if not self.limit.is_finite() or self.limit<=0:raise ValueError("Invalid dollar quota")
    def admit(self,input_tokens,requested_output):
        if self.unknown or self.pending:raise ValueError("Prior provider usage is unresolved")
        if type(input_tokens) is not int or input_tokens<0 or type(requested_output) is not int or requested_output<=0:
            raise ValueError("Invalid dollar reservation")
        input_cost=Decimal(input_tokens)*Decimal('1.25')/1000000
        output=int(((self.limit-self.spent-input_cost)*1000000/Decimal('4.25')).to_integral_value(rounding=ROUND_FLOOR))
        output=min(output,requested_output)
        if output<1:raise ValueError("Daily dollar quota exhausted")
        self.pending=input_cost+Decimal(output)*Decimal('4.25')/1000000
        return output
    def settle(self,usage):
        if usage is None:self.unknown=True;return
        actual=(Decimal(usage['input_tokens']-usage['cached_input_tokens'])*Decimal('1.25')+
                Decimal(usage['cached_input_tokens'])*Decimal('.15')+Decimal(usage['output_tokens'])*Decimal('4.25'))/1000000
        if actual>self.pending or actual<0:
            self.unknown=True;raise ValueError("Provider usage exceeded request reservation")
        self.spent+=actual;self.pending=Decimal(0)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("Provider redirects refused")


class Gateway:
    def __init__(self, key, token_limit=160000, transport=None, journal=None, dollar_limit=None):
        self.key = key
        self.dollars= DollarBudget(dollar_limit) if dollar_limit is not None else None
        self.budget = TokenBudget(token_limit)
        self.transport = transport
        self.events = []
        self.lock = threading.Lock()
        self.closing = False
        self.closed = False
        self.journal = Path(journal) if journal else None

    def persist_usage(self):
        if self.journal:
            self.journal.parent.mkdir(parents=True,exist_ok=True)
            pending = self.journal.with_suffix(".pending")
            pending.write_text(json.dumps({"schema_version":1,"requests":self.events},indent=2)+"\n")
            pending.chmod(0o600)
            os.replace(pending,self.journal)

    def forward(self, path, data):
        if self.transport:
            return 200, "application/json", json.dumps(self.transport(path, data)).encode()
        request = urllib.request.Request("https://api.meta.ai/v1" + path,
            data=json.dumps(data).encode(), headers={"Authorization":"Bearer " + self.key,
            "Content-Type":"application/json", "Accept":"text/event-stream, application/json"})
        opener = urllib.request.build_opener(NoRedirect())
        try:
            with opener.open(request, timeout=120) as response:
                body = response.read(4 * 1024 * 1024 + 1)
                if len(body) > 4 * 1024 * 1024:
                    raise ValueError("Provider output capture limit exceeded")
                return response.status, response.headers.get("Content-Type", "application/json"), body
        except urllib.error.HTTPError as error:
            # Never return the provider's raw error text; it might echo secrets.
            return error.code, "application/json", json.dumps({"error":{"type":"provider_error", "message":"Meta returned HTTP " + str(error.code)}}).encode()

    def __enter__(self):
        owner = self
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def reply(self, status, kind, body):
                try:
                    self.send_response(status)
                    self.send_header("Content-Type", kind)
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except (BrokenPipeError,ConnectionResetError):
                    # Muse may cancel reminder clients after the main turn ends.
                    # Actual provider usage was persisted before this write.
                    return

            def do_GET(self):
                if self.path not in ("/muse-code/models", "/v1/muse-code/models", "/models", "/v1/models"):
                    self.reply(404,"application/json",b"{}")
                    return
                # Pin the catalog so CLI defaults and fallback agents cannot select
                # Wonder, Contributor, hosted tools, or a differently priced model.
                body = {"object":"list","data":[{"id":MODEL,"object":"model","created":0,"owned_by":"meta"}]}
                self.reply(200,"application/json",json.dumps(body).encode())

            def do_POST(self):
                with owner.lock:
                    try:
                        if owner.closing:
                            raise ValueError("Gateway is closing")
                        if self.path not in ("/responses", "/v1/responses"):
                            raise ValueError("Only Responses inference is allowed")
                        length = int(self.headers.get("Content-Length", "0"))
                        if not 0 < length <= 2 * 1024 * 1024:
                            raise ValueError("Invalid request size")
                        data = json.loads(self.rfile.read(length))
                        if not isinstance(data,dict):
                            raise ValueError("Invalid request body")
                        allowed = {"model","input","instructions","max_output_tokens","store","tools",
                                   "reasoning","include","prompt_cache_key","stream","previous_response_id","text"}
                        if set(data) - allowed:
                            raise ValueError("Unsupported request fields cannot be counted safely")
                        data["model"] = MODEL
                        if not local_function_tools(data.get("tools", [])):
                            raise ValueError("Hosted tools are disabled for budget accounting")
                        # Count the same reconstructed context before every inference.
                        count_body = {k:v for k,v in data.items() if k in
                            ("model","input","instructions","tools","previous_response_id","reasoning","text")}
                        status, kind, body = owner.forward("/responses/input_tokens", count_body)
                        if status != 200:
                            self.reply(status,kind,body)
                            return
                        if owner.closing:
                            raise ValueError("Gateway is closing")
                        counted = json.loads(body).get("input_tokens")
                        requested=data.get("max_output_tokens",2048)
                        if owner.dollars:requested=owner.dollars.admit(counted,min(requested,2048))
                        data["max_output_tokens"] = owner.budget.admit(counted,requested)
                        owner.events.append({"model":MODEL,"pricing_mode":"STANDARD","input_tokens_reserved":counted,
                                             "max_output_tokens":data["max_output_tokens"]})
                        owner.persist_usage()  # reservation exists before first inference
                        status, kind, body = owner.forward("/responses", data)
                        owner.events[-1]["usage"] = response_usage(body)
                        if owner.dollars:owner.dollars.settle(owner.events[-1]["usage"])
                        owner.persist_usage()  # actual usage durable before CLI receives output
                        self.reply(status,kind,body)
                    except (ValueError, TypeError, AttributeError, OSError, urllib.error.URLError):
                        owner.events.append({"blocked":True,"reason":"local policy or token count rejected request"})
                        owner.persist_usage()
                        body = b'{"error":{"type":"budget_error","message":"Request refused by local token gate"}}'
                        self.reply(400,"application/json",body)
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
        self.server.daemon_threads = False
        self.url = "http://127.0.0.1:" + str(self.server.server_port)
        self.thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        return self

    def stop(self):
        if self.closed:
            return
        self.closing = True
        self.server.shutdown()
        # Non-daemon request workers are drained before exporting/accounting.
        self.server.server_close()
        self.thread.join(timeout=2)
        self.closed = True

    def __exit__(self, *args):
        self.stop()
