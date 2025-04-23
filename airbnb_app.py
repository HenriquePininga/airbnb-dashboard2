import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Análise Inteligente de Anúncios do Airbnb", layout="wide")
st.title("📊 Análise Inteligente de Anúncios do Airbnb")

st.markdown("Cole os links dos anúncios (um por linha):")
user_input = st.text_area("Links", height=150)

if st.button("Analisar"):
    links = [link.strip() for link in user_input.split("\n") if link.strip()]
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for link in links:
            data = {"Link": link}
            try:
                page = context.new_page()
                page.goto(link, timeout=60000)

                # Título
                try:
                    data["Título"] = page.locator("h1[data-testid='title']").inner_text(timeout=3000)
                except:
                    data["Título"] = "Não encontrado"

                # Localização
                try:
                    data["Localização"] = page.locator("span[class*='hpipapi']").nth(0).inner_text(timeout=3000)
                except:
                    data["Localização"] = "Não encontrado"

                # Nota
                try:
                    data["Nota"] = page.locator("span[class*='r1dxllyb']").nth(0).inner_text(timeout=3000)
                except:
                    data["Nota"] = "Não encontrada"

                # Número de Avaliações
                try:
                    data["Avaliações"] = page.locator("span[class*='r1dxllyb']").nth(1).inner_text(timeout=3000)
                except:
                    data["Avaliações"] = "Não encontrada"

                # Preço médio (considera que você esteja com datas selecionadas automaticamente)
                try:
                    data["Preço por diária"] = page.locator("span[class*='_tyxjp1']").first.inner_text(timeout=3000)
                except:
                    data["Preço por diária"] = "Não encontrado"

            except Exception as e:
                data["Erro"] = str(e)
            finally:
                results.append(data)
                page.close()

        context.close()
        browser.close()

    df = pd.DataFrame(results)
    st.markdown("## 🗃️ Dados Extraídos")
    st.dataframe(df)


