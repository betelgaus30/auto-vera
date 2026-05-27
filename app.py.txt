import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AutoReale - Calcolo TCO", page_icon="🚗", layout="wide")

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
scelta = st.sidebar.selectbox("Scegli un modello base:", list(CATALOGO_AUTO.keys()))

# Pre-compilazione dati
dati_base = CATALOGO_AUTO[scelta]
stato = st.sidebar.radio("Stato Veicolo:", ["Nuovo", "Usato"])
prezzo = st.sidebar.number_input("Prezzo Reale (€):", value=dati_base[0] if dati_base[0] > 0 else 15000)
consumo = st.sidebar.number_input("Consumo (Km/L o Km/kWh):", value=dati_base[1])
kw = st.sidebar.number_input("Potenza (kW):", value=dati_base[2])
alimentazione = st.sidebar.selectbox("Alimentazione:", ["benzina", "diesel", "ibrida", "elettrica"], index=["benzina", "diesel", "ibrida", "elettrica"].index(dati_base[3]))

st.sidebar.header("👤 Tuo Profilo")
km_annui = st.sidebar.slider("Km che farai all'anno:", 1000, 50000, 15000)
stipendio = st.sidebar.slider("Stipendio Mensile (€):", 800, 5000, 1800)

# --- LOGICA DI CALCOLO ---
prezzi_c = {"benzina": 1.88, "diesel": 1.75, "ibrida": 1.88, "elettrica": 0.45}
costo_e = ((km_annui / consumo) * prezzi_c[alimentazione]) / 12
sval_m = (prezzo * (0.16 if stato == "Nuovo" else 0.08)) / 12
fissi_m = (600 + (kw * 2.58 if alimentazione != "elettrica" else 0)) / 12
manut_m = (km_annui * (0.04 if stato == "Nuovo" else 0.09)) / 12
totale = costo_e + sval_m + fissi_m + manut_m
incidenza = (totale / stipendio) * 100

# --- LAYOUT PRINCIPALE (RISULTATI) ---
st.title("🚗 AutoReale: Il Costo Vero della tua Prossima Auto")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Analisi Mensile: **{totale:.2f}€**")
    
    # Grafico
    fig, ax = plt.subplots()
    labels = ['Energia', 'Svalutazione', 'Fissi', 'Manutenzione']
    sizes = [costo_e, sval_m, fissi_m, manut_m]
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#3498db','#e74c3c','#f1c40f','#2ecc71'])
    st.pyplot(fig)

with col2:
    st.metric("Incidenza Reddito", f"{incidenza:.1f}%")
    if incidenza > 28:
        st.error("⚠️ Sconsigliato: L'auto pesa troppo sul tuo stipendio.")
    elif incidenza > 15:
        st.warning("🧐 Attenzione: Valuta bene i costi fissi.")
    else:
        st.success("✅ Sostenibile: Ottima scelta finanziaria!")

st.markdown("---")
st.subheader("💰 Servizi Consigliati per te")
c1, c2, c3 = st.columns(3)

with c1:
    st.info("**Assicurazione**")
    st.write("Risparmia fino a 200€ sulla polizza.")
    st.button("Vedi Preventivi →", key="ass")

with c2:
    st.info("**Controllo Usato**")
    st.write("Verifica se i km sono reali.")
    st.button("Controlla Targa →", key="targa")

with c3:
    st.info("**Noleggio**")
    st.write("Preferisci un canone fisso?")
    st.button("Offerte Noleggio →", key="nolo")
