from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import orjson
import time

app = FastAPI(title="Mock Upstream", version="0.0.1")

def _json(data: dict):
    return orjson.dumps(data)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/v1/autocomplete")
async def autocomplete(request: Request):
    body = await request.json()
    return {
        "completion": "/* mock completion */",
        "echo": body,
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
    }

@app.post("/v1/chat")
async def chat(request: Request):
    body = await request.json()
    return {
        "message": {"role": "assistant", "content": "mock chat response"},
        "echo": body,
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
    }

@app.post("/v1/agent")
async def agent(request: Request):
    body = await request.json()
    # gateway가 diff hash를 계산할 수 있도록 unified diff 포맷을 포함
    diff = (
        "--- a/README.md\n"
        "+++ b/README.md\n"
        "@@ -1,1 +1,2 @@\n"
        "-old\n"
        "+new\n"
        "+another\n"
    )
    return {
        "result": {
            "diff": diff,
            "summary": "mock agent produced a diff",
        },
        "echo": body,
        "usage": {"prompt_tokens": 2, "completion_tokens": 2},
    }

@app.post("/v1/rag/query")
async def rag_query(request: Request):
    body = await request.json()
    return {
        "answers": [{"text": "mock rag answer", "score": 0.5}],
        "echo": body,
    }

@app.post("/v1/rag/index")
async def rag_index(request: Request):
    body = await request.json()
    return {"status": "ok", "echo": body}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def fallback(path: str, request: Request):
    # SSE 흉내: accept가 text/event-stream이면 chunk 3개를 흘려준다
    if "text/event-stream" in request.headers.get("accept", ""):
        def gen():
            for i in range(3):
                yield f"data: {i}\n\n".encode("utf-8")
                time.sleep(0.05)
        return StreamingResponse(gen(), media_type="text/event-stream")
    return {"error": "not_found", "path": path}

