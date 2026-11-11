# The Architecture Should Remember
## A practical guide to keeping large AI projects understandable as they grow

*Mirco A. Mannucci — HoloMathics*

We have entered a peculiar phase of software development. AI can produce code faster than many teams can explain it. Agents can refactor modules, introduce dependencies, add services, and rewrite interfaces at extraordinary speed. Yet an increasingly uncomfortable question remains:

**Does anyone still understand the system that is being built?**

This is not simply a documentation problem. A project can have excellent documentation, hundreds of tests, and impressive architectural diagrams while its actual structure slowly diverges from what its designers believe it to be.

The risk is not only *technical debt*. It is **epistemic debt**: the growing distance between what a system does, what its developers think it does, and what they can actually demonstrate.

In an earlier article I argued that large AI projects should be made more interpretable. We can now go a step further. Rather than periodically asking an AI to reconstruct an opaque architecture, **why not make architectural continuity a built-in property of the development process?**

I have put together a small starter kit to explore precisely this idea: **Architecture Continuity Kit**.

**Source code and starter kit:** https://github.com/Mircus/Architecture-Continuity-Kit

The kit is deliberately modest: a short declarative architecture map, a Python checker, an impact analyzer, a generated diagram, a decision ledger, a continuity card, an AI-review prompt, and a GitHub Actions workflow. It requires Python 3.11 or later and no third-party Python packages for its core checks.

Its ambition, however, is not modest: to help a project retain an intelligible account of its own evolution.

## 1. Five questions every large project should be able to answer

Imagine joining a project after six months of intense AI-assisted development. You may have thousands of files, multiple agents, sophisticated pipelines, and hundreds of apparently successful tests. Where do you begin?

I would start with five questions:

**1. What exists?** Which components are actually present, what are their responsibilities, and who owns them?

**2. What is allowed?** Which dependencies and architectural boundaries are permitted? Which properties must survive every refactor?

**3. Why is it this way?** What decisions created the current structure, what alternatives were rejected, and under which assumptions?

**4. What could this change affect?** If I modify one component, what other components may depend on it?

**5. What do we really know?** Which claims are verified by code, tests or traces, which are plausible inferences, and which describe intentions not yet implemented?

A useful architecture system should answer these questions without requiring an archaeologist—or a very expensive AI agent—to rediscover everything from scratch.

## 2. Put the architecture in a small, reviewable file

The starter kit begins with `architecture.toml`. Here is a simplified example:

```toml
[[components]]
id = "research"
path = "demo/research"
package = "demo.research"
purpose = "Research logic built on domain primitives."
owner = "Research team"
dependencies = ["core"]
evidence = ["tests/test_demo.py"]
```

That is all. A component has an identity, a location, a purpose, an owner, permitted dependencies, and pointers to supporting evidence.

Notice what the file does **not** pretend to describe. It does not claim to reproduce every call graph, every runtime data flow, or the semantics of every function. It is a *compact architectural contract*—a small number of statements that people can inspect and challenge.

The companion checker can verify that declared directories and evidence files exist, that the declared dependency graph contains no cycles, and that certain forbidden static Python imports do not appear. It can also generate a Mermaid diagram from the same declarations.

That last point matters: we are not maintaining a diagram separately from the architecture file. The diagram is an output of a version-controlled model.

## 3. Try it in fifteen minutes

Download the starter kit, unzip it, and open a terminal inside the `architecture-continuity-kit` folder. With Python 3.11 or newer installed, run:

```bash
python scripts/archcheck.py check
python scripts/archcheck.py report
python -m unittest discover -s tests -v
```

The first command checks the declared component map and selected static import boundaries. The second regenerates `docs/ARCHITECTURE.generated.md`, including a Mermaid dependency diagram. The third runs the included example tests.

You can then ask an important question: *If the Core module changes, who should be alerted?*

```bash
python scripts/archcheck.py impact demo/core/domain.py
```

In the example project, `core` is directly changed; `research` and `api` are potentially affected because they depend on Core, directly or through other declared dependencies.

This is not an oracle predicting software failures. It is a conservative **review map**: a prompt to inspect the relevant interfaces and tests before accepting a change.

In a Git repository, once a base branch is available locally, the same analyzer can inspect a branch diff:

```bash
python scripts/archcheck.py impact --base origin/main
```

If your repository does not have `origin/main` yet, use an appropriate existing base reference or pass changed file paths directly.

