from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import judge0


router = APIRouter(
    prefix="/api/code",
    tags=["Code Execution"],
)


# ---------------------------------------------------------
# Judge0 Client
# ---------------------------------------------------------

JUDGE0_URL = "http://localhost:2358"

client = judge0.Judge0Client(base_url=JUDGE0_URL)


# ---------------------------------------------------------
# Supported Languages
# ---------------------------------------------------------

ALLOWED_LANGUAGES = {
    50: "C",
    54: "C++",
    62: "Java",
    63: "JavaScript",
    71: "Python",
    73: "Rust",
    74: "TypeScript",
}


# ---------------------------------------------------------
# Request Schema
# ---------------------------------------------------------

class CodeExecutionRequest(BaseModel):
    source_code: str = Field(...,min_length=1,description="Source code to execute")

    language_id: int = Field(...,gt=0,description="Judge0 language ID")

    stdin: str = Field(default="",description="Standard input for the program")


# ---------------------------------------------------------
# Response Schema
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Execute Code
# ---------------------------------------------------------

@router.post(
    "/execute",
    response_model=CodeExecutionResponse
)
async def execute_code(
    request: CodeExecutionRequest
):

    # Validate language
    if request.language_id not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported programming language",
                "language_id": request.language_id,
                "allowed_languages": ALLOWED_LANGUAGES,
            }
        )

    try:

        # Execute code using local Judge0
        result = client.run(
            source_code=request.source_code,
            language=request.language_id,
            stdin=request.stdin,
        )

        return CodeExecutionResponse(
            token=getattr(result, "token", None),

            status_id=(
                getattr(
                    getattr(result, "status", None),
                    "id",
                    None
                )
            ),

            status=(
                getattr(
                    getattr(result, "status", None),
                    "description",
                    None
                )
            ),

            stdout=getattr(result, "stdout", None),
            stderr=getattr(result, "stderr", None),
            compile_output=getattr(
                result,
                "compile_output",
                None
            ),

            time=getattr(result, "time", None),
            memory=getattr(result, "memory", None),

            message=getattr(result, "message", None),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Code execution failed",
                "error": str(exc),
            }
        )