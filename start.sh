#!/bin/bash

# Instala os navegadores do Playwright
echo "Instalando navegadores do Playwright..."
python3 -m playwright install chromium

# Inicia o Streamlit
echo "Iniciando o Streamlit..."
streamlit run airbnb_app.py --server.port=$PORT --server.address=0.0.0.0
