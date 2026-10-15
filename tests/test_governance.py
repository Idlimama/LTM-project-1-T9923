from backend.models import Campaign
from backend.governance.finance import calculate
from backend.governance.gates import apply
def test_budget_gate():
    c=Campaign(authorized_budget=100000,proposed_spend=120000)
    f=calculate(c); assert f['variance']==20000 and f['gate']
    assert apply(c,f,None)[0]['code']=='HARD_BUDGET_VIOLATION'
