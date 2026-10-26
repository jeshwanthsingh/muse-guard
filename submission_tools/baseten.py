"""Offline-tested Responses -> Baseten Chat Completions bridge, outside study.
A verified input-token counter is required before live use can be enabled.
"""
import json,os,uuid,urllib.request,urllib.error
from urllib.parse import urlsplit
from muse_guard.gateway import Gateway,NoRedirect
MODEL='meta-models/muse-spark-open-1026'
BASE='https://inference.baseten.co/v1'

def configuration(env=None):
 env=os.environ if env is None else env
 key=env.get('BASETEN_API_KEY','');url=env.get('BASETEN_BASE_URL','')
 parsed=urlsplit(url)
 if parsed.scheme!='https' or parsed.netloc!='inference.baseten.co' or parsed.path.rstrip('/')!='/v1' or parsed.query or parsed.fragment:
  raise ValueError('Use the Baseten shared Model API base URL')
 if not key or any(c in key for c in '\r\n'):raise ValueError('BASETEN_API_KEY is missing or invalid')
 return key,url.rstrip('/')

def child_environment(root):
 from pathlib import Path
 root=Path(root)
 return {'PATH':os.defpath+':/opt/homebrew/bin:/usr/local/bin','HOME':str(root/'home'),'TMPDIR':str(root/'tmp'),
         'XDG_CONFIG_HOME':str(root/'config'),'LANG':'C.UTF-8','MUSE_NO_AUTO_UPDATE':'1','MUSE_CONTRIBUTOR_MODE':'0'}

def translated_tools(data):
 tools=[];mapping={}
 def add(items,prefix=''):
  for tool in items:
   name=prefix+tool.get('name','')
   if tool.get('type')=='namespace':add(tool.get('tools',[]),name+'.');continue
   if tool.get('type')!='function':raise ValueError('Only function tools are supported')
   wire=name.replace('.','__')
   if wire in mapping:raise ValueError('Ambiguous flattened tool name')
   mapping[wire]=name
   tools.append({'type':'function','function':dict({k:tool[k] for k in ('description','parameters','strict') if k in tool},name=wire)})
 add(data.get('tools',[]));return tools,mapping

def chat_request(data):
 if data.get('previous_response_id'):raise ValueError('Server-side response history is unsupported; replay full input')
 if data.get('text',{}).get('format',{}).get('type','text')!='text':raise ValueError('Structured response formatting is unsupported')
 messages=[]
 if data.get('instructions'):messages.append({'role':'system','content':data['instructions']})
 inputs=data.get('input',[])
 if isinstance(inputs,str):inputs=[{'role':'user','content':inputs}]
 for item in inputs:
  kind=item.get('type','message')
  if kind=='reasoning':
   # Encrypted native reasoning is not portable; reject instead of dropping it.
   raise ValueError('Native reasoning items are not portable to Chat Completions')
  if kind=='function_call':
   messages.append({'role':'assistant','content':None,'tool_calls':[{'id':item['call_id'],'type':'function','function':{'name':item['name'].replace('.','__'),'arguments':item['arguments']}}]});continue
  if kind=='function_call_output':messages.append({'role':'tool','tool_call_id':item['call_id'],'content':item['output']});continue
  if kind!='message' or item.get('role') not in ('user','assistant','system','developer'):raise ValueError('Unsupported input item')
  content=item.get('content','')
  if isinstance(content,list):
   if any(p.get('type') not in ('input_text','output_text','text') for p in content):raise ValueError('Only text input is supported')
   content=''.join(p['text'] for p in content)
  if not isinstance(content,str):raise ValueError('Invalid text input')
  messages.append({'role':'system' if item['role']=='developer' else item['role'],'content':content})
 tools,_=translated_tools(data)
 request={'model':MODEL,'messages':messages,'max_tokens':data.get('max_output_tokens',2048),'stream':False}
 if tools:request['tools']=tools
 # This model always reasons. Do not pretend the native effort knob is matched.
 return request

