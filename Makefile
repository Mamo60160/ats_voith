.PHONY: run clean

run:
	@echo "🚀 Lancement de l'application Streamlit..."
	@streamlit run src/app.py --server.maxUploadSize=500


clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	@rm -rf data/*
	@echo "✅ Dossier data vidé."

	@echo "🧹 Nettoyage du cache Streamlit..."
	@streamlit cache clear || true

	@echo "✅ Nettoyage terminé."
