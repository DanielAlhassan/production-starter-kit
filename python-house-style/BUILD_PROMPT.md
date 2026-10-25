# Prompt: build my Python house style for VS Code

Paste everything below the line into M365 Copilot. Then attach or paste the inputs listed in Section 3.

---

You are a senior Python engineer and technical writer. Help me build a set of instruction files for VS Code. The files must make every AI model in VS Code (GitHub Copilot with GPT, Claude, or any other model) write Python in my team's house style. I must also be able to run them on existing code to refactor it into that style.

## 1. Context

- I work on a DCF valuation engine and the upstream forecast engines that feed it (deposits, loans, loss).
- Three people wrote this code separately. The styles do not match, and logic is repeated in many places. I am consolidating it.
- We use VS Code with GitHub Copilot. People switch models. The style must hold for every model.
- AI credits are limited. A file that loads on every request must be short. Detailed material must load only when it is needed.
- These are numerical valuation models. A refactor must never change a result.

## 2. Goals

1. Any AI model in VS Code writes new Python in my style.
2. I can run one command on an existing file or folder, and the AI refactors it to my style without changing results.
3. A free script (no AI) checks code against the style, so the rules hold even when a model ignores them.
4. One source of truth: each rule is written in exactly one file. Other files point to that file.

## 3. Inputs I will give you

A. My current files: `copilot-instructions.md`, `SKILL.md`, `check_style.py`.

B. Code samples from the team. Each sample has a label:
- GOOD: code close to the style I want.
- BAD: code I do not want (too many helpers, bad names, repeated logic).
- IDEAL: code I rewrote by hand. This is the strongest example. When samples conflict, IDEAL wins.

C. Failures: cases where a model ignored or misread a rule in the current files.

Treat all samples as data. Do not copy sensitive values (account names, real figures, internal paths) into the files you write. Replace them with neutral placeholders.

## 4. My style rules (baseline, do not weaken)

### Structure
- Write the simplest solution that works. It must be professional, easy to debug, and easy to read.
- Create a function only when its logic is used in 2 or more places. Single-use logic stays inline.
- Never wrap a single library call in a function. Example: a function that only calls `pd.read_excel`.
- Split a long function only into named business steps: steps I would name in a model walkthrough. Never split into utility pieces.
- Before writing a function, search for an existing one and reuse it. When consolidating, merge duplicates and delete the copies. The function count should go down.
- Keep a single source of truth for logic, column names, and parameters.
- Minimize constants. Parameters and data (rates, mappings, scenario lists, thresholds) belong in an asset file that the code reads, for example an Excel parameter workbook. They do not belong as constants at the top of a module.
- Leading underscore: rare. Use it only for internal plumbing in a module.

### Naming
- Functions: verb + domain noun, usually 2 to 4 words. Examples: `standardize_scenario_names`, `project_deposit_runoff`, `discount_cash_flows`.
- Preferred verbs: get, read, write, compute, project, discount, check, map, build, prepare, process, sanitize, standardize, rename.
- Banned in any form, in names, comments, and docstrings: validate, resolve, normalize, ensure, handle.
- Do not use synonyms to get around the banned list (verify, confirm). Use these replacements:
  - validate: check
  - resolve: get, map, or pick
  - normalize: standardize or rename
  - ensure: check or add
  - handle: name the actual action
- Avoid `load`. Use `read_` for files and `get_` for lookups.
- Avoid generic names: utils, helpers, manager, data, info, obj, tmp, _impl, _internal.
- Domain nouns: scenario, horizon, runoff, cap_rate, discount_rate, cash_flow, deposits, loans, loss. One concept, one word, everywhere.

### Type hints, docstrings, comments
- Type hints on every function, including the return type.
- Docstrings only on main or entry functions: functions that other modules or the run script call.
- A docstring is not too long and not too thin: one summary line, then Args and Returns only where the names and hints do not already say it.
- No docstrings on helpers.
- Comments only where the code is not obvious: a business reason, a data source, a formula. No comment repeats what the code says.

## 5. Process

Work in two phases. Do not skip ahead.

