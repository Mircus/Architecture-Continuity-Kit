from demo.core.domain import Claim


def collect_claim(statement: str, evidence_uri: str | None = None) -> Claim:
    # A linked source is NOT proof of the truth of the statement; the status
    # indicates a present citation pointer, not scientific verification.
    return Claim(statement=statement, evidence_uri=evidence_uri)
