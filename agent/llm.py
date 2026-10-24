from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    provider: str = "disabled"
    model: str = ""
    api_key: str = ""

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "disabled"),
            model=os.getenv("LLM_MODEL", ""),
            api_key=os.getenv("LLM_API_KEY", ""),
        )

    def validate(self) -> None:
        if self.provider != "disabled" and not self.api_key:
            raise RuntimeError("LLM provider is enabled but LLM_API_KEY is missing")


class OptionalLLMService:
    """Configuration boundary for a future LLM provider.

    The tested MVP deliberately uses the bounded RuleBasedPlanner. Enabling an LLM
    without an implemented adapter fails explicitly rather than silently falling back.
    """

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig.from_env()
        self.config.validate()

    def available(self) -> bool:
        return self.config.provider == "disabled"

    def plan(self, _query: str) -> None:
        if self.config.provider == "disabled":
            return None
        raise NotImplementedError(
            f"LLM provider '{self.config.provider}' is configured but its adapter is not implemented"
        )

