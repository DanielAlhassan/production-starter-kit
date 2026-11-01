import sys
from pathlib import Path

import yaml
from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn

from deck_roles import describe_fill, map_roles

DRAWING_NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def main() -> None:
    """Read the company template and write brand.yaml, layout_map.yaml, and slide_catalog.yaml.

    Usage: python inspect_template.py <template.pptx> [output folder]
    The output folder defaults to the skill folder.
    - brand.yaml: theme colors and fonts of each slide master.
    - layout_map.yaml: every layout of every master, with its roles (title,
      subtitle, body, body_2, ...) and text limits.
    - slide_catalog.yaml: every example slide in the template, with its roles
      and its other shapes (text boxes, tables, pictures) and their sample text.
      Decks copy these slides, so the formatting on the slides is kept.
    The printed report shows where the title color and the background come
    from at each level (master, layout, example slide).
    """
    if len(sys.argv) < 2:
        sys.exit("Usage: python inspect_template.py <template.pptx> [output folder]")
    template = Path(sys.argv[1])
    out_dir = (
        Path(sys.argv[2])
        if len(sys.argv) > 2
        else Path(__file__).resolve().parent.parent
    )
    deck = Presentation(template)

    masters = []
    layouts = {}
    print(f"Template: {template.name}\nSlide masters: {len(deck.slide_masters)}")
    for m_index, master in enumerate(deck.slide_masters):
        theme = etree.fromstring(master.part.part_related_by(RT.THEME).blob)
        colors = {}
        for slot in theme.find(".//a:clrScheme", DRAWING_NS):
            rgb = slot.find("a:srgbClr", DRAWING_NS)
            system = slot.find("a:sysClr", DRAWING_NS)
            value = (
                rgb.get("val")
                if rgb is not None
                else system.get("lastClr")
                if system is not None
                else None
            )
            colors[etree.QName(slot).localname] = f"#{value}" if value else None
        fonts = {
            "headings": theme.find(".//a:majorFont/a:latin", DRAWING_NS).get(
                "typeface"
            ),
            "body": theme.find(".//a:minorFont/a:latin", DRAWING_NS).get("typeface"),
        }
        masters.append(
            {
                "master": m_index,
                "colors": colors,
                "chart_colors": [
                    colors[f"accent{n}"]
                    for n in range(1, 7)
                    if colors.get(f"accent{n}")
                ],
                "fonts": fonts,
            }
        )
        title_style = master._element.find(f"{qn('p:txStyles')}/{qn('p:titleStyle')}")
        print(
            f"\n== Master {m_index}: {len(master.slide_layouts)} layouts, fonts {fonts['headings']} / {fonts['body']}"
        )
        print(f"   background: {describe_fill(master._element.cSld.bg)}")
        print(f"   title color: {describe_fill(title_style)}")
        for layout in master.slide_layouts:
            key = "_".join(layout.name.lower().replace("-", " ").split())
            key = f"m{m_index}_{key}" if len(deck.slide_masters) > 1 else key
            layouts[key] = {
                "name": layout.name,
                "master": m_index,
                **map_roles(layout.placeholders),
            }
            title = next(
                (ph for ph in layout.placeholders if "title" in ph.name.lower()), None
            )
            print(
                f"   layout '{layout.name}': background {describe_fill(layout._element.cSld.bg)}, "
                f"title color {describe_fill(title._element if title is not None else None)}"
            )

    catalog = {}
    print(f"\n== Example slides: {len(deck.slides)}")
    for number, slide in enumerate(deck.slides, start=1):
        master_index = next(
            i
            for i, m in enumerate(deck.slide_masters)
            if m == slide.slide_layout.slide_master
        )
        roles = map_roles(slide.placeholders)
        role_by_idx = {idx: role for role, idx in roles.items()}
        shapes = []
        for shape in slide.shapes:
            role = (
                role_by_idx.get(shape.placeholder_format.idx)
                if shape.is_placeholder
                else None
            )
            kind = (
                "table"
                if shape.has_table
                else "chart"
                if shape.has_chart
                else str(shape.shape_type).split(".")[-1].split(" ")[0].lower()
            )
            text = (
                shape.text_frame.text.strip().replace("\n", " / ")[:60]
                if shape.has_text_frame
                else ""
            )
            shapes.append(
                {"name": shape.name, "role": role, "kind": kind, "sample_text": text}
            )
        title = slide.shapes.title
        catalog[number] = {
            "layout": slide.slide_layout.name,
            "master": master_index,
            "background": "set on slide"
            if slide._element.cSld.bg is not None
            else "from layout or master",
            "roles": list(roles),
            "shapes": shapes,
        }
        print(
            f"   slide {number}: layout '{slide.slide_layout.name}' (master {master_index}), "
            f"background {describe_fill(slide._element.cSld.bg)}, "
            f"title color {describe_fill(title._element if title is not None else None)}, "
            f"title text '{title.text_frame.text[:40] if title is not None else ''}'"
        )

    brand = {
        "source_template": template.name,
        "masters_note": "Master 0 is listed first. If example slides use another master, use that master's brand.",
        **{k: v for k, v in masters[0].items() if k != "master"},
        "other_masters": masters[1:],
    }
    (out_dir / "brand.yaml").write_text(
        yaml.safe_dump(brand, sort_keys=False), encoding="utf-8"
    )
    layout_map = {
        "template": f"assets/{template.name}",
        "max_chars": {"title": 45, "bullet": 90, "bullets_per_slide": 5},
        "layouts": layouts,
    }
    (out_dir / "layout_map.yaml").write_text(
        yaml.safe_dump(layout_map, sort_keys=False), encoding="utf-8"
    )
    (out_dir / "slide_catalog.yaml").write_text(
        yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
    )
    print(f"\nWrote brand.yaml, layout_map.yaml, slide_catalog.yaml to {out_dir}")


if __name__ == "__main__":
    main()
