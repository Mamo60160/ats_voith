import pandas as pd
import re

LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

FUZZY_LEVELS = {
    "courant": "courant",
    "fluent": "courant",
    "bilingue": "bilingue",
    "professionnel": "professionnel",
    "avancé": "avancé",
    "intermédiaire": "intermédiaire",
    "notions": "notions",
    "débutant": "débutant"
}

CITY_TRANSPORT_TIMES = {
    "noisy-le-grand": (10, 15),
    "champs-sur-marne": (5, 8),
    "torcy": (15, 20),
    "lognes": (8, 12),
    "bussy-saint-georges": (18, 25),
    "noisiel": (6, 10),
    "chelles": (20, 30),
    "vaires-sur-marne": (25, 35),
    "gournay-sur-marne": (20, 25),
    "neuilly-sur-marne": (20, 25),
    "villiers-sur-marne": (12, 18),
    "bry-sur-marne": (15, 22),
    "le-perreux-sur-marne": (20, 28),
    "fontenay-sous-bois": (18, 25),
    "rosny-sous-bois": (25, 35),
    "nogent-sur-marne": (22, 30),
    "paris": (35, 45),
    "bagnolet": (30, 40),
    "montreuil": (25, 35),
    "saint-mandé": (25, 30),
    "vincennes": (22, 30),
    "ivry-sur-seine": (30, 40),
    "gentilly": (35, 45),
    "pantin": (28, 38),
    "le-kremlin-bicetre": (35, 45),
    "charenton-le-pont": (28, 35),
    "alfortville": (25, 32),
    "maisons-alfort": (22, 30),
    "creteil": (25, 30),
    "villejuif": (35, 45),
    "vitry-sur-seine": (35, 45),
    "choisy-le-roi": (40, 50),
    "orly": (45, 55),
    "thiais": (40, 50),
    "evry": (60, 75),
    "juvisy-sur-orge": (50, 65),
    "ris-orangis": (60, 70),
    "aubervilliers": (45, 60),
    "saint-denis": (40, 55),
    "clichy": (50, 60),
    "asnieres-sur-seine": (55, 65),
    "levallois-perret": (50, 65),
    "neuilly-sur-seine": (55, 70),
    "courbevoie": (60, 75),
    "nanterre": (65, 80),
    "argenteuil": (65, 85),
    "sarcelles": (65, 85),
    "versailles": (55, 70),
    "meaux": (50, 60),
    "melun": (55, 70),
    "lagny-sur-marne": (25, 35),
    "thorigny-sur-marne": (30, 40)
}

# ----------- DÉTECTION DU NIVEAU D'ANGLAIS ------------

def detect_english_level(text):
    text = text.lower()
    lines = text.splitlines()

    fallback = None

    for line in lines:
        if "anglais" in line or "english" in line:
            clean = line.strip()
            fallback = clean  # On garde en secours

            # Si un niveau clair est précisé, on le détecte directement
            for level in LEVEL_ORDER[::-1]:
                if level.lower() in clean:
                    return level.upper()

            # Sinon, on vérifie les mentions floues
            for word in FUZZY_LEVELS:
                if word in clean:
                    return f"Mentionné ({clean})"

    # Si rien trouvé, on retourne au moins la ligne
    if fallback:
        return f"Mentionné ({fallback})"

    return "Non précisé"


def english_badge(level):
    level = level.lower()
    if level == "non précisé":
        return "🔴 Non précisé"
    elif "mentionné" in level:
        return "🟡 " + level
    else:
        return "🟢 Niveau " + level.upper()

# ----------- DÉTECTION DE L'EXPÉRIENCE ------------

def extract_experience(text):
    lines = text.lower().splitlines()

    # Vrais types d'expérience
    experience_keywords = {
        "stage": "Stage",
        "freelance": "Freelance",
        "alternance": "Alternance",
        "cdd": "CDD",
        "cdi": "CDI",
        "intérim": "Intérim",
        "emploi": "Emploi",
        "bénévolat": "Bénévolat"
    }

    # Mots à exclure (intention, projet, recherche)
    excluded_phrases = [
        "à la recherche", "souhaite", "je cherche", "je souhaite", "objectif", "intéressé par"
    ]

    date_pattern = r"(20\d{2}|19\d{2})"

    count = 0
    types_found = set()
    details = []

    for line in lines:
        clean_line = line.strip()

        if any(ex in clean_line for ex in excluded_phrases):
            continue  # Ne compte pas comme expérience

        match_type = any(kw in clean_line for kw in experience_keywords)
        match_date = re.search(date_pattern, clean_line) and ("-" in clean_line or "à" in clean_line)

        if match_type or match_date:
            # Ajoute type si trouvé
            for kw, label in experience_keywords.items():
                if kw in clean_line:
                    types_found.add(label)

            count += 1
            details.append(clean_line)

    has_exp = "✅ Oui" if count > 0 else "❌ Non"
    type_list = ", ".join(sorted(types_found)) if types_found else "Non précisé"
    detail = details[0] if details else "Aucune phrase claire"

    return has_exp, type_list, count, detail



