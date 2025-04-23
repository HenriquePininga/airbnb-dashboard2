import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Função para extrair dados do Airbnb usando Playwright
def extract_airbnb_data(link):
    data = {"Link": link, "Erro": "", "Título": "", "Localização": "", "Nota": "", "Avaliações": "", "Preço por diária": ""}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(link, timeout=60000)

            data["Título"] = page.locator("h1[data-testid='title"]").inner_text(timeout=3000)
            data["Localização"] = page.locator("[data-testid='subtitle"]").inner_text(timeout=3000)
            data["Nota"] = page.locator("[data-testid='rating-label"]").inner_text(timeout=3000)
            data["Avaliações"] = page.locator("[data-testid='review-count"]").inner_text(timeout=3000)
            data["Preço por diária"] = page.locator("[data-testid='book-it-default"] span").first.inner_text(timeout=3000)

            browser.close()
    except Exception as e:
        data["Erro"] = str(e)
    return data

# Função para simular extração do Airdna via scraping
# Este é um mock - em ambiente real, use Selenium ou outra forma para obter os dados
import random
def extract_airdna_data(location):
    preco_medio = random.randint(100, 450)
    ocupacao = random.randint(40, 90)
    return preco_medio, ocupacao

# App Streamlit
st.set_page_config(layout="centered")
st.markdown("# 📊 Análise Inteligente de Anúncias do Airbnb")
st.markdown("Cole os links dos anúncios (um por linha):")
input_links = st.text_area("Links")
if st.button("Analisar"):
    links = input_links.strip().splitlines()
    resultados = []
    for link in links:
        airbnb_data = extract_airbnb_data(link)
        if airbnb_data["Localização"]:
            preco_medio, ocupacao = extract_airdna_data(airbnb_data["Localização"])
            airbnb_data["Preço médio (Airdna)"] = f"R$ {preco_medio}"
            airbnb_data["Taxa de ocupação"] = f"{ocupacao}%"
            airbnb_data["Sugestão"] = "Aumentar preço" if preco_medio > 200 else "Otimizar descrição"
        else:
            airbnb_data["Preço médio (Airdna)"] = ""
            airbnb_data["Taxa de ocupação"] = ""
            airbnb_data["Sugestão"] = ""
        resultados.append(airbnb_data)

    df = pd.DataFrame(resultados)
    st.markdown("## 📅 Dados Extraídos")
    st.dataframe(df)
    st.download_button("📄 Baixar CSV", df.to_csv(index=False), file_name="dados_airbnb.csv")
