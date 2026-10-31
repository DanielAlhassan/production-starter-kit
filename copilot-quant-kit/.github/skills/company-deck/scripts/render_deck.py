import sys
from pathlib import Path

import yaml
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

SKILL_DIR = Path(__file__).resolve().parent.parent
CHART_TYPES = {
    "bar": XL_CHART_TYPE.BAR_CLUSTERED,
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "line": XL_CHART_TYPE.LINE_MARKERS,
    "stacked_column": XL_CHART_TYPE.COLUMN_STACKED,
}


def main() -> None:
    """Build a deck in the company template from a deck YAML file.

    Usage: python render_deck.py <deck.yaml>
    The deck YAML lists slides. Each slide names a layout key from
    layout_map.yaml and gives content per role (title, subtitle, body, ...).
    Content is text, a list of bullets, a table, a native chart, or an image.
    All fonts, colors, and positions come from the template, not from code.
    Prints a warning for text over the limits in layout_map.yaml and exits
    with 1 if there is a warning, so the text can be cut and the deck rebuilt.
    """
    spec = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    layout_map = yaml.safe_load(
        (SKILL_DIR / "layout_map.yaml").read_text(encoding="utf-8")
    )
    limits = layout_map["max_chars"]
    deck = Presentation(SKILL_DIR / layout_map["template"])
    layouts_by_name = {layout.name: layout for layout in deck.slide_layouts}

    # Remove the template's example slides. Keep its masters and layouts.
    for slide_id in list(deck.slides._sldIdLst):
        deck.part.drop_rel(slide_id.rId)
        deck.slides._sldIdLst.remove(slide_id)

    warnings = []
    for number, slide_spec in enumerate(spec["slides"], start=1):
        roles = layout_map["layouts"][slide_spec["layout"]]
        slide = deck.slides.add_slide(layouts_by_name[roles["name"]])
        placeholders = {ph.placeholder_format.idx: ph for ph in slide.placeholders}
        filled = set()

        for role, content in slide_spec.items():
            if role in ("layout", "notes"):
                continue
            if role not in roles:
                raise KeyError(
                    f"Slide {number}: layout '{slide_spec['layout']}' has no role '{role}'"
                )
            ph = placeholders[roles[role]]
            filled.add(roles[role])

            if isinstance(content, str):
                ph.text_frame.text = content
                if role == "title" and len(content) > limits["title"]:
                    warnings.append(
                        f"Slide {number}: title has {len(content)} characters (limit {limits['title']})"
                    )
            elif isinstance(content, list):
                if len(content) > limits["bullets_per_slide"]:
                    warnings.append(
                        f"Slide {number}: {len(content)} bullets (limit {limits['bullets_per_slide']})"
                    )
                frame = ph.text_frame
                for position, item in enumerate(content):
                    text, level = (
                        (item["text"], item.get("level", 0))
                        if isinstance(item, dict)
                        else (item, 0)
                    )
                    paragraph = (
                        frame.paragraphs[0] if position == 0 else frame.add_paragraph()
                    )
                    paragraph.text = text
                    paragraph.level = level
                    if len(text) > limits["bullet"]:
                        warnings.append(
                            f"Slide {number}: bullet over {limits['bullet']} characters: {text[:40]}..."
                        )
            elif "table" in content:
                table_spec = content["table"]
                size = (len(table_spec["rows"]) + 1, len(table_spec["columns"]))
                if hasattr(ph, "insert_table"):
                    table = ph.insert_table(*size).table
                else:
                    table = slide.shapes.add_table(
                        *size, ph.left, ph.top, ph.width, ph.height
                    ).table
                    ph._element.getparent().remove(ph._element)
                for col, header in enumerate(table_spec["columns"]):
                    table.cell(0, col).text = str(header)
                for row, values in enumerate(table_spec["rows"], start=1):
                    for col, value in enumerate(values):
                        table.cell(row, col).text = str(value)
            elif "chart" in content:
                chart_spec = content["chart"]
                data = CategoryChartData(
                    number_format=chart_spec.get("number_format", "General")
                )
                data.categories = chart_spec["categories"]
                for series_name, values in chart_spec["series"].items():
                    data.add_series(series_name, values)
                chart_type = CHART_TYPES[chart_spec["type"]]
                if hasattr(ph, "insert_chart"):
                    chart = ph.insert_chart(chart_type, data).chart
                else:
                    chart = slide.shapes.add_chart(
                        chart_type, ph.left, ph.top, ph.width, ph.height, data
                    ).chart
                    ph._element.getparent().remove(ph._element)
                chart.has_legend = len(chart_spec["series"]) > 1
                if chart.has_legend:
                    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
                    chart.legend.include_in_layout = False
            elif "image" in content:
                image = Path(content["image"])
                if hasattr(ph, "insert_picture"):
                    ph.insert_picture(str(image))
                else:
                    picture = slide.shapes.add_picture(
                        str(image), ph.left, ph.top, width=ph.width
                    )
                    if picture.height > ph.height:
                        scale = ph.height / picture.height
                        picture.width, picture.height = (
                            int(picture.width * scale),
                            ph.height,
                        )
                    ph._element.getparent().remove(ph._element)

        for idx, ph in placeholders.items():
            if idx not in filled:
                ph._element.getparent().remove(ph._element)
        if slide_spec.get("notes"):
            slide.notes_slide.notes_text_frame.text = slide_spec["notes"]

    output = Path(spec["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    deck.save(output)
    print(f"Saved {output} ({len(spec['slides'])} slides)")
    for warning in warnings:
        print(f"WARN {warning}")
    sys.exit(1 if warnings else 0)


if __name__ == "__main__":
    main()
