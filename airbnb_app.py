import streamlit as st
import pandas as pd
import plotly.express as px
from playwright.sync_api import sync_playwright
from io import BytesIO
import base64

# Função para extrair dados reais de anúncios do Airbnb usando Playwright
def extract_data_from_links(links):
    extracted_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for link in links:
            try:
                page.goto(link, timeout=10000)
                page.wait_for_selector("span[data-testid='price-amount']", timeout=10000)
                preco_element = page.query_selector("span[data-testid='price-amount']")
                preco = preco_element.inner_text() if preco_element else "N/A"
                title = page.title()

                extracted_data.append({"Link": link, "Título": title, "Preço": preco})
            except Exception as e:
                extracted_data.append({"Link": link, "Erro": str(e)})

        browser.close()
    return extracted_data

# Interface do Streamlit
st.set_page_config(page_title="Análise de Anúncios do Airbnb", layout="centered")
st.markdown("# 📊 Análise Inteligente de Anúncios do Airbnb")
st.write("Cole os links dos anúncios (um por linha):")

input_links = st.text_area("Links", height=150)
links = [l.strip() for l in input_links.split("\n") if l.strip()]

if st.button("Analisar") and links:
    data = extract_data_from_links(links)
    df = pd.DataFrame(data)
    st.markdown("## 📋 Dados Extraídos")
    st.dataframe(df)

