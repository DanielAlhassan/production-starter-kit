---
description: "Review a module (yours or a teammate's) before it feeds the DCF engine."
agent: model-reviewer
argument-hint: "module folder, for example src/deposits"
---

Review the module in ${input:module:module folder}.

1. Find its entry point and its output files.
2. Check its outputs against `data_dictionary.xlsx` and against what the downstream module reads (search for usages of its output columns).
3. Run its tests. If `recon/recon_config.xlsx` has a pair for this module, run the reconciliation.
4. Give the review in the standard table format. End with the three changes that matter most before integration.
