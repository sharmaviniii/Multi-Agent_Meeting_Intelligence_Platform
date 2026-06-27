import json
import logging
from contextvars import ContextVar
from datetime import datetime
from uuid import uuid4

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


def new_request_id() -> str:
    request_id = str(uuid4())
    request_id_var.set(request_id)
    return request_id


class JsonLogger:
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)

    def info(self, event: str, **kwargs) -> None:
        self.logger.info(self._format(event, kwargs))

    def exception(self, event: str, **kwargs) -> None:
        self.logger.exception(self._format(event, kwargs))

    def _format(self, event: str, fields: dict) -> str:
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "info",
            "event": event,
            "request_id": request_id_var.get(),
            **fields,
        }
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
    )


def get_logger(name: str) -> JsonLogger:
    return JsonLogger(name)
