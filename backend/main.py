import re
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from schemas import (
    AnalyzeTicketRequest,
    AnalyzeTicketResponse,
)

from fastapi.middleware.cors import CORSMiddleware
from ai_engine import analyze_with_ai
from language_utils import detect_and_normalize


app = FastAPI(title="bKash Ticket Analyzer API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# Safety Filter
# =====================================================

FORBIDDEN_PATTERNS = [
    r"\bpin\b",
    r"\botp\b",
    r"\bpassword\b",
    r"\bcard\s*number\b",
]

PROMISE_PATTERNS = [
    r"we will refund you",
    r"your money will be returned",
]


def safety_check(customer_reply: str) -> str:
    """
    Redacts unsafe customer-facing content before sending
    the response back to the customer.
    """

    sanitized = customer_reply

    # Redact sensitive credential requests
    for pattern in FORBIDDEN_PATTERNS:
        sanitized = re.sub(
            pattern,
            "[REDACTED]",
            sanitized,
            flags=re.IGNORECASE,
        )

    # Remove refund guarantees
    for pattern in PROMISE_PATTERNS:
        sanitized = re.sub(
            pattern,
            "we will review your request",
            sanitized,
            flags=re.IGNORECASE,
        )

    return sanitized


# =====================================================
# Exception Handlers
# =====================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Missing or invalid required fields.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc)
        },
    )


# =====================================================
# Health Endpoint
# =====================================================

@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


# =====================================================
# Analyze Ticket Endpoint
# =====================================================

@app.post(
    "/analyze-ticket",
    response_model=AnalyzeTicketResponse,
)
async def analyze_ticket(ticket: AnalyzeTicketRequest):

    try:

        # Convert request to dictionary
        ticket_data = ticket.model_dump()

        # Detect and normalize language
        language_info = detect_and_normalize(
            complaint=ticket_data["complaint"],
            declared_language=ticket_data["language"],
        )

        # Merge language information
        ticket_data.update(language_info)

        # AI Investigation
        result: Dict = await analyze_with_ai(ticket_data)

        # Final safety filter
        if "customer_reply" in result:
            result["customer_reply"] = safety_check(
                result["customer_reply"]
            )

        # Validate response
        return AnalyzeTicketResponse(**result)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e)
            },
        )


# =====================================================
# Local Development
# =====================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )