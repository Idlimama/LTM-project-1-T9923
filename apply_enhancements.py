from pathlib import Path
import shutil,sys
ROOT=Path.cwd()
required=[ROOT/'backend/orchestration/graph.py',ROOT/'backend/services/evaluator.py',ROOT/'backend/api/routes.py',ROOT/'backend/agents/specialists.py',ROOT/'backend/providers/policy.py',ROOT/'index.html']
missing=[str(p) for p in required if not p.exists()]
if missing:raise SystemExit('Run this from the reviewed mgc_full root. Missing: '+', '.join(missing))
PACK=Path(__file__).resolve().parent
(ROOT/'backend/retrieval').mkdir(exist_ok=True)
for rel in ['backend/retrieval/__init__.py','backend/retrieval/bm25.py','backend/retrieval/transcript.py','tests/test_retrieval.py','docs/RAG_AND_MCP_EXTENSION.md']:
 dst=ROOT/rel;dst.parent.mkdir(parents=True,exist_ok=True);src=PACK/rel; shutil.copy2(src,dst) if src.resolve() != dst.resolve() else None
def patch(path,old,new,required=True):
 p=ROOT/path;s=p.read_text(encoding='utf-8')
 if old not in s:
  if required:raise SystemExit(f'Patch anchor missing in {path}: {old[:70]}')
  return
 p.write_text(s.replace(old,new),encoding='utf-8')
