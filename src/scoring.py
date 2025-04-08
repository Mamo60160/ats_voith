import pandas as pd
import re

LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

FUZZY_LEVELS = {
    "courant": "courant", "fluent": "courant", "bilingue": "bilingue",
    "professionnel": "professionnel", "avancé": "avancé",
    "intermédiaire": "intermédiaire", "notions": "notions", "débutant": "débutant"
}

CITY_TRANSPORT_TIMES = {
    "noisy-le-grand": (10, 15), "champs-sur-marne": (5, 8), "torcy": (15, 20),
    "lognes": (8, 12), "bussy-saint-georges": (18, 25), "noisiel": (6, 10),
    "paris": (35, 45), "evry": (60, 75), "montreuil": (25, 35),
    "lagny-sur-marne": (25, 35), "thorigny-sur-marne": (30, 40)
}

def detect_english_level(text):
    text = text.lower()
    fallback = None
    for line in text.splitlines():
        if "anglais" in line or "english" in line:
            fallback = line.strip()
            for level in LEVEL_ORDER[::-1]:
                if level.lower() in fallback:
                    return level.upper()
            for word in FUZZY_LEVELS:
                if word in fallback:
                    return f"Mentionné ({fallback})"
    return f"Mentionné ({fallback})" if fallback else "Non précisé"

def english_badge(level):
    level = level.lower()
    if level == "non précisé":
        return "🔴 Non précisé"
    elif "mentionné" in level:
        return "🟡 " + level
    return "🟢 Niveau " + level.upper()

def extract_experience(text):
    lines = text.lower().splitlines()
    experience_keywords = {
        "stage": "Stage", "freelance": "Freelance", "alternance": "Alternance",
        "cdd": "CDD", "cdi": "CDI", "intérim": "Intérim", "emploi": "Emploi", "bénévolat": "Bénévolat"
    }
    excluded = ["à la recherche", "souhaite", "je cherche", "je souhaite", "objectif", "intéressé par"]
    date_pattern = r"(20\d{2}|19\d{2})"

    count, types_found, details = 0, set(), []
    for line in lines:
        if any(ex in line for ex in excluded):
            continue
        if any(kw in line for kw in experience_keywords) or (re.search(date_pattern, line) and ("-" in line or "à" in line)):
            for kw, label in experience_keywords.items():
                if kw in line:
                    types_found.add(label)
            count += 1
            details.append(line.strip())

    return (
        "✅ Oui" if count > 0 else "❌ Non",
        ", ".join(sorted(types_found)) if types_found else "Non précisé",
        count,
        details[0] if details else "Aucune phrase claire"
    )

def extract_locations(text):
    found, matches = [], []
    text = text.lower()
    for line in text.splitlines():
        for city in CITY_TRANSPORT_TIMES:
            if city in line and city not in found:
                found.append(city)
                matches.append(line.strip())
    return found, matches

def enrich_candidates_data(df, skill_keywords):
    skill_keywords = [s.lower() for s in skill_keywords]
    if "text" not in df.columns:
        return df

    df["score"] = df["text"].apply(lambda t: sum(1 for s in skill_keywords if s in t.lower()))
    df["english_level"] = df["text"].apply(detect_english_level)
    df["english_index"] = df["english_level"].apply(lambda l: LEVEL_ORDER.index(l) if l in LEVEL_ORDER else 0)
    df["english_badge"] = df["english_level"].apply(english_badge)

    experience_info = df["text"].apply(lambda t: pd.Series(extract_experience(t)))
    if not experience_info.empty and experience_info.shape[1] == 4:
        df[["has_experience", "experience_types", "experience_count", "experience_detail"]] = experience_info

    location_info = df["text"].apply(lambda t: pd.Series(extract_locations(t)))
    if not location_info.empty and location_info.shape[1] == 2:
        df[["localisation_villes", "localisation_match"]] = location_info

    df["location"] = df["localisation_villes"].apply(lambda v: v[0] if isinstance(v, list) and v else "non renseignée")
    df["commute_time_transport"] = df["location"].apply(lambda loc: CITY_TRANSPORT_TIMES.get(loc, (999, 999))[0])
    df["commute_time_car"] = df["location"].apply(lambda loc: CITY_TRANSPORT_TIMES.get(loc, (999, 999))[1])
    df["temps_trajet"] = df.apply(
        lambda row: f"{row['commute_time_transport']}min (T) / {row['commute_time_car']}min (V)", axis=1)

    return df

def filter_candidates(df, skill_keywords, min_english_level="B1", min_experience=2,
                      max_commute_transport=45, max_commute_car=60,
                      use_skills=False, use_english=False, use_experience=False,
                      use_transport=False, use_car=False, english_badge_filter="Tous"):
    if "text" in df.columns:
        df = enrich_candidates_data(df, skill_keywords)

    min_index = LEVEL_ORDER.index(min_english_level)
    filtered = df.copy()

    if use_skills:
        filtered = filtered[filtered['score'] > 0]
    if use_english:
        filtered = filtered[filtered['english_index'] >= min_index]
    if use_experience:
        filtered = filtered[filtered['has_experience'] == "✅ Oui"]
    if use_transport:
        filtered = filtered[filtered['commute_time_transport'] <= max_commute_transport]
    if use_car:
        filtered = filtered[filtered['commute_time_car'] <= max_commute_car]

    if english_badge_filter != "Tous":
        if english_badge_filter.startswith("🔴"):
            filtered = filtered[filtered["english_badge"].str.startswith("🔴")]
        elif english_badge_filter.startswith("🟡"):
            filtered = filtered[filtered["english_badge"].str.startswith("🟡")]
        elif english_badge_filter.startswith("🟢"):
            filtered = filtered[filtered["english_badge"].str.startswith("🟢")]

    return filtered.sort_values(by=["score", "english_index"], ascending=[False, False])
