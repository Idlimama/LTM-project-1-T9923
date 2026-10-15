MCP V4 ENHANCEMENT PACK
1. Extract this ZIP anywhere.
2. Copy apply_enhancements.py and the backend/tests/docs folders into the reviewed mgc_full folder.
3. Open PowerShell in mgc_full.
4. Run: python apply_enhancements.py
5. Run: pip install -r requirements.txt
6. Run: pytest -q
7. Run: uvicorn backend.main:app --host 127.0.0.1 --port 8000

Adds real BM25 transcript and policy retrieval, Evidence tab, retrieval metrics, retrieved evidence trace, and report endpoint.
