from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from agent.models import Evidence


@dataclass
class OCROutput:
    text: str
    evidence: list[Evidence]
    provider: str


class OCRProvider(ABC):
    @abstractmethod
    def extract(self, content: bytes, filename: str) -> OCROutput:
        raise NotImplementedError