# ----------- DÉTECTION DES VILLES ------------

def extract_locations(text):
    found = []
    matches = []

    text_lower = text.lower()
    lines = text_lower.splitlines()

    for line in lines:
        for city in CITY_TRANSPORT_TIMES:
            if city in line and city not in found:
                found.append(city)
                matches.append(line.strip())

    return found, matches

# ----------- ENRICHISSEMENT DES DONNÉES ------------

def enrich_candidates_data(df, skill_keywords):
    skill_keywords = [s.lower() for s in skill_keywords]

    df['score'] = df['text'].apply(lambda t: sum(1 for s in skill_keywords if s in t.lower()))
    df['english_level'] = df['text'].apply(detect_english_level)
    df['english_index'] = df['english_level'].apply(lambda lvl: LEVEL_ORDER.index(lvl) if lvl in LEVEL_ORDER else 0)
    df['english_badge'] = df['english_level'].apply(english_badge)
    df[['has_experience', 'experience_types', 'experience_count', 'experience_detail']] = df['text'].apply(lambda txt: pd.Series(extract_experience(txt)))


    df[['localisation_villes', 'localisation_match']] = df['text'].apply(lambda txt: pd.Series(extract_locations(txt)))
    df['location'] = df['localisation_villes'].apply(lambda v: v[0] if v else "non renseignée")
    df['commute_time_transport'] = df['location'].apply(lambda loc: CITY_TRANSPORT_TIMES.get(loc, (999, 999))[0])
    df['commute_time_car'] = df['location'].apply(lambda loc: CITY_TRANSPORT_TIMES.get(loc, (999, 999))[1])
    df['temps_trajet'] = df.apply(lambda row: f"{row['commute_time_transport']}min (T) / {row['commute_time_car']}min (V)", axis=1)

    return df

def filter_candidates(df, skill_keywords, min_english_level="B1", min_experience=2,
                      max_commute_transport=45, max_commute_car=60,
                      use_skills=False, use_english=False, use_experience=False,
                      use_transport=False, use_car=False, english_badge_filter="Tous"):

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

    # 🔍 Ajout du filtre par badge anglais
    if english_badge_filter != "Tous":
        if english_badge_filter == "🔴 Non précisé":
            filtered = filtered[filtered["english_badge"].str.startswith("🔴")]
        elif english_badge_filter == "🟡 Mentionné":
            filtered = filtered[filtered["english_badge"].str.startswith("🟡")]
        elif english_badge_filter == "🟢 Niveau":
            filtered = filtered[filtered["english_badge"].str.startswith("🟢")]

    return filtered.sort_values(by=["score", "english_index"], ascending=[False, False])

















