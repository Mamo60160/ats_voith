
# 🎯 SYSTÈME ATS – GUIDE D’UTILISATION COMPLET

---

## 🧾 Objectif

Ce système ATS (Applicant Tracking System) permet de :
- **Analyser automatiquement des CVs** (PDF ou DOCX)
- **Filtrer les candidatures** selon plusieurs critères
- **Attribuer un statut** à chaque candidat
- **Exporter les résultats** (tableau CSV propre)

---

## 🧱 1. Préparation des fichiers

- Crée une archive `.zip` contenant les CVs à analyser.
- Les fichiers doivent être au format **.pdf** ou **.docx**.
- Le nom du fichier sera utilisé comme **identifiant du candidat**.

---

## 📥 2. Importer les CVs

- Clique sur **📦 "Importez un ZIP contenant vos CVs"**
- Sélectionne ton fichier `.zip` contenant les CVs.
- Le système affichera le nombre de CVs détectés et traitera automatiquement les fichiers.

---

## 🧠 3. Analyse des CVs

Chaque CV est analysé pour en extraire :
- Le **texte complet**
- Les **compétences techniques** (ex. Python, SQL, etc.)
- Le **niveau d’anglais** (détecté automatiquement)
- Les **expériences professionnelles**
- La **localisation** (et temps de trajet estimé)

---

## 🧰 4. Appliquer des filtres

Dans le panneau **🛠️ Filtres de sélection** (à gauche), tu peux activer les filtres suivants :

| Filtre               | Description |
|----------------------|-------------|
| 🔍 Compétences        | Coche pour ne garder que ceux ayant les compétences listées |
| 🇬🇧 Niveau d’anglais   | Filtrer par niveau minimum ou badge (🔴, 🟡, 🟢) |
| 📊 Expérience         | Candidats avec expérience pro détectée |
| 🚇 Transport          | Filtrer selon un temps de trajet max en transport |
| 🚗 Voiture            | Filtrer selon un temps de trajet max en voiture |

> 🔧 Tu peux combiner les filtres pour affiner ta sélection.

---

## ✅ 5. Gestion des statuts

Après filtrage, chaque candidat est affiché avec une **colonne "statut"** :

- `✅ Sélectionné`
- `❌ Rejeté`
- `🕐 En attente`

### 🖱️ Modifier les statuts :

- Clique directement sur une cellule de la colonne **"statut"**
- Choisis une valeur dans le menu déroulant

> ✔️ Les statuts sont **enregistrés automatiquement** dans l'application, même si tu changes les filtres.

---

## 📊 6. Statistiques en temps réel

Tu verras en haut :
- Nombre de CV sélectionnés ✅
- Rejetés ❌
- En attente 🕐

Et plus bas :
- Score moyen
- Répartition des niveaux d’anglais
- Top villes détectées

---

## 📤 7. Exporter les données

### 📦 Télécharger tous les candidats :

- Clique sur **⬇️ Télécharger tous les candidats (CSV propre)**.
- Le fichier contient **toutes les colonnes utiles**, **sans texte brut**.

> Tu peux ouvrir le fichier avec Excel ou Google Sheets.

---

## 🧽 8. Réinitialiser

Tu peux réinitialiser tous les statuts à `🕐 En attente` depuis le bouton dédié.

---

## 🔁 9. Rejets et restauration

- Tu peux **voir tous les candidats rejetés** dans une section dédiée.
- Sélectionne ceux à **restaurer** et clique sur "🔁 Restaurer".

---

## 🚀 Conseils supplémentaires

- Utilise des mots-clés précis dans les compétences pour améliorer le score.
- Le système ignore automatiquement les phrases de motivation, pour éviter les faux positifs.
- Le score est basé sur le **nombre de mots-clés trouvés** dans le CV.
