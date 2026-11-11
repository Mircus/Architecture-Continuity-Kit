# ADR 0001: Keep the declared architecture beside the code

Status: Accepted for this example
Date: 2026-11-11

## Context
As code and agents multiply, diagrams and human memory become stale.

## Decision
Keep a minimal authoritative component registry in `architecture.toml`.
Generate a human-readable map from it; test static boundaries in CI.
Keep the record in the same pull request as code that changes a component contract.

## Alternatives considered
- Hand-drawn diagrams only: easy initially, difficult to validate.
- A large centralized architecture platform: potentially useful later, excessive for a starter.

## Consequences
We gain reproducible maps and limited automatic drift detection.
We must still compare the declared map with runtime behavior and human design intent.
