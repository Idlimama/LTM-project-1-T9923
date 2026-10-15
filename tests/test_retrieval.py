from backend.retrieval.transcript import retrieve_evidence,segment_transcript
def test_budget_rank():
 t='00:00:01 - Lead: Idea\n00:00:05 - Finance: Authorized budget INR 100000\n00:00:09 - Lead: Retail audience'
 assert '100000' in retrieve_evidence(t,'authorized budget finance',2)[0]['text']
def test_ids():assert [x['id'] for x in segment_transcript('A\nB')]==['SEG-001','SEG-002']
