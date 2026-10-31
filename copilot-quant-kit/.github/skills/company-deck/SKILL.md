---
name: company-deck
description: "Build PowerPoint decks in the company template: brand fonts, colors, and layouts come from the template file, not from code. Use for any slide, deck, or presentation the user asks for, including stakeholder updates, model results, and demos."
---

# Company deck

The template carries the brand. The agent writes only the content, as a deck YAML file. `scripts/render_deck.py` puts the content into the template's own layouts and placeholders, so fonts, colors, positions, and chart colors always match the brand.

## Files in this skill folder

| File | What it is | Who changes it |
|---|---|---|
| `assets/<template>.pptx` | The company template, saved as .pptx | A person, once |
| `brand.yaml` | Theme colors and fonts read from the template. The single brand source. | `inspect_template.py` |
| `layout_map.yaml` | Layout keys, roles (title, body, body_2, ...), placeholder idx, text limits | `inspect_template.py`, then a person keeps the layouts in use and tunes the limits |
| `scripts/inspect_template.py` | Writes `brand.yaml` and a draft `layout_map.yaml` | |
| `scripts/render_deck.py` | Builds the deck from a deck YAML file | |
| `deck_example.yaml` | Example of the deck YAML format | |

## One-time setup (a person does this)

1. Open the company template in PowerPoint. Save As `.pptx` (python-pptx cannot open `.potx`). Put it in `assets/`.
2. Run `python scripts/inspect_template.py assets/<template>.pptx .` in this folder.
3. In `layout_map.yaml`, keep the layouts you use. Build one test deck, open it in PowerPoint, and lower `max_chars` until no text overflows.

## Steps for each deck

1. Get the content first. Every number comes from a file (reconciliation summary, model output, workflow evidence). Write the source in the slide `notes`.
2. Write the deck YAML in the project, for example `data/output/decks/<name>.yaml`. Use only layout keys and roles from `layout_map.yaml`. Follow `deck_example.yaml`.
   - Text: a string. Bullets: a list (an item can be `{text: ..., level: 1}`).
   - Table: `{table: {columns: [...], rows: [[...]]}}`.
   - Chart: `{chart: {type: column | bar | line | stacked_column, categories: [...], series: {name: [values]}, number_format: "0.0"}}`. Charts are native and editable, in the template's theme colors.
   - Image: `{image: path}`.
3. Run `python <this skill folder>/scripts/render_deck.py <deck.yaml>`.
4. If it prints `WARN`, cut the text. Do not raise the limits. Run again until it exits with 0.
5. Tell the user the deck path and ask them to look at it in PowerPoint before it goes to anyone.

## Rules

- Do not set fonts, colors, sizes, or positions in code or YAML. If the brand looks wrong, the template or `layout_map.yaml` is wrong. Tell the user.
- Do not edit the template, `brand.yaml`, or `layout_map.yaml`. Hooks block edits to this folder.
- Slide text: ASD-STE100 writing skill, STE-flavored mode. No em dashes.
- The template and the decks stay on the work machine. Do not put them in a public repo.
