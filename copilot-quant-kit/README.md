# Copilot quant kit

A GitHub Copilot setup for quantitative model work in VS Code: guardrail hooks, model reconciliation, documentation, stakeholder updates, and review. Copy the `.github` folder into a model repo.

The kit assumes this model layout:

```
data/input/            source data (read only)
data/output/           model outputs
data/output/baseline/  approved outputs for reconciliation (read only)
data/output/recon/     reconciliation reports
assets/                stable methodology files (read only)
settings/              YAML: run values, toggles, enabled models, recon.yaml
src/run.py             one callable run(); src/<model>/run.py in a package
assembly/driver.py     package entry point
assembly/switchboard.py  dispatches the enabled models
```

Opus is the same model in Copilot and in Claude Code. The difference is the harness: the files that give the model context, procedures, tools, and checks. This kit is the harness.

| Layer | What it does | Credit cost |
|---|---|---|
| Instructions | Rules sent with every request | Paid on every request. Keep short. |
| Skills | Procedures loaded only when the task needs them | Paid only when used |
| Agents | A role with fixed tools (and optionally a fixed model) | Same as chat |
| Prompts | Repeatable slash commands | Same as chat |
| Hooks | Scripts that run at fixed points. They check, block, and log. | No model cost. The agent sees only the failures. |

## What is in the kit

```
.github/
  hooks/
    model-guardrails.json          Hook config (Copilot harness format)
    scripts/
      hook_policy.json             All hook settings: protected paths, blocked commands, checks
      guard_tool_use.py            preToolUse: blocks edits to data/input, assets, baselines, Excel, hook files; blocks push, hard reset, recursive delete, network calls; asks before pip install, commit, merge; logs every call
      check_python_edit.py         postToolUse: ruff lint, ruff format, and tools/check_style.py on each edited .py file; sends errors back to the agent
      run_stop_checks.py           agentStop: runs pytest, the driver, and output reconciliation before the agent can finish; stops after 2 failed fix attempts and reports
      hook_common.py               Shared functions for the three scripts
  instructions/
    model-structure.instructions.md   Your layout (data, assets, settings, src/run.py, assembly) and the three control types (*.py, *.yaml)
    writing.instructions.md           All prose goes through the STE skill (*.md, *.txt)
  skills/
    model-reconciliation/          compare_outputs.py and recon_template.yaml: baseline vs new outputs, value by value, with tolerances
    model-documentation/           MRM documentation template and procedure
    stakeholder-update/            3-slide deck, status email
  agents/
    model-builder.agent.md         Runs a spec from your brain dump agent, small steps, change record at the end
    model-reviewer.agent.md        Read-only validator-style review
  prompts/
    scaffold-model.prompt.md       /scaffold-model: new repo layout, or add a model to the package (src/<model>, switchboard, settings)
    review-model.prompt.md         /review-model src/deposits
    change-record.prompt.md        /change-record
copilot-instructions-additions.md  Lines to paste into your existing copilot-instructions.md
```

The kit does not replace your files. It adds to your brain dump agent, `python.instructions.md`, `tools/check_style.py`, `tools/house_style_terms.csv`, and your STE, em dash, and house style skills. The post-edit hook calls your `tools/check_style.py`, so the banned word list stays in one place.

## Install

1. Copy `.github/` into the repo root. Merge folders. Do not overwrite your own files.
2. Paste the block from `copilot-instructions-additions.md` into `.github/copilot-instructions.md`.
3. Install the tools: `pip install ruff pytest pandas openpyxl pyyaml`.
4. Add to `.gitignore`:
   ```
   .copilot-audit/
   data/output/recon/
   ```
5. Check `.github/hooks/scripts/hook_policy.json`. Change `protected_paths` to match your folders. The `*` in a pattern also matches subfolders.
6. In VS Code, open Chat, set **Session Target** to **Copilot**, then type `/hooks`. You see `model-guardrails.json`. If hooks do not show, your enterprise settings can disable them. Ask IT.
7. On Windows, if `python` does not start Python, change `python` to `py` in `model-guardrails.json`.

## Smoke test (5 minutes)

In a new Copilot chat:

