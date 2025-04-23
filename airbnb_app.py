import streamlit as st
import pandas as pd
import plotly.express as px
from playwright.sync_api import sync_playwright
from io import BytesIO
import base64

st.set_page_config(page_title="Análise Inteligente de Anúncios do Airbnb")
st.title("📊 Análise Inteligente de Anúncios do Airbnb")

links_input = st.text_area("Cole os links dos anúncios (um por linha):")

if st.button("Analisar"):
    links = [link.strip() for link in links_input.split("\n") if link.strip()]
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for link in links:
            page = context.new_page()
            data = {"Link": link, "Erro": "", "Título": "", "Localização": "", "Nota": "", "Avaliações": "", "Preço por diária": ""}

            try:
                page.goto(link, timeout=60000)
                page.wait_for_timeout(5000)

                data["Título"] = page.locator('h1[data-testid="title"]').inner_text(timeout=3000)

            except Exception as e:
                data["Erro"] = str(e)

            results.append(data)
            page.close()

        browser.close()

    df = pd.DataFrame(results)
    st.markdown("### 📋 Dados Extraídos")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode()
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="dados_airbnb.csv">📥 Baixar CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

