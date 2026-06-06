from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import sys
import io

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


@app.get("/")
def root():
    return {"status": "ok"}


def execute_python_code(code: str):
    old_stdout = sys.stdout
    buffer = io.StringIO()
    sys.stdout = buffer

    try:
        exec(code, {})

        return {
            "success": True,
            "output": buffer.getvalue()
        }

    except Exception as e:
        tb = traceback.format_exc()

        line_no = None

        # SyntaxError / IndentationError
        if hasattr(e, "lineno") and e.lineno is not None:
            line_no = e.lineno

        # Runtime errors
        elif e.__traceback__:
            tb_obj = e.__traceback__

            while tb_obj.tb_next:
                tb_obj = tb_obj.tb_next

            line_no = tb_obj.tb_lineno

        return {
            "success": False,
            "output": tb,
            "line": line_no
        }

    finally:
        sys.stdout = old_stdout


@app.post("/code-interpreter")
def code_interpreter(req: CodeRequest):

    result = execute_python_code(req.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"]
        }

    error_lines = []

    if result.get("line") is not None:
        error_lines = [result["line"]]

    return {
        "error": error_lines,
        "result": result["output"]
    }