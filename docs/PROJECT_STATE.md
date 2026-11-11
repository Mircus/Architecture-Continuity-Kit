# Project continuity card

Updated: 2026-11-11  
State owner: Project maintainer

## Mission
Keep the purpose, constraints, decisions and tested boundaries visible while code evolves.

## Now
- Example project, architecture map, import-boundary checks and CI template exist.
- No production service has been integrated.

## Next
- Map your real components, files, owners, tests and dependency permissions.
- Add one important, real invariant for each component.
- Compare declarations with observed runtime traces before trusting the map.

## Open questions
- Which dependencies are hidden in tools, plugins, infrastructure or dynamic calls?
- Which rules should be enforced by dedicated architecture tests?

## Known limitations
- Static checks are not behavioral proof.
- This template does not capture model inputs, outputs, approvals, runtime traces or data flow automatically.
- The example's names and results are illustrative, not claims about any external project.
