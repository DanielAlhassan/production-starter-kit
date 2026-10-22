---
description: Inline needless helpers in one file without changing outputs
agent: agent
---

Flatten the helpers in ${file}.

1. Run `python tools/check_style.py` on the file's package and note every ERROR in this file.
2. Before editing, run the file's entry function on the standard test inputs and save the output.
3. Inline every helper used in only one place. Delete every function that only wraps one call. Merge duplicate functions. Rename what is left to verb + domain noun.
4. Name intermediate results so each step can be inspected in the debugger.
5. Do not change logic, column names, or outputs.
6. Run the entry function again and compare with `pd.testing.assert_frame_equal`.
7. Run the checker again and fix every ERROR.
8. Report: function count before and after, the equivalence result, and any WARN left with the reason.
