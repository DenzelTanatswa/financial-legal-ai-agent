FINANCIAL_PROMPT = """
You are a senior Financial Analyst. Analyze the financial document below.

Context:
{context}

Question:
{question}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "summary": "<executive summary>",
  "key_findings": ["<finding 1>", "<finding 2>"],
  "key_figures": ["<figure 1>"],
  "total_amount": "<total if applicable>",
  "period_covered": "<period if applicable>",
  "risks": [
    {{"severity": "HIGH|MEDIUM|LOW", "description": "<risk>", "clause": null}}
  ],
  "recommendations": ["<rec 1>"],
  "confidence_score": 0.0,
  "confidence_rationale": "<why this score>",
  "reasoning_steps": [
    {{"step": 1, "action": "<what you did>", "observation": "<what you found>"}}
  ]
}}
"""

LEGAL_PROMPT = """
You are a senior Legal Analyst. Review the contract document below.

Context:
{context}

Question:
{question}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "summary": "<contract summary>",
  "key_findings": ["<finding 1>"],
  "parties_involved": ["<party 1>", "<party 2>"],
  "governing_law": "<jurisdiction>",
  "effective_date": "<date or null>",
  "termination_clauses": ["<clause 1>"],
  "risks": [
    {{"severity": "HIGH|MEDIUM|LOW", "description": "<risk>", "clause": "<clause ref>"}}
  ],
  "recommendations": ["<rec 1>"],
  "confidence_score": 0.0,
  "confidence_rationale": "<why this score>",
  "reasoning_steps": [
    {{"step": 1, "action": "<what you did>", "observation": "<what you found>"}}
  ]
}}
"""

INVOICE_PROMPT = """
You are an Invoice Audit Specialist. Analyze the invoice below.

Context:
{context}

Question:
{question}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "summary": "<invoice summary>",
  "key_findings": ["<finding 1>"],
  "vendor": "<vendor name>",
  "invoice_number": "<number>",
  "amount_due": "<amount>",
  "due_date": "<date>",
  "risks": [
    {{"severity": "HIGH|MEDIUM|LOW", "description": "<risk>", "clause": null}}
  ],
  "recommendations": ["<rec 1>"],
  "confidence_score": 0.0,
  "confidence_rationale": "<why this score>",
  "reasoning_steps": [
    {{"step": 1, "action": "<what you did>", "observation": "<what you found>"}}
  ]
}}
"""

TAX_PROMPT = """
You are a Tax Compliance Expert. Analyze the tax document below.

Context:
{context}

Question:
{question}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "summary": "<tax document summary>",
  "key_findings": ["<finding 1>"],
  "tax_year": "<year>",
  "total_income": "<amount>",
  "total_deductions": "<amount>",
  "tax_liability": "<amount>",
  "risks": [
    {{"severity": "HIGH|MEDIUM|LOW", "description": "<risk>", "clause": null}}
  ],
  "recommendations": ["<rec 1>"],
  "confidence_score": 0.0,
  "confidence_rationale": "<why this score>",
  "reasoning_steps": [
    {{"step": 1, "action": "<what you did>", "observation": "<what you found>"}}
  ]
}}
"""

COMPLIANCE_PROMPT = """
You are a Compliance Officer. Assess the document for regulatory compliance.

Context:
{context}

Question:
{question}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "summary": "<compliance summary>",
  "key_findings": ["<finding 1>"],
  "compliance_status": "COMPLIANT|NON-COMPLIANT|PARTIAL|UNKNOWN",
  "violated_regulations": ["<regulation 1>"],
  "required_actions": ["<action 1>"],
  "risks": [
    {{"severity": "HIGH|MEDIUM|LOW", "description": "<risk>", "clause": "<ref>"}}
  ],
  "recommendations": ["<rec 1>"],
  "confidence_score": 0.0,
  "confidence_rationale": "<why this score>",
  "reasoning_steps": [
    {{"step": 1, "action": "<what you did>", "observation": "<what you found>"}}
  ]
}}
"""

VALIDATOR_PROMPT = """
You are a Response Quality Validator. Review the agent's analysis below.

Document Type: {document_type}
Agent Response:
{response}

Check for:
1. completeness — are all required fields present and non-empty?
2. consistency — do the risks match the summary?
3. confidence_calibration — is the confidence score justified?
4. hallucination_risk — are claims grounded in the context?

Respond ONLY with a valid JSON object:
{{
  "passed": true,
  "overall_score": 0.0,
  "checks": [
    {{"check_name": "completeness", "passed": true, "detail": "<detail>"}},
    {{"check_name": "consistency", "passed": true, "detail": "<detail>"}},
    {{"check_name": "confidence_calibration", "passed": true, "detail": "<detail>"}},
    {{"check_name": "hallucination_risk", "passed": true, "detail": "<detail>"}}
  ]
}}
"""
