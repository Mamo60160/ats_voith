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

# Nettoyage du dossier data au démarrage
if os.path.exists("data"):
    shutil.rmtree("data")
os.makedirs("data", exist_ok=True)

# Upload
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

    for idx, path in enumerate(uploaded_files):
        name = os.path.basename(path)
        text = extract_text_from_pdf(path) if path.endswith(".pdf") else extract_text_from_docx(path)
        candidates.append({"name": name, "text": text})
        progress.progress((idx + 1) / len(uploaded_files))

    df = pd.DataFrame(candidates)

    # Filtres dans la sidebar
    st.sidebar.markdown("### 🔍 Filtres actifs")
    use_skills = st.sidebar.checkbox("Compétences", value=False)
    use_english = st.sidebar.checkbox("Niveau d'anglais", value=False)
    use_experience = st.sidebar.checkbox("Expérience", value=False)
    use_transport = st.sidebar.checkbox("Transport", value=False)
    use_car = st.sidebar.checkbox("Voiture", value=False)

    skills = st.sidebar.text_area("Compétences clés", "Python, SQL, React").split(",")
    skills = [s.strip() for s in skills if s.strip()]
    min_english = st.sidebar.selectbox("Niveau anglais min", ["A1", "A2", "B1", "B2", "C1", "C2"], index=2)
    badge = st.sidebar.selectbox("Badge anglais requis", ["Tous", "🔴 Non précisé", "🟡 Mentionné", "🟢 Niveau"], index=0)
    min_exp = st.sidebar.slider("Expérience min (années)", 0, 10, 2)
    max_trans = st.sidebar.slider("Transport max (min)", 0, 120, 45)
    max_car = st.sidebar.slider("Voiture max (min)", 0, 120, 60)

    # Enrichissement
    enriched = enrich_candidates_data(df, skills)
    enriched["statut"] = "🕐 En attente"

    # Filtrage
    filtered = filter_candidates(
        enriched, skills,
        min_english_level=min_english,
        min_experience=min_exp,
        max_commute_transport=max_trans,
        max_commute_car=max_car,
        use_skills=use_skills,
        use_english=use_english,
        use_experience=use_experience,
        use_transport=use_transport,
        use_car=use_car,
        english_badge_filter=badge
    )

    # Gestion du DataFrame mis à jour avec statuts conservés
    if "updated_df" not in st.session_state:
        st.session_state.updated_df = filtered.copy()
    else:
        current_names = set(filtered["name"])
        current_df = st.session_state.updated_df
        current_df = current_df[current_df["name"].isin(current_names)]
        new_entries = filtered[~filtered["name"].isin(current_df["name"])]
        st.session_state.updated_df = pd.concat([current_df, new_entries], ignore_index=True)

    updated_df = st.session_state.updated_df

    # Affichage du tableau AgGrid
    st.subheader("📋 Liste des candidatures")
    gb = GridOptionsBuilder.from_dataframe(updated_df.drop(columns=["text"]))
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_column("statut", editable=True, cellEditor='agSelectCellEditor',
                        cellEditorParams={'values': ['✅ Sélectionné', '❌ Rejeté', '🕐 En attente']})
    grid_response = AgGrid(
        updated_df.drop(columns=["text"]),
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        height=500,
        allow_unsafe_jscode=True,
        theme="alpine"
    )
    selected_rows = grid_response["selected_rows"]
    updated_df = grid_response["data"]
    st.session_state.updated_df = updated_df

    # Actions groupées
    st.subheader("🛠️ Actions groupées")
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("✅ Marquer sélectionnés"):
        for row in selected_rows:
            updated_df.loc[updated_df["name"] == row["name"], "statut"] = "✅ Sélectionné"
        st.rerun()
    if col2.button("❌ Marquer rejetés"):
        for row in selected_rows:
            updated_df.loc[updated_df["name"] == row["name"], "statut"] = "❌ Rejeté"
        st.rerun()
    if col3.button("🕐 Marquer en attente"):
        for row in selected_rows:
            updated_df.loc[updated_df["name"] == row["name"], "statut"] = "🕐 En attente"
        st.rerun()
    if col4.button("♻️ Réinitialiser"):
        updated_df["statut"] = "🕐 En attente"
        st.rerun()

    # Statistiques
    st.subheader("📊 Statistiques")
    st.markdown(f"- ✅ Sélectionnés : {len(updated_df[updated_df['statut'] == '✅ Sélectionné'])}")
    st.markdown(f"- ❌ Rejetés : {len(updated_df[updated_df['statut'] == '❌ Rejeté'])}")
    st.markdown(f"- 🕐 En attente : {len(updated_df[updated_df['statut'] == '🕐 En attente'])}")

    # Filtres d’affichage par statut
    st.subheader("🔎 Affichage par statut")
    choix = st.radio("Filtrer :", ["Tous", "✅ Sélectionné", "❌ Rejeté", "🕐 En attente"])
    to_show = updated_df if choix == "Tous" else updated_df[updated_df["statut"] == choix]
    st.dataframe(to_show)

    # Téléchargement CSV sélectionnés uniquement
    csv = updated_df[updated_df["statut"] == "✅ Sélectionné"].to_csv(index=False)
    st.download_button("⬇️ Télécharger les ✅ sélectionnés (.csv)", csv, file_name="candidats_selectionnes.csv", mime="text/csv")
