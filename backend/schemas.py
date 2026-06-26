from enum import Enum
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


# -----------------------------
# Request Models
# -----------------------------

class Transaction(BaseModel):
    transaction_id: str
    timestamp: str
    type: str
    amount: float
    counterparty: str
    status: str


class AnalyzeTicketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: str
    complaint: str
    language: Literal["en", "bn", "banglish"]
    channel: str
    user_type: str
    campaign_context: str
    transaction_history: List[Transaction]


# -----------------------------
# Response Enums
# -----------------------------

class CaseType(str, Enum):
    wrong_transfer = "wrong_transfer"
    payment_failed = "payment_failed"
    refund_request = "refund_request"
    duplicate_payment = "duplicate_payment"
    merchant_settlement_delay = "merchant_settlement_delay"
    agent_cash_in_issue = "agent_cash_in_issue"
    phishing_or_social_engineering = "phishing_or_social_engineering"
    other = "other"


class Department(str, Enum):
    customer_support = "customer_support"
    dispute_resolution = "dispute_resolution"
    payments_ops = "payments_ops"
    merchant_operations = "merchant_operations"
    agent_operations = "agent_operations"
    fraud_risk = "fraud_risk"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class EvidenceVerdict(str, Enum):
    consistent = "consistent"
    inconsistent = "inconsistent"
    insufficient_data = "insufficient_data"


# -----------------------------
# Response Model
# -----------------------------

class AnalyzeTicketResponse(BaseModel):
    ticket_id: str

    case_type: CaseType
    department: Department
    severity: Severity
    evidence_verdict: EvidenceVerdict

    relevant_transaction_id: Optional[str] = None

    agent_summary: str
    recommended_next_action: str
    customer_reply: str

    human_review_required: bool

    confidence: float = Field(ge=0.0, le=1.0)

    reason_codes: List[str]