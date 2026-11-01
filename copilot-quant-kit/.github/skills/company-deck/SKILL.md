---
name: company-deck
description: "Build PowerPoint decks in the company template: brand fonts, colors, backgrounds, and logos come from the template's own example slides, not from code. Use for any slide, deck, or presentation the user asks for, including stakeholder updates, model results, and demos."
---

# Company deck

Corporate templates put part of the brand on their example slides (red titles, slide backgrounds, logos, styled tables), not only in the layouts. So a deck starts from copies of the template's example slides, and the renderer replaces only the text and data. The formatting already on each text run, table cell, and background stays.

## Files in this skill folder

| File | What it is | Who changes it |
|---|---|---|
| `assets/<template>.pptx` | The company template, saved as .pptx, with its example slides | A person |
| `slide_catalog.yaml` | Each example slide: number, layout, roles (title, body, ...), other shapes by name with sample text | `inspect_template.py` |
| `layout_map.yaml` | Each layout of each master, with roles, and the text limits (`max_chars`) | `inspect_template.py`, then a person tunes `max_chars` |
| `brand.yaml` | Theme colors and fonts of each master | `inspect_template.py` |
| `scripts/inspect_template.py` | Writes the three files and prints where title colors and backgrounds come from | |
| `scripts/render_deck.py` | Builds the deck from a deck YAML file | |
| `deck_example.yaml` | Example deck YAML | |

## One-time setup (a person does this)

1. Open the template in PowerPoint and Save As `.pptx` into `assets/`.
2. Make sure the template has one well-formatted example slide for each slide type you use: title, content with bullets, two columns, table, chart. If the template has none, make them once by hand in PowerPoint (these are the "golden slides").
3. Run `python scripts/inspect_template.py assets/<template>.pptx` in this folder. Read the report. If example slides show a title color or background that the layouts do not have, that brand formatting lives on the slides, and `source:` keeps it.
4. Build one deck, open it in PowerPoint, and lower `max_chars` in `layout_map.yaml` until no text overflows.

## Steps for each deck

1. Get the content first. Every number comes from a file. Write the source in the slide `notes`.
2. Read `slide_catalog.yaml`. Pick an example slide for each slide of the deck.
3. Write the deck YAML in the project, for example `data/output/decks/<name>.yaml`, following `deck_example.yaml`:
   - `source: <n>`: copy example slide n. Always prefer this.
   - `layout: <key>`: start from an empty layout. Use only if no example slide fits; brand formatting on example slides is lost.
   - Content by role: `title`, `subtitle`, `body`, `body_2`, ... (the roles listed for that slide in the catalog).
   - Content by shape name: `shapes: {"Source note": "text", "Results table": {table: ...}}`.
   - `remove: ["shape name"]` for sample shapes you do not use. Placeholders you do not fill are removed.
   - Text: a string. Bullets: a list; an item can be `{text: ..., level: 1}`.
   - Table: `{table: {columns: [...], rows: [[...]]}}`. Into an existing template table, rows are added or removed and the style is kept. Column count must match.
   - Chart: `{chart: {type: column | bar | line | stacked_column, categories: [...], series: {name: [values]}, number_format: "0.0"}}`.
   - Image: `{image: path}`.
4. Run `python <this skill folder>/scripts/render_deck.py <deck.yaml>` from the project folder.
5. If it prints `WARN`, cut the text and run again. Do not raise the limits.
6. Tell the user the deck path. The user checks it in PowerPoint before it goes to anyone.

## Rules

- Do not set fonts, colors, sizes, or positions in code or YAML. If the brand looks wrong, the example slide or the template is wrong. Tell the user and show the inspect report.
- Do not change the scripts, the template, or the YAML files in this folder. Hooks block edits here. If a script fails, report the error to the user.
- Slide text: ASD-STE100 writing skill, STE-flavored mode. No em dashes.
- The template and the decks stay on the work machine. Do not put them in a public repo.
