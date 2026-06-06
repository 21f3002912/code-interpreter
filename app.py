from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/code-interpreter")
def code_interpreter():
    return {
        "error": [],
        "result": "test"
    }