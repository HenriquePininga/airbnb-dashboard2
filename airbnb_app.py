
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
        for link in links:
            try:
                page = context.new_page()
                page.goto(link, timeout=60000)
                page.wait_for_timeout(5000)

                title = page.title()
                preco_selector = '._tyxjp1'
                localizacao_selector = '._1tanv1h'
                avaliacao_selector = '._17p6nbba'
                reviews_selector = '._1iu38lrc'

                preco = page.locator(preco_selector).first.inner_text(timeout=3000)
                localizacao = page.locator(localizacao_selector).first.inner_text(timeout=3000)
                avaliacao = page.locator(avaliacao_selector).first.inner_text(timeout=3000)
                reviews = page.locator(reviews_selector).first.inner_text(timeout=3000)

                extracted_data.append({
                    'Link': link,
                    'Nome': title,
                    'Preço por noite (R$)': preco,
                    'Localização': localizacao,
                    'Avaliação': avaliacao,
                    'Nº de Reviews': reviews
                })

                page.close()
            except Exception as e:
                extracted_data.append({
                    'Link': link,
                    'Erro': str(e)
                })
        browser.close()
    return pd.DataFrame(extracted_data)

# Função para exportar para Excel
def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Airbnb')
        writer.save()
    return base64.b64encode(output.getvalue()).decode()

# Interface Streamlit
st.set_page_config(page_title="Dashboard Airbnb", layout="wide")
st.title("📊 Análise Inteligente de Anúncios do Airbnb")

link_input = st.text_area("Cole os links dos anúncios (um por linha):")

if st.button("Analisar"):
    links = [l.strip() for l in link_input.strip().split('\n') if l.strip()]
    if links:
        df = extract_data_from_links(links)

        st.subheader("📋 Dados Extraídos")
        st.dataframe(df)

        if 'Erro' not in df.columns:
            try:
                df['Preço por noite (R$)'] = df['Preço por noite (R$)'].str.replace("R$", "").str.replace(".", "").str.replace(",", ".").astype(float)
                df['Avaliação'] = df['Avaliação'].str.replace(",", ".").astype(float)
                df['Nº de Reviews'] = df['Nº de Reviews'].str.extract(r'(\d+)').astype(float)

                st.subheader("📈 Estatísticas Gerais")
                preco_medio = df['Preço por noite (R$)'].mean()
                st.metric("Preço Médio por Noite", f"R$ {preco_medio:.2f}")
                st.metric("Média de Avaliações", f"{df['Avaliação'].mean():.2f} ⭐")

                fig_preco = px.bar(df, x='Nome', y='Preço por noite (R$)', title="Preços por Anúncio", text_auto=True)
                st.plotly_chart(fig_preco, use_container_width=True)

                fig_aval = px.bar(df, x='Nome', y='Avaliação', title="Avaliação dos Anúncios", text_auto=True)
                st.plotly_chart(fig_aval, use_container_width=True)

                st.subheader("📤 Exportar Dados")
                excel_base64 = export_excel(df)
                href = f'<a href="data:application/octet-stream;base64,{excel_base64}" download="airbnb_analise.xlsx">📁 Baixar Excel</a>'
                st.markdown(href, unsafe_allow_html=True)

                st.subheader("💡 Sugestões Automáticas")
                max_price = df['Preço por noite (R$)'].max()
                st.info(f"Você poderia cobrar até R$ {max_price * 1.1:.2f} por noite se estiver acima da média e bem avaliado.")

                low_rated = df[df['Avaliação'] < 4.5]
                if not low_rated.empty:
                    st.warning("Anúncios com avaliação abaixo de 4.5 podem melhorar a descrição, fotos ou serviços.")

            except Exception as e:
                st.warning(f"Erro na análise: {e}")
    else:
        st.warning("Por favor, insira ao menos um link.")
