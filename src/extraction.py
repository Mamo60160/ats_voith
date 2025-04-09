import subprocess
import os
from docx import Document

def extract_text_from_pdf(file_path):
    txt_path = file_path.replace(".pdf", ".txt")

    try:
        # Convertir le PDF en fichier texte avec pdftotext (exactement comme tu le fais à la main)
        subprocess.run(["pdftotext", file_path, txt_path], check=True)

        # Lire le fichier texte généré
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        return text.strip()

    except Exception as e:
        return f"Erreur lors de l'extraction : {e}"

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
