import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

st.set_page_config(page_title="HisKi-haku", layout="wide")

st.title("HisKi-hakutyökalu")
st.caption("Suomen Sukututkimusseuran HisKi-tietokannan epävirallinen käyttöliittymä")

# ---- INPUT ----
col1, col2, col3 = st.columns(3)

with col1:
    firstname = st.text_input("Etunimi", "")

with col2:
    lastname = st.text_input("Sukunimi", "")

with col3:
    parish = st.text_input("Seurakunta (vapaa teksti)", "")

col4, col5 = st.columns(2)

with col4:
    year_from = st.number_input("Vuodesta", 1500, 1950, 1800)

with col5:
    year_to = st.number_input("Vuoteen", 1500, 1950, 1850)

event_type = st.selectbox(
    "Tapahtuma",
    ["kastetut", "vihityt", "haudatut"]
)

search_button = st.button("Hae")

# ---- FUNCTION ----
def fetch_hiski(firstname, lastname, parish, year_from, year_to):
    url = "https://hiski.genealogia.fi/hiski"

    # HUOM: nämä parametrit ovat arvio – oikea HisKi käyttää hieman erilaisia
    params = {
        "fi": "",
        "firstname": firstname,
        "lastname": lastname,
        "parish": parish,
        "year_from": year_from,
        "year_to": year_to,
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    if not table:
        return []

    rows = []
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if cols:
            rows.append(cols)

    return rows

# ---- SEARCH ----
if search_button:
    with st.spinner("Haetaan tietoja HisKistä..."):
        time.sleep(1)  # pieni throttling

        data = fetch_hiski(
            firstname,
            lastname,
            parish,
            year_from,
            year_to
        )

    if data is None:
        st.error("Virhe haussa")
    elif len(data) == 0:
        st.warning("Ei tuloksia tai rakenne ei tunnistettu")
    else:
        df = pd.DataFrame(data)

        st.success(f"Löytyi {len(df)} riviä")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Lataa CSV",
            csv,
            "hiski_tulokset.csv",
            "text/csv"
        )