## 4. From a diagram to a discipline of change

The deeper value does not lie in the commands. It lies in the habits surrounding them.

Suppose an AI coding agent proposes to move authorization logic from a shared Core module into a feature-specific service. The tests still pass. The application still runs. Is the change safe?

Not necessarily. The agent may have altered an important responsibility boundary without changing any user-visible behavior *yet*.

The development workflow should ask:

**Before implementation:** What exactly is changing? Which component is responsible? Which invariants must remain true?

**During implementation:** Are new dependencies being introduced? Are existing boundaries being crossed? Is the change still consistent with the agreed architecture?

**Before merging:** What does the impact map identify? Which tests passed? Which claims remain unverified? Does the architectural decision need to be recorded?

**After merging:** Can another developer or AI agent reconstruct the new state without reading the entire conversation that led to it?

The kit supports this with four small artifacts: `docs/INVARIANTS.md` for protected properties, `docs/decisions/` for architecture decision records, `.github/pull_request_template.md` for structured review, and `docs/PROJECT_STATE.md` for a concise handoff.

The objective is **not more paperwork**. Routine changes should remain routine. But consequential changes should preserve the reasoning that makes them intelligible.

## 5. Make the AI reviewer distinguish knowledge from conjecture

Here is perhaps the most important practical lesson.

AI coding assistants are very good at explaining what a system *could* be doing. They are sometimes much less reliable at distinguishing that plausible story from evidence about what the repository and runtime actually do.

The kit therefore includes `prompts/ARCHITECT_REVIEW.md`, which asks an AI reviewer to classify architectural claims:

- **VERIFIED:** supported by a specific inspected file, test result or runtime trace, with its limits stated.
- **INFERRED:** plausible based on available evidence, but not directly established.
- **INTENDED:** written in specifications or design notes, but not demonstrated as implemented.

A fourth answer must always remain possible: **UNKNOWN**. The correct response to missing evidence is not an invented explanation.

Consider these two sentences:

“Research never calls Core directly.”

“The declared dependency map permits Research to import Core; the static checker found no unauthorized imports in the files it inspected. Runtime service calls have not been examined.”

The second is less elegant but far more valuable. It says precisely what has—and has not—been established.

In complex AI development, that distinction is a foundation of trust.

## 6. Let continuous integration enforce the small things

The starter includes a GitHub Actions workflow that runs on pull requests and pushes to `main`. It checks the architectural declarations, executes unit tests, regenerates the architecture report, and fails if the committed report is stale.

This does not automatically make the checks mandatory for merging. A repository maintainer must configure the appropriate GitHub branch protection or ruleset and require the workflow's check.

Once that is done, a mundane but important class of architectural mistakes can no longer slip through unnoticed: at least those that the declared rules and implemented checker can actually detect.

That qualification is essential. **A green check is evidence about the checks that ran, not proof that the entire system is correct.**

## 7. The tools to add as complexity grows

The starter kit is intentionally dependency-light. It should be easy to open, understand, and adapt. For larger systems, however, one should not reinvent mature tools.

For Python dependency rules, **Import Linter** can enforce richer module contracts. For JavaScript and TypeScript, **dependency-cruiser** offers configurable dependency validation and visualization. For multi-level architecture views, **Structurizr DSL** allows a single text model to generate C4-style diagrams.

And for agentic systems, static architecture is only half the story. Agents execute tools, call models, reach external services, and sometimes change the world. Here **OpenTelemetry**, its evolving generative-AI semantic conventions, **OpenInference**, and a self-hosted trace viewer such as **Arize Phoenix** can help reconstruct actual execution paths.

The architecture file tells us what the system is *supposed* to permit. A runtime trace can tell us which path a particular execution *actually followed*. The most interesting discrepancies lie between the two.

Instrumentation must, of course, be designed with privacy in mind: prompts, user data, credentials, tool arguments, and model outputs should not be indiscriminately captured or sent to external services.

## 8. A realistic adoption plan

One common failure of architectural governance is attempting to describe everything on day one. A better approach is incremental.

**Day 1 — Map the major components.** Start with perhaps five to ten meaningful units. For each, record purpose, owner, and permitted dependencies. Generate the diagram. Identify obvious mismatches between the model and the code.

