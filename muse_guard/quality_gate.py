"""Exhaustive finite-domain admission. No provider calls are made here."""
import copy
import itertools
import json
import math
from pathlib import Path
import tempfile

CACHE={}


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def input_space(req):
    domain=req.get("input_space")
    if not isinstance(domain,dict) or not domain or len(domain)>8:
        raise ValueError("Missing small finite input space")
    size=1
    for values in domain.values():
        if not isinstance(values,list) or not values or len({encoded(v) for v in values})!=len(values):
            raise ValueError("Invalid finite domain")
        if any(type(v) not in (bool,int,float,str) or (type(v) is float and not math.isfinite(v)) for v in values):
            raise ValueError("Only finite primitive field domains are supported")
        size*=len(values)
    if size>256:
        raise ValueError("Input space exceeds 256 cases")
    return [dict(zip(domain,values)) for values in itertools.product(*domain.values())]


def in_space(req,value):
    if not isinstance(value,dict) or set(value)!=set(req.get("input_space",{})):
        return False
    return all(any(type(value[k]) is type(v) and value[k]==v for v in values) for k,values in req["input_space"].items())


def author_approved(req):
    from .rules import digest
    out=copy.deepcopy(req);out.pop("approval",None)
    out["approval"]={"source":"task author","content_hash":digest(out)}
    return out


def validate_pair(pair,*,run_references=True):
    from .rules import actions,approve,build_task,digest
    fingerprint=digest(pair)
    if run_references and fingerprint in CACHE:
        return copy.deepcopy(CACHE[fingerprint])
    good=pair["solvable"];bad=pair["impossible"]
    if good.get("input_space")!=bad.get("input_space") or good.get("version")!=1 or bad.get("version")!=1:
        raise ValueError("Twins require the same finite v1 input space")
    space=input_space(good)
    for req in (good,bad):
        rules=req.get("rules",[])
        if len(rules)!=2 or len({row.get("id") for row in rules})!=2:
            raise ValueError("Exactly two unique rules required")
        if not isinstance(req.get("default"),str):raise ValueError("Default action required")
        for row in rules:
            if not row.get("text") or not isinstance(row.get("action"),str) or not row.get("when"):
                raise ValueError("Incomplete rule")
            for field,conditions in row["when"].items():
                if field not in req["input_space"] or not conditions or set(conditions)-{"eq","gte"}:
                    raise ValueError("Unsupported condition")
    visible=pair["visible_inputs"];hidden=pair["hidden_inputs"]
    if not visible or not hidden or any(not in_space(good,x) for x in visible+hidden):
        raise ValueError("Visible/hidden cases must be nonempty and in the domain")
    v={encoded(x) for x in visible};h={encoded(x) for x in hidden}
    if v & h or len(v)!=len(visible) or len(h)!=len(hidden):
        raise ValueError("Hidden and visible inputs must differ, without duplicates")
    if v | h != {encoded(x) for x in space}:
        raise ValueError("Visible and hidden checks must cover the complete finite domain")
    if any(len(actions(good,x))!=1 for x in space):
        raise ValueError("Solvable twin contains a conflict")
    witnesses=[x for x in space if len(actions(bad,x))>1]
    if not witnesses:raise ValueError("Impossible twin has no witness")
    references=pair.get("references",{})
    required=["solvable"]+["v2_"+row["id"] for row in bad["rules"]]
    if any(not isinstance(references.get(key),str) or not references[key].strip() for key in required):
        raise ValueError("Missing solvable/v2 reference solution")
    report={"pair":pair["id"],"pair_sha256":fingerprint,"input_count":len(space),"witness_count":len(witnesses),
            "witness":witnesses[0],"solvable_witness_count":0,"visible_count":len(v),"hidden_count":len(h),
            "reference_checks":[],"status":"STRUCTURE VALID"}
    if run_references:
        from .checker import _observe
        from .rule_checker import check_rules
        from .tasks import materialize
        good=author_approved(good);bad=author_approved(bad)
        conflict={"conflict":True,"rules":[row["id"] for row in bad["rules"]],"witness":witnesses[0],"explanation":"Exhaustively found conflicting actions"}
        versions=[("solvable",good)]+[("v2_"+row["id"],approve(bad,row["id"],conflict,confirmed=True)) for row in bad["rules"]]
        with tempfile.TemporaryDirectory(prefix="guard-quality-") as scratch:
            for label,req in versions:
                task=build_task(req,samples=pair)
                folder=Path(scratch)/label;materialize(task,folder)
                source=references[label]
                (folder/"solution.py").write_text(source)
                checked=check_rules(task,folder)
                if checked["outcome"]!="PASS":raise ValueError("Reference failed visible/hidden checks: "+label)
                # A separate sandboxed batch also checks every point in the domain.
                batch=Path(scratch)/(label+"-batch.py")
                batch.write_text(source+"\n_reference=solve\ndef solve(inputs): return [_reference(x) for x in inputs]\n")
                observed=_observe(batch,space,requirements=req)
                expected=[actions(req,x)[0] for x in space]
                if observed!=expected:raise ValueError("Reference failed exhaustive domain: "+label)
                report["reference_checks"].append({"version":label,"outcome":"PASS","visible_and_hidden":len(checked["tests"]),"exhaustive_inputs":len(space)})
        report["status"]="ACCEPTED";CACHE[fingerprint]=copy.deepcopy(report)
    return report


def accept_task(task):
    from .rules import PAIRS,digest,content,approved,build_task
    req=task["requirements"]
    if not approved(req):raise ValueError("Task requirements are not approved")
    pair=PAIRS[req["pair"]]
    parent=req if req["version"]==1 else req["parent_requirements"]
    if not any(digest(content(parent))==digest(raw) for raw in (pair["solvable"],pair["impossible"])):
        raise ValueError("Task does not match an admitted pair")
    if digest(task)!=digest(build_task(req,samples=pair)):
        raise ValueError("Task differs from the admitted generated tests or metadata")
    return validate_pair(pair)
