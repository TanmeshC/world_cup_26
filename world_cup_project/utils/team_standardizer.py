"""Normalize team names across historical and 2026 datasets."""

TEAM_MAPPING = {
    # Historical nation renames / mergers
    "West Germany": "Germany",
    "German DR": "Germany",
    "Soviet Union": "Russia",
    "Yugoslavia": "Serbia",
    "Serbia and Montenegro": "Serbia",
    "Czechoslovakia": "Czechia",
    "Zaire": "Congo DR",
    # FIFA / schedule naming variants
    "IR Iran": "Iran",
    "Korea Republic": "South Korea",
    "USA": "United States",
    "England ": "England",
    "Côte d'Ivoire": "Ivory Coast",
    "Türkiye": "Turkey",
    "Congo DR": "DR Congo",
    "DR Congo": "DR Congo",
    "Czechia": "Czechia",
    "Czech Republic": "Czechia",
}


def standardize_team_name(team_name):
    if team_name is None or (isinstance(team_name, float)):
        return None
    team_name = str(team_name).strip()
    return TEAM_MAPPING.get(team_name, team_name)


def standardize_dataframe_teams(df, columns):
    """Apply name standardization to specified columns in-place copy."""
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = out[col].apply(standardize_team_name)
    return out
