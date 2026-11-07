---
description: "Run the model, compare outputs with the baseline, and summarize what moved."
agent: agent
tools: ["read", "search", "execute"]
---

Use the model-reconciliation skill.

1. Run the model: `python -m assembly.driver` for a package, or the repo's way of calling `run()` in `src/run.py`.
2. Run the comparison with `settings/recon.yaml`.
3. Reply with a short table: output, PASS or FAIL, breaches, largest difference.
4. For each FAIL, name the most likely cause in the recent changes (`git diff`) in one sentence. Do not change code, settings, tolerances, or baselines.
