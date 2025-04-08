run:
	@echo "🚀 Lancement de l'application Streamlit..."
	streamlit run src/app.py

clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	rm -rf data rejetes __pycache__
	rm -f resultats_ats.csv
	streamlit cache clear
	@echo "✅ Nettoyage terminé."
