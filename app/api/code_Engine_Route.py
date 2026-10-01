from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
import judge0api
import os

router = APIRouter()

JUDGE0_URL = os.getenv("JUDGE0_URL", "http://localhost:2358")
client = judge0api.Client(JUDGE0_URL)
client.wait = True

def _decode(val: bytes | str | None) -> str | None:
    if val is None:
        return None
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return str(val)

class CodeExecutionRequest(BaseModel):
    source_code: str = Field(..., min_length=1, description="Source code to execute")
    language_id: int = Field(..., gt=0, description="Judge0 language ID")
    stdin: str = Field(default="", description="Standard input for the program")

    @field_validator("source_code")
    @classmethod
    def normalize_source_code(cls, value: str) -> str:
        value = value.replace("\r\n", "\n").replace("\r", "\n")
        return value.strip()

class CodeExecutionResponse(BaseModel):
    token: str | None = None
    status_id: int | None = None
    status: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    compile_output: str | None = None
    time: str | None = None
    memory: int | None = None
    message: str | None = None

@router.post("/run", response_model=CodeExecutionResponse)
def execute_code(request: CodeExecutionRequest):
    try:
        submission = judge0api.submission.submit(
            client,
            source_code=request.source_code.encode("utf-8"),
            language=request.language_id,
            stdin=request.stdin.encode("utf-8") if request.stdin else None,
        )

        status_id = None
        status_desc = None
        if hasattr(submission, "status") and submission.status:
            if isinstance(submission.status, dict):
                status_id = submission.status.get("id")
                status_desc = submission.status.get("description")
            elif hasattr(submission.status, "id"):
                status_id = getattr(submission.status, "id", None)
                status_desc = getattr(submission.status, "description", None)

        return CodeExecutionResponse(
            token=getattr(submission, "token", None),
            status_id=status_id,
            status=status_desc,
            stdout=_decode(getattr(submission, "stdout", None)),
            stderr=_decode(getattr(submission, "stderr", None)),
            compile_output=_decode(getattr(submission, "compile_output", None)),
            time=str(submission.time) if getattr(submission, "time", None) is not None else None,
            memory=int(submission.memory) if getattr(submission, "memory", None) is not None else None,
            message=_decode(getattr(submission, "message", None)),
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail={"message": "Code execution failed", "error": str(exc)})