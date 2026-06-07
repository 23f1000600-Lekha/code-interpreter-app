from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from io import StringIO
import sys
import traceback
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

class CodeResponse(BaseModel):
    error: List[int]
    result: str


def execute_python_code(code: str) -> dict:
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code, {})
        output = sys.stdout.getvalue()
        return {"success": True, "output": output}

    except Exception:
        output = traceback.format_exc()
        return {"success": False, "output": output}

    finally:
        sys.stdout = old_stdout


def analyze_error_lines(traceback_text: str) -> List[int]:
    matches = re.findall(r'line (\d+)', traceback_text)
    if matches:
        return [int(matches[-1])]
    return []


@app.post("/code-interpreter", response_model=CodeResponse)
def code_interpreter(request: CodeRequest):
    execution_result = execute_python_code(request.code)

    if execution_result["success"]:
        return {
            "error": [],
            "result": execution_result["output"]
        }

    error_lines = analyze_error_lines(execution_result["output"])

    return {
        "error": error_lines,
        "result": execution_result["output"]
    }


@app.get("/")
def home():
    return {"message": "Code interpreter API is running"}