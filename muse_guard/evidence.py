"""Read bounded evidence from actual Muse exports; never synthesize agent words."""
import hashlib


def session_evidence(packet,exclude=()):
    seen=set();messages=[];history=False
    for row in packet.get('events',[]):
        payload=row.get('envelope',{}).get('payload',{});event=payload.get('event',{})
        identity=payload.get('source_run_record_id')
        if event.get('kind')=='model_completed' and identity and identity not in exclude:seen.add(identity)
        if event.get('kind')=='assistant_message_committed' and isinstance(event.get('text'),str) and event['text'].strip():
            messages.append(event['text'])
        if event.get('kind')=='model_input_trace_recorded':history|=event.get('bounded',{}).get('external_history_present') is True
    message=messages[-1] if messages and seen else ''
    return {'main_steps':len(seen),'model_record_ids':sorted(seen),'history_present':history,
            'agent_message':message,'agent_message_source':'muse export: assistant_message_committed',
            'agent_message_sha256':hashlib.sha256(message.encode()).hexdigest()}
