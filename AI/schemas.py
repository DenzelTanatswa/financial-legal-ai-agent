from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    severity: str = Field(description="HIGH | MEDIUM | LOW")
    description: str
    clause: Optional[str] = None


class ReasoningStep(BaseModel):
    step: int
    action: str
    observation: str


class ValidationCheck(BaseModel):
    check_name: str
    passed: bool
    detail: str


class ValidationReport(BaseModel):
    passed: bool
    overall_score: float = Field(ge=0.0, le=1.0)
    checks: List[ValidationCheck] = Field(default_factory=list)


class BaseAgentResponse(BaseModel):
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


class FinancialAgentResponse(BaseAgentResponse):
    agent_name: str = "Financial Analyst"
    key_figures: List[str] = Field(default_factory=list)
    total_amount: Optional[str] = None
    period_covered: Optional[str] = None


class LegalAgentResponse(BaseAgentResponse):
    agent_name: str = "Contract Reviewer"
    parties_involved: List[str] = Field(default_factory=list)
    governing_law: Optional[str] = None
    effective_date: Optional[str] = None
    termination_clauses: List[str] = Field(default_factory=list)


class InvoiceAgentResponse(BaseAgentResponse):
    agent_name: str = "Invoice Analyzer"
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    amount_due: Optional[str] = None
    due_date: Optional[str] = None


class TaxAgentResponse(BaseAgentResponse):
    agent_name: str = "Tax Assistant"
    tax_year: Optional[str] = None
    total_income: Optional[str] = None
    total_deductions: Optional[str] = None
    tax_liability: Optional[str] = None


class ComplianceAgentResponse(BaseAgentResponse):
    agent_name: str = "Compliance Officer"
    compliance_status: str = "UNKNOWN"
    violated_regulations: List[str] = Field(default_factory=list)
    required_actions: List[str] = Field(default_factory=list)


class CollaborationResult(BaseModel):
    primary_agent: str
    collaborating_agents: List[str] = Field(default_factory=list)
    merged_summary: str
    merged_risks: List[RiskItem] = Field(default_factory=list)
    merged_recommendations: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    agent_responses: List[BaseAgentResponse] = Field(default_factory=list)
    validation_report: Optional[ValidationReport] = None
