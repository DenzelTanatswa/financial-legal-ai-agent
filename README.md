<div align="center">

# Aureon Intelligence Studio
### Financial & Legal Document AI Agent
Turn complex documents into structured insights, risk summaries, and downloadable reports.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-166534?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-2563EB?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

**Portfolio project · Local development prototype**

[Explore the Code](https://github.com/DenzelTanatswa/financial-legal-ai-agent) · [Connect on LinkedIn](https://www.linkedin.com/in/denzel-chidzikwe-0a6965288/)

</div>

---

## Overview

Aureon Intelligence Studio is a Python application for reviewing financial and legal documents through a Streamlit workspace. It combines document extraction, rule-based classification, retrieval-augmented generation (RAG), and a LangGraph workflow with specialist agents.

Users can upload a document, ask a focused question, inspect structured findings, and export a PDF report. The project demonstrates applied AI engineering across document processing, semantic retrieval, agent orchestration, typed outputs, and persistent user history.

## Features

| Capability | Implementation |
| :--- | :--- |
| Document upload | PDF, DOCX, TXT, CSV, and XLSX |
| Automatic classification | Keyword and pattern signals identify bank statements, invoices, contracts, and tax documents |
| Specialist analysis | Financial, invoice, legal, tax, and compliance agents |
| Agent collaboration | Supervisor selects specialists; their outputs are combined and validated |
| Document Q&A | Semantic retrieval supplies relevant document sections and recent conversation context |
| Structured findings | Pydantic schemas organize summaries, financial fields, risks, and recommendations |
| Entity extraction | Pattern-based detection of amounts, dates, and email addresses |
| Review transparency | Source-section references, validation results, execution details, and confidence indicators |
| User workspace | Registration, login, document history, follow-up questions, and document deletion |
| Reporting | PDF report generation and stored analysis results |
| Usage analytics | Per-user document counts, analysis outcomes, and processing-time summaries |

Available fields and findings depend on the document and selected specialists.

## How It Works

1. **Upload:** Extract text from a supported document.
2. **Classify:** Identify a document category using rule-based signals.
3. **Retrieve:** Split text into 1,000-character chunks, embed them with a sentence-transformer model, and retrieve up to four relevant chunks through FAISS.
4. **Analyze:** Route the document through the supervisor and selected specialist agents.
5. **Combine and validate:** Merge agent findings and apply validation with a retry route.
6. **Review and save:** Display findings, persist history, and generate reports.

The application uses OpenAI through LangChain for language-model analysis. Embeddings use `sentence-transformers/all-MiniLM-L6-v2`.

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| Interface | Streamlit, custom HTML/CSS |
| Agent workflow | LangGraph, LangChain, LangChain OpenAI |
| Language model | Configurable OpenAI model; default in code: `gpt-4o` |
| Retrieval | FAISS, Hugging Face sentence-transformer embeddings |
| Data processing | Pandas, PyMuPDF, python-docx |
| Validation | Pydantic |
| Persistence | SQLAlchemy, SQLite |
| Reports | ReportLab |
| API module | FastAPI router for structured analysis |
| Configuration | python-dotenv, environment variables |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/DenzelTanatswa/financial-legal-ai-agent.git
cd financial-legal-ai-agent
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

### 2. Install dependencies

The current `requirements-local.txt` contains supplemental dependencies rather than the complete application stack. Install those and the additional packages used by the application:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-local.txt
python -m pip install streamlit python-dotenv pandas PyMuPDF python-docx openpyxl Werkzeug pydantic langchain langchain-openai langchain-community langgraph sentence-transformers faiss-cpu
```

These commands are based on source inspection. Dependency versions have not been locked or verified in a clean environment.

### 3. Configure the application

Create a `.env` file in the repository root:

```dotenv
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
UPLOAD_FOLDER=Uploads
DATABASE_URL=sqlite:///Database/aureon.db
```

Use a model available to your API account that supports the application's structured-output requirements. Keep your API key out of version control.

### 4. Launch

```bash
python -m streamlit run app.py
```

Open the local address printed in the terminal, create an account, and upload a sample document. The application initializes its database tables on startup.

The embedding model may require a download on first use. Language-model analysis requires internet access and an OpenAI API key.

## Example Review Questions

- “Summarize income, expenses, and net cash flow in this bank statement.”
- “Extract the invoice subtotal, tax, total, and payment terms.”
- “Highlight termination clauses and payment obligations in this contract.”
- “List the tax-related amounts and supporting details found in this document.”

## Project Structure

| Path | Purpose |
| :--- | :--- |
| `app.py` | Streamlit workspace and application entry point |
| `Agents/` | Specialists, supervisor, collaboration, validation, and LangGraph workflow |
| `core/` | Configuration, database models, schemas, and exceptions |
| `services/` | Document extraction, analysis, authentication, persistence, logging, and reports |
| `repositories/` | Embeddings and vector-store operations |
| `ui/` | Sidebar interface |
| `api/routes.py` | Optional structured-analysis API router |
| `requirements-local.txt` | Supplemental local dependencies |

## Optional API Module

`api/routes.py` defines an `APIRouter` with `POST /api/v1/analyze`. Its request includes `text`, `document_type`, and an optional `question`.

The repository currently provides the router rather than a standalone FastAPI application entry point. Mount it in a FastAPI application before serving it with Uvicorn.

## Current Status & Limitations

- **Development prototype:** Production readiness and analysis accuracy have not been established.
- **Demo metrics:** The four headline dashboard cards use hardcoded sample values. The separate “My analytics” panel reads persisted user activity.
- **Text extraction:** Scanned image-only PDFs require OCR, which is not implemented in the current extraction service.
- **Confidence:** Displayed scores are model or heuristic signals, not calibrated probabilities of correctness.
- **Retrieval:** Source references identify text chunks rather than verified page-level citations.
- **Data handling:** Uploaded files and extracted text are stored locally; document context is sent to the configured OpenAI service for analysis. Encryption at rest is not established by this implementation.
- **Professional review:** Generated financial, tax, legal, and compliance findings require independent review before use.

## Suggested Next Steps

- Add a complete, versioned dependency manifest and reproducible setup checks.
- Replace demo dashboard cards with live metrics.
- Add OCR support and page-level source references.
- Evaluate extraction and analysis quality against labeled sample documents.
- Strengthen upload isolation, retention controls, and deployment security.
- Add anonymized screenshots and a short walkthrough.

## Author

**Denzel Chidzikwe**  
BSc Information Technology · Big Data Analytics

[GitHub](https://github.com/DenzelTanatswa) · [LinkedIn](https://www.linkedin.com/in/denzel-chidzikwe-0a6965288/)

