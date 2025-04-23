
import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from datetime import datetime
import re

st.set_page_config(page_title="Análise Inteligente de Anúncios do Airbnb")

st.markdown("## 📊 Análise Inteligente de Anúncios do Airbnb")
st.write("Cole os links dos anúncios (um por linha):")

input_links = st.text_area("Links", height=150)
analyze_button = st.button("Analisar")

def extract_airbnb_data(link):
    data = {"Link": link, "Erro": "", "Título": "", "Localização": "", "Nota": "", "Avaliações": "", "Preço por diária": ""}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(link, timeout=60000)

            # Espera para o título e localização
            try:
                page.wait_for_selector('h1', timeout=10000)
            except PlaywrightTimeout:
                data["Erro"] = "Timeout ao esperar o título"
                return data

            # Título do anúncio
            data["Título"] = page.query_selector("h1").inner_text()

            # Localização
            try:
                location = page.query_selector("h1 + div")
                if location:
                    data["Localização"] = location.inner_text()
            except:
                pass

            # Nota e avaliações
            try:
                rating_section = page.query_selector("span[aria-label*='de 5']")
                if rating_section:
                    nota_texto = rating_section.inner_text()
                    match = re.search(r"(\d,\d)", nota_texto)
                    if match:
                        data["Nota"] = match.group(1)
                review_section = page.query_selector("span[aria-label*='avaliações']")
                if review_section:
                    reviews = review_section.inner_text()
                    data["Avaliações"] = reviews
            except:
                pass

            # Preço
            try:
                calendar_price = page.query_selector("span[class*='_tyxjp1']")
                if calendar_price:
                    data["Preço por diária"] = calendar_price.inner_text()
                else:
                    # Alternativa de fallback
                    price_fallback = page.query_selector("span[class*='price']")
                    if price_fallback:
                        data["Preço por diária"] = price_fallback.inner_text()
            except:
                pass

            browser.close()
    except Exception as e:
        data["Erro"] = str(e)
    return data

if analyze_button and input_links.strip():
    links = [l.strip() for l in input_links.splitlines() if l.strip()]
    result_data = []

    with st.spinner("Extraindo informações dos anúncios..."):
        for link in links:
            if not link.startswith("http"):
                link = f"https://www.airbnb.com.br/rooms/{link}"
            data = extract_airbnb_data(link)
            result_data.append(data)

    df = pd.DataFrame(result_data)
    st.markdown("### 📋 Dados Extraídos")
    st.dataframe(df)

