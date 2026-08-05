"""
Canonical Pydantic models for the Financial & Legal AI Agent Platform.

All agent response schemas, validation models, and shared data structures
are defined here.  Every other module should import from this file —
never define the same model in two places.
"""
from __future__ import annotations

from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict, Union

from pydantic import BaseModel, Field


# ── LangGraph State ──────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """Typed state dictionary passed through every LangGraph node."""

    # Input
    question: str
    context: str
    document_type: str
    extracted_text: str

    # Routing
    selected_agent: str
    required_agents: List[str]
    collaborating_agents: List[str]

    # Outputs
    response: str
    structured_response: Optional[Dict[str, Any]]
    confidence_score: float
    confidence_rationale: str

    # Collaboration
    agent_responses: List[Dict[str, Any]]

    # Validation
    validation_passed: bool
    validation_report: Optional[Dict[str, Any]]

    # Explainability
    reasoning_steps: List[Dict[str, Any]]
    retry_count: int
    validation_error: Optional[str]


# ── Shared sub-models ────────────────────────────────────────────────────────

class RiskItem(BaseModel):
    """A single identified risk with severity and optional clause reference."""

    severity: str = Field(description="HIGH | MEDIUM | LOW")
    description: str
    clause: Optional[str] = None


class ReasoningStep(BaseModel):
    """One step in the agent's chain-of-thought."""

    step: int
    action: str
    observation: str


class ValidationCheck(BaseModel):
    """Result of a single validation criterion."""

    check_name: str
    passed: bool
    detail: str


class ValidationReport(BaseModel):
    """Aggregated validation result for an agent response."""

    passed: bool
    overall_score: float = Field(ge=0.0, le=1.0)
    checks: List[ValidationCheck] = Field(default_factory=list)


ConfidenceLabel = Literal["High Confidence", "Medium Confidence", "Low Confidence"]


def confidence_label(score: float) -> ConfidenceLabel:
    """Map a heuristic system score to a user-facing confidence label."""
    if score >= 0.75:
        return "High Confidence"
    if score >= 0.45:
        return "Medium Confidence"
    return "Low Confidence"


class SystemConfidence(BaseModel):
    """A heuristic AI/system confidence indicator, not a calibrated probability."""

    confidence: float = Field(ge=0.0, le=1.0)
    label: ConfidenceLabel
    rationale: str = ""
    disclaimer: str = (
        "This is an AI/system confidence score based on available signals; "
        "it is not a calibrated probability of correctness."
    )

    @classmethod
    def from_score(cls, score: float, rationale: str = "") -> "SystemConfidence":
        bounded_score = max(0.0, min(1.0, score))
        return cls(
            confidence=round(bounded_score, 4),
            label=confidence_label(bounded_score),
            rationale=rationale,
        )


# ── Base agent response ──────────────────────────────────────────────────────

class BaseAgentResponse(BaseModel):
    """Common fields shared by every specialist agent response."""

    agent_name: str
    document_type: str
    summary: str
    key_findings: List[str] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_rationale: str
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)
    validation_passed: bool = True
    validation_notes: Optional[str] = None


class StructuredAnalysis(BaseModel):
    """Shared export contract for all structured analysis outputs.

    `model_dump(mode="json")` produces only JSON-native values, so the same
    object can be returned by an API, persisted as JSON, sent to Power BI, or
    passed as context to a PDF renderer without parsing display text.
    """

    def to_api_payload(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    def to_database_record(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    def to_power_bi_row(self) -> Dict[str, Any]:
        """Return a JSON-native row suitable for a Power BI push dataset."""
        return self.model_dump(mode="json")

    def to_pdf_context(self) -> Dict[str, Any]:
        """Return named fields for a PDF template; no markdown parsing needed."""
        return self.model_dump(mode="json")


# ── Financial structured output ─────────────────────────────────────────────

class CashFlowItem(BaseModel):
    label: str = Field(description="e.g. 'Operating', 'Investing', 'Financing'")
    amount: float
    currency: str = "USD"


class FinancialAnalysis(StructuredAnalysis):
    """Fully structured output for the Financial Analyst agent."""

    agent_name: str = Field(default="Financial Analyst")
    document_type: str = Field(default="Bank Statement")
    summary: str = Field(description="Executive summary of the financial document")
    period_covered: Optional[str] = Field(None, description="Reporting period, e.g. 'Jan–Dec 2024'")
    currency: str = Field(default="USD")
    income: Optional[float] = Field(None, description="Total income / revenue")
    expenses: Optional[float] = Field(None, description="Total expenses / outflows")
    cashflow: Optional[float] = Field(None, description="Net cash flow (income minus expenses)")
    cashflow_breakdown: List[CashFlowItem] = Field(default_factory=list, description="Optional cash-flow categories")
    financial_highlights: List[str] = Field(default_factory=list, description="Key financial observations")
    risks: List[RiskItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence in this analysis")
    confidence_rationale: str = Field(default="")
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)


# ── Legal structured output ──────────────────────────────────────────────────

class ContractParty(BaseModel):
    name: str
    role: Optional[str] = Field(None, description="e.g. 'Employer', 'Contractor', 'Buyer'")


class ImportantClause(BaseModel):
    title: str
    summary: str
    clause_reference: Optional[str] = None


class LegalAnalysis(StructuredAnalysis):
    """Fully structured output for the Contract Reviewer agent."""

    agent_name: str = Field(default="Contract Reviewer")
    document_type: str = Field(default="Contract")
    summary: str = Field(description="High-level summary of the contract")
    parties: List[ContractParty] = Field(default_factory=list)
    governing_law: Optional[str] = Field(None, description="Jurisdiction / governing law")
    effective_date: Optional[str] = Field(None, description="Contract start date")
    termination_date: Optional[str] = Field(None, description="Contract end or expiry date")
    important_clauses: List[ImportantClause] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_rationale: str = Field(default="")
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)


# ── Invoice structured output ────────────────────────────────────────────────

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None


class InvoiceAnalysis(StructuredAnalysis):
    """Fully structured output for the Invoice Analyzer agent."""

    agent_name: str = Field(default="Invoice Analyzer")
    document_type: str = Field(default="Invoice")
    vendor: Optional[str] = Field(None, description="Vendor / supplier name")
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    currency: str = Field(default="USD")
    subtotal: Optional[float] = None
    tax: Optional[float] = Field(None, description="Total tax amount")
    tax_rate: Optional[float] = Field(None, description="Tax rate as a decimal, e.g. 0.15 for 15%")
    total: Optional[float] = None
    line_items: List[LineItem] = Field(default_factory=list)
    summary: str = Field(default="")
    risks: List[RiskItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_rationale: str = Field(default="")
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)


# ── Tax structured output ────────────────────────────────────────────────────

class TaxAnalysis(StructuredAnalysis):
    """Fully structured output for the Tax Assistant agent."""

    agent_name: str = Field(default="Tax Assistant")
    document_type: str = Field(default="Tax Document")
    summary: str = Field(default="")
    tax_year: Optional[str] = None
    currency: str = Field(default="USD")
    total_income: Optional[float] = None
    total_deductions: Optional[float] = None
    taxable_income: Optional[float] = None
    tax_liability: Optional[float] = None
    effective_tax_rate: Optional[float] = Field(None, description="Effective rate as decimal")
    financial_highlights: List[str] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_rationale: str = Field(default="")
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)


