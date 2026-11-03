---
description: "Prepare an update for manager or team: scope from the last update, draft, deck, record."
agent: agent
tools: ["read", "search", "execute", "edit"]
argument-hint: "manager or team, and the project folders"
---

Use the progress-log skill, "prepare an update" steps, for ${input:audience:manager or team}.

1. Run the scope for that audience. Projects: the current folder, plus any I name.
2. Draft the content: done, decisions, issues, next. Facts and numbers from files only.
3. Show me the draft. Wait for my OK before you build the deck.
4. Build the 3-slide deck with the stakeholder-update and wf-deck skills.
5. Ask me if the update was given. Run `record` only after I say yes.
