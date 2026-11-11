from demo.research.pipeline import collect_claim


def summarize(statement: str) -> dict[str, str]:
    item = collect_claim(statement)
    return {"statement": item.statement, "evidence_status": item.evidence_status}
