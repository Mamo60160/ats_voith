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

    if "updated_df" not in st.session_state:
        st.session_state["updated_df"] = enriched.copy()

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

    # Met à jour les statuts des candidats dans session_state
    updated_df = st.session_state["updated_df"]
    for name in filtered["name"]:
        if name not in updated_df["name"].values:
            new_row = enriched[enriched["name"] == name]
            updated_df = pd.concat([updated_df, new_row], ignore_index=True)

    # Masquer colonne texte à l'affichage
    display_df = updated_df[updated_df["name"].isin(filtered["name"])].copy()
    if "text" in display_df.columns:
        display_df.drop("text", axis=1, inplace=True)

    # 📊 Statistiques
    st.markdown("### 📈 Statistiques en temps réel")
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Sélectionnés", len(updated_df[updated_df["statut"] == "✅ Sélectionné"]))
    col2.metric("❌ Rejetés", len(updated_df[updated_df["statut"] == "❌ Rejeté"]))
    col3.metric("🕐 En attente", len(updated_df[updated_df["statut"] == "🕐 En attente"]))

    # Boutons d'action globale
    col_a, col_b = st.columns(2)
    if col_a.button("✅ Sélectionner tous les candidats filtrés"):
        updated_df.loc[updated_df["name"].isin(filtered["name"]), "statut"] = "✅ Sélectionné"
        st.session_state["updated_df"] = updated_df
        st.rerun()

    if col_b.button("❌ Rejeter tous les candidats filtrés"):
        updated_df.loc[updated_df["name"].isin(filtered["name"]), "statut"] = "❌ Rejeté"
        st.session_state["updated_df"] = updated_df
        st.rerun()

    # Affichage dynamique
    colonnes_utiles = [
        "statut",            # Statut du candidat (sélectionné, en attente, rejeté)
      "name",              # Nom du fichier CV
      "score",             # Score basé sur les compétences détectées
     "english_badge",     # Badge anglais (🔴, 🟡, 🟢)
      "has_experience",    # Est-ce qu’il y a de l’expérience ?
      "experience_types",  # Type d’expériences trouvées (Stage, CDI, etc.)
      "experience_count",  # Nombre d’expériences détectées
      "experience_detail", # Détail de la première ligne détectée
        "localisation_match",
       "location",          # Ville détectée dans le CV
      "temps_trajet"       # Temps de trajet (Transport/Voiture)
]

# Filtrage des colonnes existantes (sécurité)
    colonnes_utiles = [col for col in colonnes_utiles if col in display_df.columns]

# Affichage propre
    st.dataframe(display_df[colonnes_utiles])



      # 📥 Exporter le tableau affiché tel quel (sans la colonne text)
    st.markdown("### 📥 Exporter ce tableau (CSV)")
    export_df = display_df[colonnes_utiles]  # Utilise exactement les mêmes colonnes que le tableau affiché
    csv_export = export_df.to_csv(index=False, sep=";", encoding="utf-8-sig")
    st.download_button(
        label="⬇️ Télécharger ce tableau en CSV",
        data=csv_export,
        file_name="tableau_candidatures.csv",
        mime="text/csv"
    )


# 📚 Guide d'utilisation de l'ATS
with st.expander("📘 Guide d'utilisation de l'ATS"):
    st.markdown("""
## 📄 Système ATS – Guide Utilisateur

Ce système vous permet de filtrer, trier et suivre les candidatures de façon efficace.

### 🧩 Étapes d'utilisation

1. **Importer les CVs :**
   - Chargez un fichier ZIP contenant des fichiers PDF ou DOCX via l’interface.
   - Les fichiers seront automatiquement analysés.

2. **Appliquer des filtres (barre latérale) :**
   - 🔍 Par compétences (mots-clés)
   - 🇬🇧 Par niveau d’anglais
   - 📊 Par expérience
   - 🚇 Temps max en transport
   - 🚗 Temps max en voiture

3. **Analyser les résultats :**
   - Le tableau affiche tous les candidats enrichis (score, anglais, ville, expérience...).
   - Vous pouvez modifier leur statut via le tableau.

4. **Suivre les statuts :**
   - ✅ Sélectionné
   - ❌ Rejeté
   - 🕐 En attente

5. **Exporter les résultats :**
   - 📤 Télécharger tous les candidats filtrés au format CSV.
   - Les CVs rejetés peuvent être restaurés.

### 📈 Astuces

- Le tableau est interactif : vous pouvez modifier les statuts en direct.
- Les statuts sont sauvegardés dynamiquement pendant la session.
- Cliquez sur les boutons pour filtrer visuellement par statut.

### ℹ️ À savoir

- Le champ `text` est caché à l'affichage pour ne pas encombrer la vue.
- Le bouton d’export CSV génère un tableau lisible sans décalage.

---
""")
