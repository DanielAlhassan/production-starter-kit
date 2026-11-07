---
description: "Draft the data dictionary from model outputs, for the team to agree names, types, and allowed values."
agent: agent
tools: ["read", "search", "execute"]
argument-hint: "output files or folder, for example data/output"
---

Draft a data dictionary from ${input:outputs:output files or folder}.

1. Read each output file with pandas. For each column, get: file, column, data type, null count, number of distinct values, and for text columns with 50 or fewer distinct values, the list of values.
2. Search `src/` for where each column is created. Add the file and line.
3. Flag conflicts across files: same meaning with different names (for example `region` and `Region_Name`), same name with different types, and different spellings of scenario or region values.
4. Write the draft to `data/output/data_dictionary_draft.csv` with columns: file, column, proposed_name, type, unit, allowed_values, description, source, conflict. Leave `unit` and `description` empty where the code does not make them clear.
5. In chat, list the conflicts only. The team agrees on the names. A person moves the final version to `assets/`. Do not change code.