# ── Compliance structured output ─────────────────────────────────────────────

class ComplianceAnalysis(StructuredAnalysis):
    """Fully structured output for the Compliance Officer agent."""

    agent_name: str = Field(default="Compliance Officer")
    document_type: str = Field(default="Unknown")
    summary: str = Field(default="")
    compliance_status: str = Field(default="UNKNOWN", description="COMPLIANT | NON-COMPLIANT | PARTIAL | UNKNOWN")
    violated_regulations: List[str] = Field(default_factory=list)
    required_actions: List[str] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_rationale: str = Field(default="")
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)


# ── Union type for typed agent responses ─────────────────────────────────────

AgentAnalysis = Union[FinancialAnalysis, LegalAnalysis, InvoiceAnalysis, TaxAnalysis, ComplianceAnalysis]


class AnalysisResponse(BaseModel):
    """Stable, typed envelope for Streamlit, REST, storage, BI, and PDF layers."""

    document_type: str
    selected_agent: str
    analysis: AgentAnalysis
    validation: Optional[ValidationReport] = None
    collaborating_agents: List[str] = Field(default_factory=list)

    def to_api_payload(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    def to_database_record(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    def to_power_bi_row(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    def to_pdf_context(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


# ── Collaboration result ─────────────────────────────────────────────────────

class CollaborationResult(BaseModel):
    """Merged output produced by the Collaborator node after multi-agent runs."""

    primary_agent: str
    collaborating_agents: List[str] = Field(default_factory=list)
    merged_summary: str
    merged_risks: List[RiskItem] = Field(default_factory=list)
    merged_recommendations: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    agent_responses: List[Dict[str, Any]] = Field(default_factory=list)
    validation_report: Optional[ValidationReport] = None


# ── Classification result ────────────────────────────────────────────────────

class ClassificationResult(BaseModel):
    """Output of the document classifier including confidence scoring."""

    document_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_label: ConfidenceLabel
    matched_signals: List[str] = Field(default_factory=list)
    confidence_note: str = (
        "AI/system confidence score based on matching document signals; "
        "not a calibrated probability."
    )

    @classmethod
    def from_score(
        cls,
        document_type: str,
        confidence: float,
        matched_signals: List[str],
    ) -> "ClassificationResult":
        return cls(
            document_type=document_type,
            confidence=round(confidence, 4),
            confidence_label=confidence_label(confidence),
            matched_signals=matched_signals,
        )


class EntityExtractionResult(BaseModel):
    """Extracted entities plus a heuristic extraction-quality signal."""

    entities: Dict[str, List[str]] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_label: ConfidenceLabel
    matched_entity_types: List[str] = Field(default_factory=list)
    confidence_note: str = (
        "AI/system confidence score based on recognisable entity patterns and "
        "document coverage; not a calibrated probability."
    )

    @classmethod
    def from_score(
        cls, entities: Dict[str, List[str]], score: float
    ) -> "EntityExtractionResult":
        bounded_score = max(0.0, min(1.0, score))
        return cls(
            entities=entities,
            confidence=round(bounded_score, 4),
            confidence_label=confidence_label(bounded_score),
            matched_entity_types=[name for name, values in entities.items() if values],
        )