# policy BM25
(ROOT/'backend/providers/policy.py').write_text('''import json\nfrom pathlib import Path\nfrom backend.retrieval.bm25 import BM25Index\nP=Path(__file__).resolve().parents[2]/"data"/"policies.json"\ndef all_policies():return json.loads(P.read_text(encoding="utf-8"))\ndef retrieve(text,k=4):\n docs=[{"id":p["id"],"text":p["title"]+" "+p["text"],"metadata":p} for p in all_policies()]\n return [{**h.metadata,"retrieval_score":h.score} for h in BM25Index(docs).search(text,k)]\n''',encoding='utf-8')
# agent evidence input
patch('backend/agents/specialists.py','def run(name,campaign,finance,policies):','def run(name,campaign,finance,policies,evidence_hits=None):')
patch('backend/agents/specialists.py',"'policies':policies}","'policies':policies,'retrieved_transcript_evidence':evidence_hits or []}")
# graph
patch('backend/orchestration/graph.py','from backend.models import AgentResult','from backend.models import AgentResult\nfrom backend.retrieval.transcript import segment_transcript,retrieve_evidence')
patch('backend/orchestration/graph.py','    policies: list[dict]\n','    policies: list[dict]\n    transcript_segments: list[dict]\n    evidence_hits: list[dict]\n')
node='''\ndef evidence_node(state):\n    c=state['campaign'];query=' '.join([c.objective or '',c.audience or '',' '.join(c.claims),' '.join(c.channels)])\n    segments=segment_transcript(state['text']);hits=retrieve_evidence(state['text'],query or state['text'][:500],6)\n    return {'transcript_segments':segments,'evidence_hits':hits,'events':_event(state,'EVIDENCE',f'{len(hits)} transcript evidence segments retrieved with BM25.')}\n'''
patch('backend/orchestration/graph.py','\ndef finance_node(state):',node+'\ndef finance_node(state):')
patch('backend/orchestration/graph.py',"a=run(name,state['campaign'],state['finance'],state['policies'])","a=run(name,state['campaign'],state['finance'],state['policies'],state.get('evidence_hits',[]))")
patch('backend/orchestration/graph.py',"g.add_node('extract',extract_node); g.add_node('finance',finance_node);","g.add_node('extract',extract_node); g.add_node('evidence',evidence_node); g.add_node('finance',finance_node);")
patch('backend/orchestration/graph.py',"g.add_edge(START,'extract'); g.add_edge('extract','finance');","g.add_edge(START,'extract'); g.add_edge('extract','evidence'); g.add_edge('evidence','finance');")
# output
patch('backend/services/evaluator.py',"'policies':state['policies'],","'policies':state['policies'],'transcript_segments':state.get('transcript_segments',[]),'evidence_hits':state.get('evidence_hits',[]),")
patch('backend/services/evaluator.py',"'runtime_s':round(time.perf_counter()-start,2)}","'runtime_s':round(time.perf_counter()-start,2),'metrics':{'segments_parsed':len(state.get('transcript_segments',[])),'evidence_hits':len(state.get('evidence_hits',[])),'policies_retrieved':len(state.get('policies',[])),'fields_present':sum(v not in (None,[],'') for v in state['campaign'].model_dump().values()),'fields_total':len(state['campaign'].model_dump())}}")
# API endpoints
p=ROOT/'backend/api/routes.py';s=p.read_text(encoding='utf-8')
if 'retrieve_evidence' not in s:s=s.replace('from backend.providers.ollama_provider import MODEL','from backend.providers.ollama_provider import MODEL\nfrom backend.retrieval.transcript import retrieve_evidence\nfrom fastapi.responses import PlainTextResponse')
if "/retrieval/preview" not in s:s+='''\n@r.post('/retrieval/preview')\nasync def preview(file:UploadFile|None=File(default=None),text:str=Form(default=''),query:str=Form(default='marketing campaign budget audience claim')):\n raw=(await file.read()).decode('utf-8','ignore') if file else text\n return {'query':query,'hits':retrieve_evidence(raw,query,8)}\n@r.get('/evaluations/{eid}/report',response_class=PlainTextResponse)\ndef report(eid:str):\n x=get_eval(eid)\n if not x:return 'Evaluation not found.'\n lines=[f"# Evaluation {eid}",'',f"Status: {x['status']}",f"Council score: {x['score']}/100",'',x['summary'],'','## Gates']+[f"- {g['code']}: {g['reason']}" for g in x['gates']]\n return '\\n'.join(lines)\n'''
p.write_text(s,encoding='utf-8')
# UI: add Evidence tab and result metrics without changing existing control flow
p=ROOT/'index.html';s=p.read_text(encoding='utf-8')
s=s.replace('<a data-page="policies">POLICIES</a>','<a data-page="evidence">EVIDENCE</a><a data-page="policies">POLICIES</a>')
evidence='''<main id="evidence" class="page"><div class="box amber"><h2>Evidence Retrieval Lab</h2><p class="muted">Inspect BM25-ranked transcript segments.</p><input id="ragFile" type="file" accept=".txt,.vtt"><input id="ragQuery" value="budget audience guarantee evidence channels"><button onclick="previewRag()">RETRIEVE EVIDENCE</button><div id="ragResult"></div></div></main>\n'''
s=s.replace('<main id="policies" class="page">',evidence+'<main id="policies" class="page">')
metric='<h3>Retrieval metrics</h3><div class="kpis"><div class="kpi">SEGMENTS<br><b>${x.metrics.segments_parsed}</b></div><div class="kpi">EVIDENCE<br><b>${x.metrics.evidence_hits}</b></div><div class="kpi">POLICIES<br><b>${x.metrics.policies_retrieved}</b></div><div class="kpi">FIELDS<br><b>${x.metrics.fields_present}/${x.metrics.fields_total}</b></div></div><details><summary>Retrieved transcript evidence</summary>${x.evidence_hits.map(h=>`<p><b>${h.segment_id}</b> [${h.timestamp||\'no timestamp\'}] score ${h.score}<br>${esc(h.text)}</p>`).join(\'\')}</details><p><a style="color:#43b4d8" target="_blank" href="/api/evaluations/${x.id}/report">OPEN REPORT</a></p><h3>Deterministic finance</h3>'
s=s.replace('<h3>Deterministic finance</h3>',metric)
fn="""\nasync function previewRag(){let f=new FormData();if($('ragFile').files[0])f.append('file',$('ragFile').files[0]);f.append('query',$('ragQuery').value);let x=await fetch('/api/retrieval/preview',{method:'POST',body:f}).then(r=>r.json());$('ragResult').innerHTML='<h3>Ranked evidence</h3>'+x.hits.map(h=>`<details open><summary>${h.segment_id} â€” score ${h.score}</summary><p>${esc(h.text)}</p><small>${esc(h.timestamp||'no timestamp')} ${esc(h.speaker||'')}</small></details>`).join('')}\n"""
s=s.replace('async function loadPolicies()',fn+'\nasync function loadPolicies()')
p.write_text(s,encoding='utf-8')
print('Enhancements applied. Run: python -m py_compile backend/**/*.py ; pytest -q')