**Week 1 — Protect three critical boundaries.** Choose the dependencies that would do the most damage if violated: for example, Core must not depend on a feature module; an agent must not bypass the approval gateway; a domain module must not write directly to another domain's persistent store. Encode the checks that can be automated, and mark the rest as unenforced.

**Weeks 2–4 — Add change review and evidence.** Use the impact command on pull requests. Record significant decisions. Attach relevant tests and traces. Require the AI reviewer to distinguish VERIFIED, INFERRED, INTENDED and UNKNOWN. Establish a short handoff format.

**Month 2 — Compare declaration with observation.** Add selected runtime traces for the most consequential workflows. Identify undeclared service calls, tool pathways, and ownership ambiguities. Do not instrument everything indiscriminately; choose a few end-to-end paths that matter.

**Month 3 — Add drift detection.** Investigate discrepancies between declared and observed dependencies. Make the comparison visible in code review. Measure how often unexplained architectural changes reach production and how quickly a new contributor can reconstruct a component's role.

A small project might stop after Week 1. That is perfectly reasonable. The purpose is to preserve understanding, not create an architecture bureaucracy.

## 9. Where I would take the project next

The starter kit is Version 0.1 in spirit: useful for a demonstration, deliberately limited for production architecture analysis. I see six natural extensions.

**First: a richer contract layer.** Move beyond imports to declare capabilities, ownership, data boundaries, and agent permissions. An architectural component should specify not only whom it can call, but also what kinds of actions it is allowed to perform.

**Second: runtime reconciliation.** Compare the declared component graph with observed traces. Highlight observed-but-undeclared edges, declared-but-never-observed edges (which require careful interpretation), and suspicious cross-boundary behavior.

**Third: evidence-linked architectural claims.** Instead of attaching only file paths, record the specific test, trace, commit or review that supports a claim, when it was last checked, and what remains outside its scope.

**Fourth: historical understanding.** Treat architecture as an evolving object. We should be able to ask: *When did this dependency first appear? What decision justified it? Which assumptions were later overturned?*

**Fifth: AI-assisted recovery and repair.** When a violation occurs, do not stop at a red warning. Ask an AI assistant to propose a minimal repair, identify what evidence would validate it, and explain the trade-offs—without authorizing it to merge consequential changes on its own.

**Sixth: a compact architectural health report.** Not a decorative dashboard with a mysterious “architecture score,” but a grounded summary: unchecked invariants, unresolved dependency violations, stale decisions, components with no clear owner, and important architectural claims lacking evidence.

I would resist the temptation to implement all six immediately. The right first experiment is a real repository, a real architectural boundary, and a real pull request whose consequences become easier to understand because the kit is present.

## 10. The larger principle: architectural continuity

There is a deeper issue beneath these engineering practices.

Traditionally, software architecture is treated as a design artifact: something we produce before the system, occasionally update, and perhaps reconstruct when it becomes unmanageable.

But in AI-accelerated development, the architecture is being modified continuously, sometimes by agents that have substantial local context but limited knowledge of the project's history. Under these conditions, understanding cannot depend on a single architect, a single conversation, or a single AI model's ability to generate a persuasive explanation.

It must become a **shared, inspectable, evidence-bearing property of the project itself**.

This leads to a principle I would like to see adopted more widely:

> **Every consequential change should leave behind enough evidence for another human—or another AI agent—to recover what changed, why it changed, what might be affected, and which assumptions remain unverified.**

This is not the same as exhaustive documentation. It is a form of intellectual continuity: preserving the chain between intention, implementation, observation, and responsibility.

The aim is not to prevent AI from accelerating software development. It is to ensure that **our understanding accelerates with it**.

If this idea interests you, the **Architecture Continuity Kit** is intended as a small, practical starting point. I would welcome experiments, counterexamples, and suggestions—especially from teams working with multi-agent systems, rapidly evolving platforms, and large AI-generated codebases.

*Because the best AI-assisted project is not necessarily the one that produces the most code. It is the one whose architecture remains intelligible, challengeable, and under human control.*

---

### Further resources

- GitHub CLI, repository publication: https://cli.github.com/manual/gh_repo_create
- GitHub required status checks: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- Structurizr DSL: https://docs.structurizr.com/dsl
- Import Linter: https://import-linter.readthedocs.io/
- dependency-cruiser: https://github.com/sverweij/dependency-cruiser
- OpenTelemetry GenAI conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Arize Phoenix: https://github.com/Arize-ai/phoenix
