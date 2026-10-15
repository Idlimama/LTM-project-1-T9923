import sys, urllib.request, json
print('Python:',sys.version.split()[0])
try:
    print('Ollama:',urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=3).status)
    data=json.load(urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=3))
    print('Models:',', '.join(m['name'] for m in data.get('models',[])) or 'none')
except Exception as e: print('Ollama check failed:',e)
try:
    import fastapi,pydantic,langgraph,ollama
    print('Python packages: OK')
except Exception as e: print('Package check failed:',e)
