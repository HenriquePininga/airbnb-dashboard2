import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import time

st.set_page_config(page_title="Análise Inteligente de Anúncios do Airbnb", layout="wide")
st.title("📊 Análise Inteligente de Anúncios do Airbnb")

st.markdown("Cole os links dos anúncios (um por linha):")
links_input = st.text_area("Links", height=200)

@st.cache_resource
def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(options=options)

def extract_data(link, driver):
    try:
        driver.get(link)
        time.sleep(5)

        title = driver.find_element(By.CSS_SELECTOR, 'h1[data-testid="title"]')
        location = driver.find_element(By.CSS_SELECTOR, 'span[class*="hpipapi"]')

        try:
            rating = driver.find_element(By.CSS_SELECTOR, 'span[aria-label*="nota"]').text
        except:
            rating = "-"

        try:
            reviews = driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="avali"] span').text
        except:
            reviews = "-"

        try:
            price = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="book-it-default-text"]').text
        except:
            price = "-"

        return {
            "Link": link,
            "Título": title.text,
            "Localização": location.text,
            "Nota": rating,
            "Avaliações": reviews,
            "Preço por diária": price
        }

    except Exception as e:
        return {"Link": link, "Erro": str(e)}

if st.button("Analisar"):
    if links_input.strip():
        links = [l.strip() for l in links_input.split("\n") if l.strip()]
        driver = get_driver()
        data = [extract_data(link, driver) for link in links]
        driver.quit()

        df = pd.DataFrame(data)
        st.markdown("### 🗂️ Dados Extraídos")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Por favor, insira ao menos um link.")

