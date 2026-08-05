"""User-scoped document, analysis, and conversation persistence."""
from datetime import datetime
from core.database import AgentRun, Analysis, AuditLog, ChatMessage, ChatSession, Document, SessionLocal, init_database


def create_document(user_id, filename, file_type, document_type, confidence, extracted_text=""):
    init_database()
    with SessionLocal() as db:
        item = Document(user_id=user_id, filename=filename, file_type=file_type, document_type=document_type, processing_status="processing", classification_confidence=confidence, extracted_text=extracted_text)
        db.add(item); db.flush(); db.add(AuditLog(user_id=user_id, event="document_created", metadata_json={"document_id": item.id})); db.commit(); return item.id


def save_analysis(user_id, document_id, result, processing_seconds):
    with SessionLocal() as db:
        doc = db.query(Document).filter_by(id=document_id, user_id=user_id).first()
        if not doc: raise PermissionError("Document does not belong to this user.")
        doc.processing_status = "completed" if result.get("validation_passed", False) else "validation_failed"
        analysis = Analysis(document_id=document_id, result_json=result, processing_seconds=processing_seconds, status=doc.processing_status)
        db.add(analysis); db.flush()
        for run in result.get("agent_runs", []):
            db.add(AgentRun(analysis_id=analysis.id, agent_name=run.get("agent", "unknown"), status=run.get("status", "completed"), execution_seconds=run.get("execution_seconds")))
        db.add(AuditLog(user_id=user_id, event="analysis_saved", metadata_json={"document_id": document_id})); db.commit(); return analysis.id


def get_user_documents(user_id):
    init_database()
    with SessionLocal() as db:
        return [{"id": d.id, "filename": d.filename, "document_type": d.document_type, "status": d.processing_status, "uploaded_at": d.uploaded_at} for d in db.query(Document).filter_by(user_id=user_id).order_by(Document.uploaded_at.desc()).all()]


def get_document_analysis(user_id, document_id):
    with SessionLocal() as db:
        doc = db.query(Document).filter_by(id=document_id, user_id=user_id).first()
        if not doc: raise PermissionError("Document does not belong to this user.")
        analysis = db.query(Analysis).filter_by(document_id=document_id).order_by(Analysis.created_at.desc()).first()
        return analysis.result_json if analysis else None


def get_document_text(user_id, document_id):
    with SessionLocal() as db:
        doc = db.query(Document).filter_by(id=document_id, user_id=user_id).first()
        if not doc: raise PermissionError("Document does not belong to this user.")
        return {"text": doc.extracted_text or "", "document_type": doc.document_type, "filename": doc.filename}


def get_user_analytics(user_id):
    with SessionLocal() as db:
        documents = db.query(Document).filter_by(user_id=user_id).all()
        analyses = db.query(Analysis).join(Document).filter(Document.user_id == user_id).all()
        by_type = {}
        for document in documents: by_type[document.document_type] = by_type.get(document.document_type, 0) + 1
        successful = sum(analysis.status == "completed" for analysis in analyses)
        durations = [analysis.processing_seconds for analysis in analyses if analysis.processing_seconds is not None]
        agents = {}
        for analysis in analyses:
            for run in analysis.agent_runs:
                agents[run.agent_name] = agents.get(run.agent_name, 0) + 1
        return {"total_documents": len(documents), "total_analyses": len(analyses), "documents_by_type": by_type, "successful_analyses": successful, "failed_analyses": len(analyses) - successful, "average_processing_time": round(sum(durations) / len(durations), 2) if durations else 0, "most_used_agent": max(agents, key=agents.get) if agents else "—"}


def delete_document(user_id, document_id):
    with SessionLocal() as db:
        item = db.query(Document).filter_by(id=document_id, user_id=user_id).first()
        if not item: raise PermissionError("Document does not belong to this user.")
        db.delete(item); db.add(AuditLog(user_id=user_id, event="document_deleted", metadata_json={"document_id": document_id})); db.commit()


def get_or_create_session(user_id, document_id):
    with SessionLocal() as db:
        session = db.query(ChatSession).filter_by(user_id=user_id, document_id=document_id).first()
        if not session: session = ChatSession(user_id=user_id, document_id=document_id); db.add(session); db.flush(); db.commit()
        return session.id


def add_message(user_id, document_id, role, content):
    with SessionLocal() as db:
        session = db.query(ChatSession).filter_by(user_id=user_id, document_id=document_id).first()
        if not session: session = ChatSession(user_id=user_id, document_id=document_id); db.add(session); db.flush()
        db.add(ChatMessage(session_id=session.id, role=role, content=content)); db.commit()


def get_history(user_id, document_id, limit=12):
    with SessionLocal() as db:
        session = db.query(ChatSession).filter_by(user_id=user_id, document_id=document_id).first()
        if not session: return []
        return [{"role": m.role, "content": m.content} for m in session.messages[-limit:]]
