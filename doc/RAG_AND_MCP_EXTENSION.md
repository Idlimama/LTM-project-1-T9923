# RAG and MCP Extension
This enhancement adds dependency-free BM25 retrieval for transcript evidence. Use segment IDs as citations in agent outputs.

## Current retrieval
1. Parse transcript lines into stable segment IDs.
2. Rank segments with BM25.
3. Pass only top evidence segments to specialist agents.
4. Display IDs, timestamps, text, and retrieval scores.

## Recommended next hybrid retrieval
Keep BM25. Add an Ollama embedding provider later. Retrieve top lexical and semantic candidates, fuse rankings, then rerank only the small merged set. Never replace evidence citations with model memory.

## Safety
Treat transcript and retrieved policy text as untrusted evidence. Retrieved text cannot change system instructions or tool permissions.
