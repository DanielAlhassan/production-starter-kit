import copy
import sys
from pathlib import Path

import yaml
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.text.text import _Paragraph

from deck_roles import map_roles

SKILL_DIR = Path(__file__).resolve().parent.parent
CHART_TYPES = {
    "bar": XL_CHART_TYPE.BAR_CLUSTERED,
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "line": XL_CHART_TYPE.LINE_MARKERS,
    "stacked_column": XL_CHART_TYPE.COLUMN_STACKED,
}
REL_ATTRIBUTES = [qn("r:embed"), qn("r:id"), qn("r:link"), qn("r:pict")]


def write_paragraphs(frame: object, items: list[tuple[str, int | None]]) -> None:
    # Reuse the paragraph and run formatting already in the shape (per level), then replace the text.
    body = frame._txBody
    paragraphs = body.findall(qn("a:p"))
    models = {}
    for p in paragraphs:
        level = int(p.pPr.get("lvl", 0)) if p.pPr is not None else 0
        models.setdefault(level, copy.deepcopy(p))
    for p in paragraphs:
        body.remove(p)
    for text, level in items:
        p = copy.deepcopy(models.get(level or 0, next(iter(models.values()))))
        first_run = p.find(qn("a:r"))
        run_format = (
            copy.deepcopy(first_run.find(qn("a:rPr")))
            if first_run is not None
            else None
        )
        for child in list(p):
            if child.tag in (qn("a:r"), qn("a:br"), qn("a:fld")):
                p.remove(child)
        body.append(p)
        paragraph = _Paragraph(p, frame)
        run = paragraph.add_run()
        if run_format is not None:
            default = run._r.find(qn("a:rPr"))
            if default is not None:
                run._r.remove(default)
            run._r.insert(0, run_format)
        run.text = text
        if level is not None:
            paragraph.level = level


def fill_shape(
    slide: object,
    shape: object,
    content: object,
    label: str,
    limits: dict,
    warnings: list[str],
) -> None:
    # Put text, bullets, a table, a chart, or an image into one shape, keeping the template's formatting.
    if isinstance(content, str):
        write_paragraphs(shape.text_frame, [(content, None)])
        if label.endswith("title") and len(content) > limits["title"]:
            warnings.append(
                f"{label} has {len(content)} characters (limit {limits['title']})"
            )
        return
    if isinstance(content, list):
        items = [
            (i["text"], i.get("level", 0)) if isinstance(i, dict) else (i, None)
            for i in content
        ]
        write_paragraphs(shape.text_frame, items)
        if len(items) > limits["bullets_per_slide"]:
            warnings.append(
                f"{label}: {len(items)} bullets (limit {limits['bullets_per_slide']})"
            )
        warnings.extend(
            f"{label}: bullet over {limits['bullet']} characters: {text[:40]}..."
            for text, _ in items
            if len(text) > limits["bullet"]
        )
        return
    if "table" in content:
        spec = content["table"]
        values = [spec["columns"], *spec["rows"]]
        if shape.has_table:
            # Keep the template table's style: add or remove rows by copying its last row.
            table_xml = shape.table._tbl
            while len(table_xml.tr_lst) < len(values):
                table_xml.append(copy.deepcopy(table_xml.tr_lst[-1]))
            while len(table_xml.tr_lst) > len(values):
                table_xml.remove(table_xml.tr_lst[-1])
            if len(shape.table.columns) != len(spec["columns"]):
                raise ValueError(
                    f"{label}: template table has {len(shape.table.columns)} columns, content has {len(spec['columns'])}"
                )
            table = shape.table
        elif hasattr(shape, "insert_table"):
            table = shape.insert_table(len(values), len(spec["columns"])).table
        else:
            table = slide.shapes.add_table(
                len(values),
                len(spec["columns"]),
                shape.left,
                shape.top,
                shape.width,
                shape.height,
            ).table
            shape._element.getparent().remove(shape._element)
        for r, row in enumerate(values):
            for c, value in enumerate(row):
                write_paragraphs(table.cell(r, c).text_frame, [(str(value), None)])
        return
    if "chart" in content:
        spec = content["chart"]
        data = CategoryChartData(number_format=spec.get("number_format", "General"))
        data.categories = spec["categories"]
        for name, series in spec["series"].items():
            data.add_series(name, series)
        if hasattr(shape, "insert_chart"):
            chart = shape.insert_chart(CHART_TYPES[spec["type"]], data).chart
        else:
            chart = slide.shapes.add_chart(
                CHART_TYPES[spec["type"]],
                shape.left,
                shape.top,
                shape.width,
                shape.height,
                data,
            ).chart
            shape._element.getparent().remove(shape._element)
        chart.has_legend = len(spec["series"]) > 1
        if chart.has_legend:
            chart.legend.position = XL_LEGEND_POSITION.BOTTOM
            chart.legend.include_in_layout = False
        return
    if "image" in content:
        if hasattr(shape, "insert_picture"):
            shape.insert_picture(str(content["image"]))
            return
        picture = slide.shapes.add_picture(
            str(content["image"]), shape.left, shape.top, width=shape.width
        )
        if picture.height > shape.height:
            scale = shape.height / picture.height
            picture.width, picture.height = int(picture.width * scale), shape.height
        shape._element.getparent().remove(shape._element)