def response(packet,mapping=None):
 choices=packet.get('choices',[])
 if len(choices)!=1:raise ValueError('Expected one provider choice')
 choice=choices[0];message=choice['message'];output=[]
 if message.get('content'):
  output.append({'id':'msg_'+uuid.uuid4().hex,'type':'message','role':'assistant','status':'completed',
                 'content':[{'type':'output_text','text':message['content'],'annotations':[]}]})
 for call in message.get('tool_calls',[]):
  if call.get('type')!='function':raise ValueError('Unsupported provider tool')
  output.append({'id':'fc_'+uuid.uuid4().hex,'type':'function_call','status':'completed','call_id':call['id'],
                 'name':(mapping or {}).get(call['function']['name'],call['function']['name']),'arguments':call['function']['arguments']})
 result={'id':'resp_'+uuid.uuid4().hex,'object':'response','created_at':0,'model':MODEL,
         'status':'completed' if choice.get('finish_reason') in ('stop','tool_calls') else 'incomplete','output':output}
 usage=packet.get('usage')
 if isinstance(usage,dict):
  result['usage']={'input_tokens':usage.get('prompt_tokens'),'output_tokens':usage.get('completion_tokens'),
                   'input_tokens_details':{'cached_tokens':usage.get('prompt_tokens_details',{}).get('cached_tokens',0)}}
 return result

def stream_response(row):
 events=[]
 def add(kind,**fields):events.append({'type':kind,'sequence_number':len(events),**fields})
 add('response.created',response=dict(row,status='in_progress',output=[]))
 for index,item in enumerate(row['output']):
  added=dict(item,status='in_progress')
  if item['type']=='message':added['content']=[]
  else:added['arguments']=''
  add('response.output_item.added',output_index=index,item=added)
  if item['type']=='message':
   part=item['content'][0];add('response.content_part.added',item_id=item['id'],output_index=index,content_index=0,part=dict(part,text=''))
   add('response.output_text.delta',item_id=item['id'],output_index=index,content_index=0,delta=part['text'])
   add('response.output_text.done',item_id=item['id'],output_index=index,content_index=0,text=part['text'])
   add('response.content_part.done',item_id=item['id'],output_index=index,content_index=0,part=part)
  else:
   add('response.function_call_arguments.delta',item_id=item['id'],output_index=index,delta=item['arguments'])
   add('response.function_call_arguments.done',item_id=item['id'],output_index=index,arguments=item['arguments'])
  add('response.output_item.done',output_index=index,item=item)
 add('response.'+row['status'],response=row)
 return ''.join('event: '+e['type']+'\ndata: '+json.dumps(e)+'\n\n' for e in events).encode()

class BasetenTransport:
 """Shared Model API transport. No redirects, raw errors or credential logs."""
 def __init__(self,key,base_url):
  self.key,self.base_url=configuration({'BASETEN_API_KEY':key,'BASETEN_BASE_URL':base_url})
 def __call__(self,payload):
  request=urllib.request.Request(self.base_url+'/chat/completions',data=json.dumps(payload).encode(),
   headers={'Content-Type':'application/json','Authorization':'Bearer '+self.key})
  try:
   with urllib.request.build_opener(NoRedirect()).open(request,timeout=120) as reply:
    body=reply.read(4*1024*1024+1)
    if len(body)>4*1024*1024:raise ValueError('Provider capture limit')
    return json.loads(body)
  except Exception:raise ValueError('Baseten request failed; private provider details suppressed') from None

class BasetenGateway(Gateway):
 """Same local gateway policy and durable accounting; injected fake transport only.
 Live admission requires a validated pre-inference token counter.
 """
 def __init__(self,key,*,base_url=BASE,chat_transport=None,count_tokens=None,**kwargs):
  configuration({'BASETEN_API_KEY':key,'BASETEN_BASE_URL':base_url})
  if count_tokens is None:raise ValueError('Live Baseten blocked: verified pre-inference token counter is not configured')
  super().__init__(key,**kwargs);self.chat_transport=chat_transport or BasetenTransport(key,base_url);self.count_tokens=count_tokens
 @classmethod
 def from_env(cls,**kwargs):
  key,url=configuration();return cls(key,base_url=url,**kwargs)
 def forward(self,path,data):
  chat=chat_request(data)
  if path=='/responses/input_tokens':
   count=self.count_tokens(chat)
   if type(count) is not int or count<0:raise ValueError('Invalid token count')
   return 200,'application/json',json.dumps({'input_tokens':count}).encode()
  if path!='/responses':raise ValueError('Unsupported route')
  try:row=response(self.chat_transport(chat),translated_tools(data)[1])
  except Exception:raise ValueError('Baseten response failed; private provider details suppressed') from None
  return (200,'text/event-stream',stream_response(row)) if data.get('stream') else (200,'application/json',json.dumps(row).encode())
 def persist_usage(self):
  for event in self.events:
   if not event.get('blocked'):
    event['model']=MODEL;event['provider']='baseten';event['pricing_mode']='BASETEN_MODEL_API'
  super().persist_usage()
