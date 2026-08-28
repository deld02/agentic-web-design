def add_research_identity(text):
    text = text.replace("IDENTITY_STATUS: `EVALUATED | NO_EXISTING_IDENTITY`", "IDENTITY_STATUS: EVALUATED", 1)
    marker = "|---|---|---|---|---|---|---|---|"
    pos = text.find(marker, text.find("## Identity authority contract"))
    row = (
        "\n| IDN-001 | Existing wordmark and deep-ink palette / supplied identity | Primary recognition cue across current material | "
        "EVOLVE_WITHIN_LIMITS | Supports expert authority but needs warmer editorial range | Extend neutrals and add one restrained "
        "material accent | Do not replace deep ink as the principal recognition field or make the result look like another consultancy | 03 / 04 |"
    )
    return text[:pos] + marker + row + text[pos + len(marker):]


def add_direction_identity(text):
    marker = "|---|---|---|---|---|"
    pos = text.find(marker, text.find("### Identity constraint fit"))
    rows = (
        "\n| DIR-001 | IDN-001 | Preserve deep ink and wordmark; vary only neutral paper range | Recognition remains direct; risk is excessive restraint | PASS |"
        "\n| DIR-002 | IDN-001 | Preserve deep ink as principal field and evolve with one copper material accent | Recognition survives while editorial warmth increases | PASS |"
        "\n| DIR-003 | IDN-001 | Preserve deep ink and constrain translucent color to support roles | Recognition survives; risk is over-signalling technology | PASS |"
    )
    text = text[:pos] + marker + rows + text[pos + len(marker):]
    return text.replace("IDENTITY_INHERITANCE: `IDN-* | NO_EXISTING_IDENTITY`", "IDENTITY_INHERITANCE: IDN-001", 1)


def add_visual_identity(text):
    text = text.replace("IDENTITY_INHERITANCE: `IDN-* | NO_EXISTING_IDENTITY`", "IDENTITY_INHERITANCE: IDN-001", 1)
    marker = "|---|---|---|---|---|---|---|---|"
    pos = text.find(marker, text.find("### Independent color challenge"))
    row = (
        "\n| CLR-900:evidence/clr-challenge-sheet.png | hierarchy weakens | identity flattens | becomes interchangeable | IDN-001 | "
        "Deep-ink recognition remains dominant; no prohibited consequence observed | selected improves material distinction without losing recognition | PASS |"
    )
    return text[:pos] + marker + row + text[pos + len(marker):]
