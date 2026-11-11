from dataclasses import dataclass


@dataclass(frozen=True)
class Claim:
    statement: str
    evidence_uri: str | None = None

    @property
    def evidence_status(self) -> str:
        return "source-linked" if self.evidence_uri else "unsupported"