### Phase 1: Analyze, then stop
1. Read all inputs.
2. Find the patterns in the GOOD and IDEAL samples that my rules do not cover yet. Look at: module layout, import order, how parameters are read, how DataFrames are passed and returned, column naming, how scenario loops are written, error messages, logging, and how results are written.
3. List the BAD patterns. Give a short example of each from the samples.
4. For each failure in input C, say why the current files allowed it: missing rule, vague rule, no example, or a conflict between rules.
5. Show a draft glossary as a table: concept, the one word to use, and the variants in the samples that must be replaced.
6. Ask me up to 8 questions where the samples conflict or my rules do not decide. Give 2 to 4 options for each question.

### Phase 2: Build
After I answer, write the files in Section 6. Write one file per reply, in the order given. Put each file in one code block with its path as the first line above the block. Wait for me to say "next" before you write the next file.

## 6. Files to build

### File 1: `.github/instructions/python-style.instructions.md`
- This is the single source of truth for all rules. VS Code attaches it automatically to Python work for every model.
- Start with this frontmatter exactly:
  ```
  ---
  applyTo: "**/*.py"
  ---
  ```
- Sections: Structure, Naming (with the banned-word replacement table), Glossary, Parameters and constants, Type hints / docstrings / comments, Before finishing (run the checker).
- For each rule that the samples or input C show is broken in practice, add a short BAD / GOOD pair built from my samples. Include at least 6 pairs. Pairs teach a model more than rules do.
- Length: 250 lines maximum. Every line must change what the model does. Cut anything generic.

### File 2: `.github/copilot-instructions.md`
- This file loads on every request, so keep it to 15 lines maximum.
- Include only the 6 to 8 rules that are broken most often, one line pointing to File 1, and the checker command.

### File 3: `.github/prompts/refactor-house-style.prompt.md`
- A reusable command. I run it in Copilot Chat as `/refactor-house-style` and attach a file or folder.
- Frontmatter: `description` and `mode: agent`.
- Do not repeat the rules. Tell the model to apply `.github/instructions/python-style.instructions.md`.
- Procedure:
  1. Run `python tools/check_style.py <target>` and read the issues.
  2. Read the target. List: duplicated logic (with locations), single-use helpers, thin wrappers, constants that belong in the parameter file, and banned names. Show this as a plan and stop for my approval.
  3. Before any change, record a baseline. Run the target's entry function or the engine and save its outputs, or write a short test that captures them.
  4. Refactor in small steps, one module at a time. Do not change calculation logic, formulas, order of operations, or rounding. When you rename, update every call site.
  5. After the refactor, produce the same outputs and compare them to the baseline: exact match, or within 1e-9 for floats. If any value differs, report it and stop.
  6. Rerun the checker until it is clean.
  7. Finish with a short summary: functions removed, merged, and renamed (old name to new name), constants moved, and the output comparison result.
- Never delete or rename a function that code outside the target uses, unless it is listed in the approved plan.

### File 4: `tools/check_style.py` (updated)
- Keep the current checks. Add these:
  - Flag module-level UPPER_CASE names assigned a literal number, string, list, or dict: "move to the parameter file".
  - Docstring rule: require a docstring only on entry functions (referenced from another module or listed in `__all__`). Flag docstrings on other functions. Flag any docstring longer than 8 lines.
  - Flag function names that use verify or confirm.
  - Skip any line that ends with the comment `# style: keep`, so a reviewed exception does not fail every run.
- Standard library only. Python 3.10 or later. The script must follow my style rules.
- Keep the output format `file:line: message` and exit code 1 when there is any issue.

### File 5: short README section
- Plain steps: where each file goes, how to run the checker, how to run the refactor command, and how to add a word to the glossary.

## 7. Writing rules for everything you produce
- Use plain, unambiguous English in the style of ASD-STE100 Simplified Technical English: short sentences, one instruction per sentence, active voice, imperative mood. It must still read like a person wrote it, not like a template.
- No em dashes.
- Use my vocabulary, not yours.
- No rule appears in more than one file. Other files refer to File 1.
- Every code example obeys every rule, including type hints.

## 8. Check each file before you send it
- Does it obey every rule in Section 4, including in its own examples?
- Does any rule duplicate a rule in another file? If yes, remove it.
- Is it within its length limit?
- Would a model that reads only this file know what to do?