1. "Add a line to assets/test.csv." The guard blocks it.
2. "Run git push." The guard blocks it.
3. "Create src/tmp_check.py with a function validate_rates that returns x*2 and an unused import." The post-edit hook removes the import, formats the file, and your style check reports `validate`.
4. Open `.copilot-audit/agent_actions.jsonl`. Each tool call is there.
5. Delete `src/tmp_check.py`.

If step 1 or 2 does not block, the tool names in your VS Code version differ. Open the Agent Debug Logs, find the tool name, and add a word from it to `edit_tool_words` or `shell_tool_words` in `hook_policy.json`.

## Reconciliation setup (once per repo)

1. Put approved outputs in `data/output/baseline/`. A person does this, not the agent. The guard protects this folder.
2. Copy `.github/skills/model-reconciliation/recon_template.yaml` to `settings/recon.yaml`. Add one entry per output, with keys and tolerances.
3. From then on, the stop hook runs `python -m assembly.driver` and then the reconciliation after every agent turn that edits Python. A numeric change cannot pass silently.
4. Single model with no `assembly/`: change the "model run" command in `hook_policy.json` to how you call `run()` from `src/run.py`. If a full run is too slow for every turn, remove that check and run the model by hand before you reconcile.

Run it by hand any time:
```
python .github/skills/model-reconciliation/scripts/compare_outputs.py settings/recon.yaml
```

## Make the STE skill run without asking

Copilot picks a skill from its `description` only. Put the trigger in the description. Replace the description in your STE skill frontmatter with:

```yaml
description: "ASD-STE100 Simplified Technical English rules, strict and STE-flavored modes. Use for ALL prose you write, even when the user does not mention STE: documentation, READMEs, docstrings, code comments, change records, specs, emails, slide text, and summaries. Strict mode for procedures, controls, and run steps. STE-flavored mode for everything else."
```

`writing.instructions.md` and the lines in `copilot-instructions-additions.md` back this up for Markdown files and for comments and docstrings.

## Daily workflow

1. New model or new model in the package: `/scaffold-model`.
2. Brain dump in Microsoft Copilot (no cap) or your brain dump agent. Get a task spec.
3. Plan agent with Opus for a hard task. Approve the plan.
4. `model-builder` agent runs the spec. Hooks check each edit and each finish.
5. Handoff button: **Review this change** opens `model-reviewer`.
6. `/change-record` for the MRM log. `stakeholder-update` skill for the 3-slide deck.

## Use credits well

| Do | Why |
|---|---|
| Keep Auto as the default. Choose Opus by hand only for planning, hard debugging, and review. | Auto sends easy steps to cheaper models. |
| Do brainstorms and brain dumps in Microsoft Copilot. Bring only the spec to GitHub Copilot. | Microsoft Copilot has no cap for you. |
| Start a new chat for each task. Use `/compact` in long chats and `/fork` for side questions. | Old history is resent with every request. |
| Keep `copilot-instructions.md` short. Move long rules into skills. | Instructions are paid on every request. Skills are paid only when used. |
| Let hooks and scripts do the checks. | A script costs no credits. The agent reads only the failure. |
| Give each agent only the tools it needs. | Fewer tools, smaller context, fewer wrong turns. |
| Add `data/`, `.copilot-audit/`, and other large folders to `search.exclude` in VS Code settings. | Search results count as context. |
| Hover a response to see its cost. Run `/chronicle:cost-tips` once a week. | Find the expensive habits. |

To pin a model on an agent, add `model: <name>` to its frontmatter. Use the exact name from the model picker. The kit does not pin models, so Auto stays in control.

## Why this matters for MRM

- The agent cannot change inputs, baselines, Excel files, or its own guardrails.
- Every agent action is logged with time, session, tool, and files.
- Every change to model code is tested and reconciled before the agent says it is done.
- Every change has a change record with its numeric impact.

## Limits

- VS Code hooks are in Preview. The event payloads can change between versions. Run the smoke test after each VS Code update.
- The scripts were tested with simulated hook events, not inside your VS Code. Run the smoke test first.
- A hook timeout lets the tool call continue with normal approvals. The guard is a safety net, not a replacement for code review.
