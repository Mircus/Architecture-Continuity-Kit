# Invariants

Invariants are behavioral or structural rules that should survive refactors.
A prose invariant is a promise, not automatically an enforced property.

| ID | Rule | How checked | Gaps |
| --- | --- | --- | --- |
| ARCH-01 | `core` must not import `research` or `api` | `archcheck.py` parses Python AST imports | Does not detect dynamic imports or runtime service calls |
| ARCH-02 | Declared dependencies must not contain cycles | `archcheck.py check` | Undeclared runtime edges remain possible |
| EVID-01 | A claim without a source pointer must be marked unsupported | `tests/test_demo.py` | A source pointer is not verification of truth |

When a rule becomes critical, attach a real automated test or runtime check.
Review each gap explicitly rather than pretending a prose statement is an enforcement mechanism.
