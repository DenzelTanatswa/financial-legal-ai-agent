"""Structured metadata logging only; never logs document content, keys, or passwords."""
import logging, json

logger = logging.getLogger("aureon")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler); logger.setLevel(logging.INFO)

def log_event(event: str, **metadata) -> None:
    safe = {k: v for k, v in metadata.items() if k not in {"text", "content", "password", "api_key", "token"}}
    logger.info(json.dumps({"event": event, **safe}, default=str))