"""""





import streamlit as st
import pandas as pd
import os
import shutil
import zipfile
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from extraction import extract_text_from_pdf, extract_text_from_docx
from scoring import filter_candidates, enrich_candidates_data
from collections import Counter

st.set_page_config(page_title="ATS - Analyse de CV", layout="wide")
st.title("📄 Système ATS – Analyse et tri des candidatures")
st.sidebar.header("🛠️ Filtres de sélection")

if os.path.exists("data"):
    shutil.rmtree("data")
os.makedirs("data", exist_ok=True)
os.makedirs("rejetes", exist_ok=True)

zip_file = st.file_uploader("📦 Importez un ZIP contenant vos CVs (PDF ou DOCX)", type=["zip"])
uploaded_files = []

if zip_file:
    with zipfile.ZipFile(BytesIO(zip_file.read()), "r") as zip_ref:
        zip_ref.extractall("data")

    for root, _, files in os.walk("data"):
        for filename in files:
            if filename.lower().endswith((".pdf", ".docx")):
                uploaded_files.append(os.path.join(root, filename))

if uploaded_files:
    candidates = []
    st.info(f"📁 {len(uploaded_files)} CVs détectés. Analyse en cours...")
    progress = st.progress(0)

    for idx, file_path in enumerate(uploaded_files):
        file_name = os.path.basename(file_path)
        text = extract_text_from_pdf(file_path) if file_path.lower().endswith(".pdf") else extract_text_from_docx(file_path)
        candidates.append({"name": file_name, "text": text})
        progress.progress((idx + 1) / len(uploaded_files))

    candidates_df = pd.DataFrame(candidates)

    # Filtres
    st.sidebar.markdown("### 🔧 Filtres")
    use_skills = st.sidebar.checkbox("🔍 Par compétences", value=False)
    use_english = st.sidebar.checkbox("🇬🇧 Par niveau d'anglais", value=False)
    use_experience = st.sidebar.checkbox("📊 Par expérience", value=False)
    use_transport = st.sidebar.checkbox("🚇 Par transport", value=False)
    use_car = st.sidebar.checkbox("🚗 Par voiture", value=False)

    skill_keywords = st.sidebar.text_area("Compétences requises", "Python, SQL, React").split(",")
    skill_keywords = [s.strip() for s in skill_keywords if s.strip()]
    english_required = st.sidebar.selectbox("Niveau d'anglais minimum", ["A1", "A2", "B1", "B2", "C1", "C2"], index=2)
    badge_selected = st.sidebar.selectbox("Badge anglais requis", ["Tous", "🔴 Non précisé", "🟡 Mentionné", "🟢 Niveau"], index=0)
    min_experience = st.sidebar.slider("Expérience minimum (années)", 0, 10, 2)
    max_commute_transport = st.sidebar.slider("Temps max en transport (min)", 0, 120, 45)
    max_commute_car = st.sidebar.slider("Temps max en voiture (min)", 0, 120, 60)

    # Enrichissement + filtrage
    enriched = enrich_candidates_data(candidates_df, skill_keywords)
    enriched["statut"] = "🕐 En attente"

    filtered = filter_candidates(
        enriched,
        skill_keywords,
        min_english_level=english_required,
        min_experience=min_experience,
        max_commute_transport=max_commute_transport,
        max_commute_car=max_commute_car,
        use_skills=use_skills,
        use_english=use_english,
        use_experience=use_experience,
        use_transport=use_transport,
        use_car=use_car,
        english_badge_filter=badge_selected
    )

    # Session & statuts
    if "updated_df" not in st.session_state:
        st.session_state["updated_df"] = filtered.copy()

    filtered_names = set(filtered["name"])
    updated_df = st.session_state["updated_df"]
    updated_df = updated_df[updated_df["name"].isin(filtered_names)].reset_index(drop=True)
    missing = filtered[~filtered["name"].isin(updated_df["name"])]
    if not missing.empty:
        updated_df = pd.concat([updated_df, missing], ignore_index=True)
    st.session_state["updated_df"] = updated_df
    # 📊 Affichage des compteurs par statut
    st.markdown("### 📈 Statistiques en temps réel")
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    total = len(updated_df)
    nb_select = len(updated_df[updated_df["statut"] == "✅ Sélectionné"])
    nb_rejete = len(updated_df[updated_df["statut"] == "❌ Rejeté"])
    nb_attente = len(updated_df[updated_df["statut"] == "🕐 En attente"])

    col_stat1.metric("✅ Sélectionnés", nb_select)
    col_stat2.metric("❌ Rejetés", nb_rejete)
    col_stat3.metric("🕐 En attente", nb_attente)

    # Tableau interactif
    st.subheader("🧾 Candidatures filtrées")
    gb = GridOptionsBuilder.from_dataframe(updated_df)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_column("statut", editable=True, cellEditor='agSelectCellEditor',
                        cellEditorParams={'values': ['✅ Sélectionné', '❌ Rejeté', '🕐 En attente']})
    grid_options = gb.build()

    grid_response = AgGrid(
        updated_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        height=500,
        allow_unsafe_jscode=True,
        theme='alpine'
    )

    updated_df = grid_response["data"]
    selected_rows = grid_response.get("selected_rows", [])
    st.session_state["updated_df"] = updated_df

    # Actions groupées
    st.markdown("### ⚙️ Actions groupées")
    col1, col2, col3, col4 = st.columns(4)

    if col1.button("✅ Mettre en Sélectionné"):
        if selected_rows is not None and len(selected_rows) > 0:
            for row in selected_rows:
                name = row["name"] if isinstance(row, dict) and "name" in row else str(row)
                updated_df.loc[updated_df["name"] == name, "statut"] = "✅ Sélectionné"
            st.session_state["updated_df"] = updated_df
            st.rerun()

    if col2.button("❌ Mettre en Rejeté"):
        if selected_rows is not None and len(selected_rows) > 0:
            for row in selected_rows:
                name = row["name"] if isinstance(row, dict) and "name" in row else str(row)
                updated_df.loc[updated_df["name"] == name, "statut"] = "❌ Rejeté"
            st.session_state["updated_df"] = updated_df
            st.rerun()

    if col3.button("🕐 Mettre en Attente"):
        if selected_rows is not None and len(selected_rows) > 0:
            for row in selected_rows:
                name = row["name"] if isinstance(row, dict) and "name" in row else str(row)
                updated_df.loc[updated_df["name"] == name, "statut"] = "🕐 En attente"
            st.session_state["updated_df"] = updated_df
            st.rerun()

    if col4.button("♻️ Réinitialiser les statuts"):
        updated_df["statut"] = "🕐 En attente"
        st.session_state["updated_df"] = updated_df
        st.success("Tous les statuts ont été réinitialisés.")
        st.rerun()

    # Filtres visuels
    st.markdown("### 🔎 Filtrer l'affichage")
    choix_statut = st.radio("Voir uniquement :", ["Tous", "✅ Sélectionné", "🕐 En attente", "❌ Rejeté"])
    display_df = updated_df if choix_statut == "Tous" else updated_df[updated_df["statut"] == choix_statut]
    st.dataframe(display_df)

    # Téléchargement ZIP des rejetés
    if st.button("📦 Télécharger les CVs ❌ Rejetés"):
        rejected_files = updated_df[updated_df["statut"] == "❌ Rejeté"]["name"].tolist()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for filename in rejected_files:
                path = os.path.join("data", filename)
                if os.path.exists(path):
                    zipf.write(path, arcname=filename)
        st.download_button("⬇️ Télécharger maintenant", data=zip_buffer.getvalue(),
                           file_name="cv_rejetes.zip", mime="application/zip")

    # Export CSV sélectionnés uniquement
    csv_selectionnes = updated_df[updated_df["statut"] == "✅ Sélectionné"].to_csv(index=False)
    st.download_button("⬇️ Exporter uniquement les ✅ sélectionnés (CSV)", data=csv_selectionnes, file_name="selectionnes.csv", mime="text/csv")
    # 🔁 Restauration des rejetés
    with st.expander("📁 Voir les ❌ Rejetés et restaurer"):
        rejetes = updated_df[updated_df["statut"] == "❌ Rejeté"]
        st.dataframe(rejetes)
        noms_a_restaurer = st.multiselect("Restaurer :", rejetes["name"].tolist())
        if st.button("🔁 Restaurer"):
            updated_df.loc[updated_df["name"].isin(noms_a_restaurer), "statut"] = "🕐 En attente"
            st.session_state["updated_df"] = updated_df
            st.success("Candidatures restaurées.")
            st.rerun()

    # 📋 Résumé RH
    with st.expander("📊 Résumé RH"):
        st.subheader("Statistiques globales")
        st.markdown(f"- **Total de CVs analysés :** {len(updated_df)}")
        st.markdown(f"- ✅ **Sélectionnés :** {nb_select}")
        st.markdown(f"- ❌ **Rejetés :** {nb_rejete}")
        st.markdown(f"- 🕐 **En attente :** {nb_attente}")

        # Score moyen
        score_moyen = updated_df["score"].mean()
        st.markdown(f"- 📈 **Score moyen des candidats :** {score_moyen:.2f}")

        # Top villes
        top_villes = Counter(updated_df["location"]).most_common(3)
        top_villes_str = ", ".join([f"{ville} ({nb})" for ville, nb in top_villes])
        st.markdown(f"- 🏙️ **Top localisations :** {top_villes_str}")

        # English level breakdown
        levels = Counter(updated_df["english_badge"])
        st.markdown("- 🇬🇧 **Répartition des badges anglais :**")
        for level, nb in levels.items():
            st.markdown(f"  - {level} : {nb} CVs")

    # 🧠 Compétences détectées
    st.subheader("🧠 Compétences détectées")
    for _, row in updated_df.iterrows():
        found_skills = [s for s in skill_keywords if s.lower() in row['text'].lower()]
        st.markdown(f"**{row['name']}** : {', '.join(found_skills) if found_skills else 'Aucune détectée'}")

"""