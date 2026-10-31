import sys
from pathlib import Path

import yaml
from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

DRAWING_NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def main() -> None:
    """Read the company template and write brand.yaml and a draft layout_map.yaml.

    Usage: python inspect_template.py <template.pptx> <skill folder>
    brand.yaml holds the theme colors and fonts from the slide master. It is
    the single brand source for decks, and later for Word and Excel outputs.
    layout_map.yaml maps each slide layout to roles (title, subtitle, body,
    body_2, picture, chart, table) and placeholder idx. Keep the layouts you
    use, rename keys if you want, and delete the rest.
    """
    template = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    deck = Presentation(template)

    theme_part = deck.slide_master.part.part_related_by(RT.THEME)
    theme = etree.fromstring(theme_part.blob)
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
        "headings": theme.find(".//a:majorFont/a:latin", DRAWING_NS).get("typeface"),
        "body": theme.find(".//a:minorFont/a:latin", DRAWING_NS).get("typeface"),
    }
    brand = {
        "source_template": template.name,
        "colors": colors,
        "chart_colors": [
            colors[k]
            for k in ("accent1", "accent2", "accent3", "accent4", "accent5", "accent6")
            if colors.get(k)
        ],
        "fonts": fonts,
    }
    (out_dir / "brand.yaml").write_text(
        yaml.safe_dump(brand, sort_keys=False), encoding="utf-8"
    )

    role_names = {
        "TITLE": "title",
        "CENTER_TITLE": "title",
        "SUBTITLE": "subtitle",
        "BODY": "body",
        "OBJECT": "body",
        "PICTURE": "picture",
        "CHART": "chart",
        "TABLE": "table",
    }
    skip_types = {"DATE", "FOOTER", "SLIDE_NUMBER"}
    layouts = {}
    for index, layout in enumerate(deck.slide_layouts):
        print(f"\n[{index}] {layout.name}")
        roles = {"name": layout.name}
        for ph in layout.placeholders:
            kind = (
                ph.placeholder_format.type.name
                if ph.placeholder_format.type
                else "OTHER"
            )
            print(f"    idx {ph.placeholder_format.idx}: {kind} | {ph.name}")
            if kind in skip_types:
                continue
            role = role_names.get(kind, kind.lower())
            count = sum(1 for key in roles if key.startswith(role))
            roles[f"{role}_{count + 1}" if count else role] = ph.placeholder_format.idx
        key = "_".join(layout.name.lower().replace("-", " ").split())
        layouts[key] = roles
    draft = {
        "template": f"assets/{template.name}",
        "max_chars": {"title": 45, "bullet": 90, "bullets_per_slide": 5},
        "layouts": layouts,
    }
    (out_dir / "layout_map.yaml").write_text(
        yaml.safe_dump(draft, sort_keys=False), encoding="utf-8"
    )
    print(f"\nWrote {out_dir / 'brand.yaml'} and {out_dir / 'layout_map.yaml'}")


if __name__ == "__main__":
    main()
