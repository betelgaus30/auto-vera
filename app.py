import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AutoReale - Calcolo TCO Completo", page_icon="🚗", layout="wide")

# --- DATABASE AUTO ---
CATALOGO_AUTO = {
    "Inserimento Manuale": [0, 15.0, 75, "benzina"],
    "Fiat Panda 1.0 Hybrid": [15500, 20.4, 51, "ibrida"],
    "Dacia Sandero Stepway": [16500, 18.2, 67, "benzina"],
    "Toyota Yaris Hybrid": [24500, 26.3, 85, "ibrida"],
    "Volkswagen Golf Diesel": [32000, 22.5, 110, "diesel"],
    "Tesla Model 3": [42000, 6.5, 208, "elettrica"]
}

# --- SIDEBAR (COMANDI) ---
st.sidebar.header("⚙️ Configura Veicolo")
scelta = st.sidebar.selectbox("Modello base:", list(CATALOGO_AUTO.keys()))
dati_base = CATALOGO_AUTO[scelta]
stato = st.sidebar.radio("Stato Veicolo:", ["Nuovo", "Usato"])

km_veicolo = 0
if stato == "Usato":
    km_veicolo = st.sidebar.number_input("Km attuali dell'auto:", value=50000, step=5000)

prezzo = st.sidebar.number_input("Prezzo Reale (€):", value=dati_base[0] if dati_base[0] > 0 else 15000)
consumo = st.sidebar.number_input("Consumo (Km/L o Km/kWh):", value=dati_base[1])
kw = st.sidebar.number_input("Potenza (kW):", value=dati_base[2])
alimentazione = st.sidebar.selectbox("Alimentazione:", ["benzina", "diesel", "ibrida", "elettrica"], index=["benzina", "diesel", "ibrida", "elettrica"].index(dati_base[3]))

# --- SEZIONE FINANZIAMENTO ---
st.sidebar.header("💳 Finanziamento")
usa_finanziamento = st.sidebar.checkbox("Attiva calcolo finanziamento", value=True)
if usa_finanziamento:
    anticipo = st.sidebar.number_input("Anticipo (€):", value=2000, step=500)
    durata_mesi = st.sidebar.slider("Durata (mesi):", 12, 96, 48)
    tan = st.sidebar.slider("TAN (%):", 0.0, 15.0, 6.5, 0.1)
    
    # Calcolo Rata Reale
    capitale = prezzo - anticipo
    tasso_mensile = (tan / 100) / 12
    if tasso_mensile > 0:
        rata = capitale * (tasso_mensile * (1 + tasso_mensile)**durata_mesi) / ((1 + tasso_mensile)**durata_mesi - 1)
    else:
        rata = capitale / durata_mesi
else:
    rata = 0

st.sidebar.header("👤 Tuo Profilo")
km_annui = st.sidebar.slider("Km che farai all'anno:", 1000, 50000, 15000)
stipendio
