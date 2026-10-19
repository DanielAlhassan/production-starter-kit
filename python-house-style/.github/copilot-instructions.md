# Python style (always on)

- No helper function unless the logic is used in 2+ places. Never wrap a single library call (e.g. `pd.read_excel`) in its own function.
- Split a function only into named business steps, never utility pieces. Search for an existing function before writing a new one.
- Names: verb + domain noun. Verbs: get, read, write, compute, project, discount, check, map, build, prepare, process, sanitize, standardize, rename.
- Never use, in any form, in code or comments: validate, resolve, normalize, ensure, handle. Avoid `load` (use read/get).
- Leading underscore only for rare internal plumbing.
- Type hints on every function. Short docstrings on public functions only; none on helpers.
- Before finishing, run `python tools/check_style.py <changed files>` and fix what it flags.
- Full rules and examples: `.github/skills/python-house-style/SKILL.md`