def main() -> None:
    """Build a deck in the company template from a deck YAML file.

    Usage: python render_deck.py <deck.yaml>
    Each slide in the deck YAML starts from one of two things:
    - source: <n>  copies example slide n of the template (see slide_catalog.yaml).
      All formatting on that slide is kept: run colors, background, logos.
      This is the preferred way.
    - layout: <key>  starts from an empty layout (see layout_map.yaml).
    Content goes in by role (title, subtitle, body, body_2, ...) or by shape
    name under `shapes:`. `remove:` lists shape names to delete. Unfilled
    placeholders are removed. The template's own example slides are removed.
    Prints WARN for text over the limits and exits with 1 if there is one.
    """
    spec = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    layout_map = yaml.safe_load(
        (SKILL_DIR / "layout_map.yaml").read_text(encoding="utf-8")
    )
    limits = layout_map["max_chars"]
    deck = Presentation(SKILL_DIR / layout_map["template"])
    template_slides = list(deck.slides)
    template_ids = list(deck.slides._sldIdLst)
    layouts = {
        (m, layout.name): layout
        for m, master in enumerate(deck.slide_masters)
        for layout in master.slide_layouts
    }

    warnings = []
    for number, slide_spec in enumerate(spec["slides"], start=1):
        if "source" in slide_spec:
            source = template_slides[slide_spec["source"] - 1]
            slide = deck.slides.add_slide(source.slide_layout)
            for ph in list(slide.placeholders):
                ph._element.getparent().remove(ph._element)
            rid_map = {}
            for rid, rel in source.part.rels.items():
                if rel.reltype in (RT.SLIDE_LAYOUT, RT.NOTES_SLIDE):
                    continue
                rid_map[rid] = (
                    slide.part.rels.get_or_add_ext_rel(rel.reltype, rel.target_ref)
                    if rel.is_external
                    else slide.part.rels.get_or_add(rel.reltype, rel.target_part)
                )
            if source._element.cSld.bg is not None:
                slide._element.cSld.insert(0, copy.deepcopy(source._element.cSld.bg))
            tree = slide.shapes._spTree
            for element in source.shapes._spTree.iterchildren():
                if element.tag not in (
                    qn("p:nvGrpSpPr"),
                    qn("p:grpSpPr"),
                    qn("p:extLst"),
                ):
                    tree.append(copy.deepcopy(element))
            for element in tree.iter():
                for attribute in REL_ATTRIBUTES:
                    if element.get(attribute) in rid_map:
                        element.set(attribute, rid_map[element.get(attribute)])
        else:
            entry = layout_map["layouts"][slide_spec["layout"]]
            slide = deck.slides.add_slide(
                layouts[(entry.get("master", 0), entry["name"])]
            )

        roles = map_roles(slide.placeholders)
        placeholders = {ph.placeholder_format.idx: ph for ph in slide.placeholders}
        named = {shape.name: shape for shape in slide.shapes}
        filled = set()
        for key, content in slide_spec.items():
            if key in ("source", "layout", "notes", "shapes", "remove"):
                continue
            if key not in roles:
                raise KeyError(
                    f"Slide {number}: no role '{key}'. Roles on this slide: {list(roles)}"
                )
            filled.add(roles[key])
            fill_shape(
                slide,
                placeholders[roles[key]],
                content,
                f"Slide {number} {key}",
                limits,
                warnings,
            )
        for name, content in (slide_spec.get("shapes") or {}).items():
            if name not in named:
                raise KeyError(
                    f"Slide {number}: no shape '{name}'. Shapes: {list(named)}"
                )
            fill_shape(
                slide,
                named[name],
                content,
                f"Slide {number} '{name}'",
                limits,
                warnings,
            )
        for idx, ph in placeholders.items():
            if idx not in filled and ph.name not in (slide_spec.get("shapes") or {}):
                ph._element.getparent().remove(ph._element)
        for name in slide_spec.get("remove") or []:
            named[name]._element.getparent().remove(named[name]._element)
        if slide_spec.get("notes"):
            slide.notes_slide.notes_text_frame.text = slide_spec["notes"]

    for slide_id in template_ids:
        deck.part.drop_rel(slide_id.rId)
        deck.slides._sldIdLst.remove(slide_id)

    output = Path(spec["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    deck.save(output)
    print(f"Saved {output} ({len(spec['slides'])} slides)")
    for warning in warnings:
        print(f"WARN {warning}")
    sys.exit(1 if warnings else 0)


if __name__ == "__main__":
    main()
