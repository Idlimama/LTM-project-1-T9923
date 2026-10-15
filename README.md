# Marketing Governance Council — Functional Review Build

This build prioritizes a real end-to-end governance path over the full product specification.

## Implemented
- Python FastAPI backend split into API, agents, providers, services, governance and database modules.
- Ollama / `qwen2.5:3b` structured extraction and specialist outputs.
- Growth, Audit, Finance and Audience specialists.
- One bounded peer-review round.
- Deterministic budget calculations and hard gates.
- SQLite evaluation history and human disposition storage.
- Policy retrieval against a small synthetic review policy pack.
- Browser council console, event stream, specialist transparency, score chart, history, policy and system tabs.
- Transparent fallback if an Ollama call fails.

## Data disclosure
`data/sample_campaign_transcript.txt` and `data/policies.json` are synthetic review data. Do not describe them as real company or regulatory data.

## Start on Windows
1. Keep Ollama running.
2. Open PowerShell in the project folder.
3. Run `ollama pull qwen2.5:3b`.
4. Run `py -m venv .venv`.
5. Run `.venv\Scripts\Activate.ps1`.
6. Run `pip install -r requirements.txt`.
7. Run `uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
8. Open `http://127.0.0.1:8000` in the browser.
9. Upload `data/sample_campaign_transcript.txt`.
10. Select **RUN COUNCIL**.

## Review statement
“This is the functional review build. The implemented core performs local model-backed extraction and specialist analysis, bounded peer review, deterministic governance checks, persistence and human disposition. The policy pack and demonstration transcript are synthetic and explicitly labeled. The complete design adds richer retrieval, orchestration and interface layers around these stable contracts.”

## Orchestration
The active review workflow uses a real LangGraph `StateGraph` in `backend/orchestration/graph.py`. The graph has explicit extraction, finance, policy retrieval, specialist council, bounded peer-review and deterministic governance nodes. This is deliberately a small graph so the review build remains understandable and recoverable.

## Offline UI
The score visualization uses native CSS. It does not require a chart CDN or internet connection.
