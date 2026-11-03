from pptx.oxml.ns import qn

ROLE_NAMES = {
    "TITLE": "title",
    "CENTER_TITLE": "title",
    "SUBTITLE": "subtitle",
    "BODY": "body",
    "OBJECT": "body",
    "PICTURE": "picture",
    "CHART": "chart",
    "TABLE": "table",
}
SKIPPED_TYPES = {"DATE", "FOOTER", "SLIDE_NUMBER"}


def map_roles(placeholders: object) -> dict[str, int]:
    # The same rule names placeholders in layouts and in slides: title, body, body_2, ...
    roles = {}
    for ph in placeholders:
        kind = (
            ph.placeholder_format.type.name if ph.placeholder_format.type else "OTHER"
        )
        if kind in SKIPPED_TYPES:
            continue
        role = ROLE_NAMES.get(kind, kind.lower())
        count = sum(1 for key in roles if key == role or key.startswith(f"{role}_"))
        roles[f"{role}_{count + 1}" if count else role] = ph.placeholder_format.idx
    return roles


def describe_fill(element: object) -> str:
    # Plain-words description of the first fill under an XML element, for the template report.
    if element is None:
        return "not set (inherited)"
    for fill in element.iter(
        qn("a:solidFill"), qn("a:gradFill"), qn("a:blipFill"), qn("p:bgRef")
    ):
        if fill.tag == qn("a:gradFill"):
            return "gradient"
        if fill.tag == qn("a:blipFill"):
            return "picture"
        if fill.tag == qn("p:bgRef"):
            color = fill[0] if len(fill) else None
            return f"theme background style ({color.get('val') if color is not None else '?'})"
        color = fill[0] if len(fill) else None
        if color is None:
            return "solid"
        kind = "rgb" if color.tag == qn("a:srgbClr") else "theme color"
        return f"{kind} {color.get('val')}"
    return "not set (inherited)"
