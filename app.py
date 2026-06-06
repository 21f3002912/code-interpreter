from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import sys
import io
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str


def execute_python_code(code: str):
    old_stdout = sys.stdout
    buffer = io.StringIO()
    sys.stdout = buffer

    try:
        exec(code, {})
        output = buffer.getvalue()

        return {
            "success": True,
            "output": output
        }

    except Exception:
        return {
            "success": False,
            "output": traceback.format_exc()
        }

    finally:
        sys.stdout = old_stdout


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/code-interpreter")
def code_interpreter(req: CodeRequest):

    result = execute_python_code(req.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"]
        }

    tb = result["output"]

    # Only extract line numbers from the user's code
    lines = []

    for match in re.finditer(r'File "<string>", line (\d+)', tb):
        lines.append(int(match.group(1)))

    return {
        "error": sorted(set(lines)),
        "result": tb
    }