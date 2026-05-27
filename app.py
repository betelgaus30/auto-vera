import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AutoReale - Il Calcolatore TCO Definitivo", page_icon="🚗", layout="wide")

# --- DATABASE AUTO ---
CATALOGO_AUTO = {
    "Inserimento Manuale": [0, 15.0, 75, "benzina"],
    "Fiat Panda 1.0 Hybrid": [15500, 20.4, 51, "ibrida"],
    "Dacia Sandero Stepway": [16500, 18.2, 67, "benzina"],
    "Toyota Yaris Hybrid": [24500, 26.3, 85, "ibrida"],
    "Volkswagen Golf Diesel": [32000, 22.5, 110, "diesel"],
    "Tesla Model 3": [42000, 6.5, 208, "elettrica"]
}

# --- SIDEBAR (PANNELLO DI CONTROLLO) ---
st.sidebar.header("⚙️ 1. Configura Veicolo")
scelta = st.sidebar.selectbox("Modello base di riferimento:", list(CATALOGO_AUTO.keys()))
dati_base = CATALOGO_AUTO[scelta]

stato = st.sidebar.radio("Stato del Veicolo:", ["Nuovo", "Usato"])
km_veicolo = 0
if stato == "Usato":
    km_veicolo = st.sidebar.number_input("Km attuali della vettura:", value=50000, step=5000)

prezzo_auto = st.sidebar.number_input("Prezzo del veicolo (€):", value=dati_base[0] if dati_base[0] > 0 else 15000)
consumo = st.sidebar.number_input("Consumo (Km/L o Km/kWh):", value=dati_base[1], min_value=1.0)
kw = st.sidebar.number_input("Potenza del motore (kW):", value=dati_base[2])
alimentazione = st.sidebar.selectbox("Alimentazione:", ["benzina", "diesel", "ibrida", "elettrica"], index=["benzina", "diesel", "ibrida", "elettrica"].index(dati_base[3]))

# --- NUOVA SEZIONE: TIPOLOGIA DI ACQUISTO ---
st.sidebar.header("💰 2. Modalità di Acquisizione")
tipo_acquisto = st.sidebar.selectbox(
    "Come intendi acquisire l'auto?",
    ["Acquisto in Contanti", "Finanziamento / Maxi-Rata (VFG)", "Noleggio a Lungo Termine"]
)

# Inizializzazione variabili finanziarie
quota_mensile_acconto = 0
rata_finanziamento = 0
interessi_totali = 0
maxirata = 0

if tipo_acquisto == "Finanziamento / Maxi-Rata (VFG)":
    anticipo = st.sidebar.number_input("Anticipo Finanziamento (€):", value=3000, step=500)
    maxirata = st.sidebar.number_input("Maxirata Finale / VFG (€):", value=6000, step=500)
    durata_mesi = st.sidebar.slider("Durata del contratto (mesi):", 12, 84, 36)
    tan = st.sidebar.slider("Tasso d'interesse TAN (%):", 0.0, 15.0, 7.5, 0.1)
    
    capitale_da_finanziare = prezzo_auto - anticipo
    tasso_mensile = (tan / 100) / 12
    if tasso_mensile > 0:
        numeratore = capitale_da_finanziare * tasso_mensile * (1 + tasso_mensile)**durata_mesi - maxirata * tasso_mensile
        denominatore = (1 + tasso_mensile)**durata_mesi - 1
        rata_finanziamento = numeratore / denominatore
    else:
        rata_finanziamento = (capitale_da_finanziare - maxirata) / durata_mesi
    interessi_totali = (rata_finanziamento * durata_mesi) + maxirata + anticipo - prezzo_auto

elif tipo_acquisto == "Noleggio a Lungo Termine":
    anticipo_nolo = st.sidebar.number_input("Anticipo Noleggio (€):", value=2500, step=500)
    canone_nolo = st.sidebar.number_input("Canone Mensile IVA Inclusa (€):", value=350, step=10)
    durata_nolo_mesi = st.sidebar.slider("Durata Noleggio (mesi):", 24, 60, 36)
    # L'anticipo viene spalmato sui mesi di utilizzo per calcolare il costo mensile reale
    quota_mensile_acconto = anticipo_nolo / durata_nolo_mesi

st.sidebar.header("👤 3. Tuo Profilo d'Uso")
km_annui = st.sidebar.slider("Chilometri percorsi all'anno:", 1000, 50000, 15000)
stipendio = st.sidebar.slider("Tuo Stipendio Mensile Netto (€):", 800, 5000, 1800)

# --- MOTORE DI CALCOLO TCO REALE ---
prezzi_carburante = {"benzina": 1.85, "diesel": 1.75, "ibrida": 1.85, "elettrica": 0.40}
costo_carburante_m = ((km_annui / consumo) * prezzi_carburante[alimentazione]) / 12

# Calcolo spese di gestione basato sulla tipologia di acquisto
if tipo_acquisto == "Noleggio a Lungo Termine":
    # Nel noleggio bollo, assicurazione e manutenzione sono COMPRESI nel canone
    fissi_m = 0 
    manut_m = 0
    sval_m = 0  # Il rischio svalutazione è a carico della società di noleggio
    quota_acquisizione_m = canone_nolo + quota_mensile_acconto
else:
    # Acquisto Cash o Finanziamento: le spese di gestione sono a carico del proprietario
    fissi_m = (650 + (kw * 2.58 if alimentazione != "elettrica" else 0)) / 12  # Assicurazione media + Bollo italiano
    manut_m = (km_annui * (0.05 + (km_veicolo / 1000000))) / 12
    sval_m = (prezzo_auto * (0.15 if stato == "Nuovo" else 0.07)) / 12
    
    if tipo_acquisto == "Finanziamento / Maxi-Rata (VFG)":
        quota_acquisizione_m = rata_finanziamento
    else:
        # Se contanti, non c'è una rata mensile fisica, ma includiamo la svalutazione patrimoniale 
        # per far capire all'utente quanto valore perde l'auto ogni mese
        quota_acquisizione_m = sval_m

# COSTO TOTALE MENSILE REALE
totale_mensile = quota_acquisizione_m + costo_carburante_m + fissi_m + manut_m
incidenza = (totale_mensile / stipendio) * 100

# --- INTERFACCIA UTENTE PRINCIPALE ---
st.title("🚗 AutoReale: Il Costo Totale di Proprietà (TCO)")
st.markdown(f"Analisi corrente: **{scelta}** | Modalità: **{tipo_acquisto}** ({stato})")
st.markdown("---")

# KPI Principali
c1, c2, c3, c4 = st.columns(4)
with c1:
    if tipo_acquisto == "Finanziamento / Maxi-Rata (VFG)":
        st.metric("Rata Finanziamento", f"{rata_finanziamento:.2f} €")
    elif tipo_acquisto == "Noleggio a Lungo Termine":
        st.metric("Canone + Quota Anticipo", f"{quota_acquisizione_m:.2f} €")
    else:
        st.metric("Svalutazione Vettura", f"{sval_m:.2f} €/mese")
with c2:
    st.metric("Spesa Carburante/Mese", f"{costo_carburante_m:.2f} €")
with c3:
    st.metric("Manutenzione + Fissi", f"{(manut_m + fissi_m):.2f} €")
with c4:
    st.metric("COSTO MENSILE COMPLESSIVO", f"{totale_mensile:.2f} €", delta=f"{incidenza:.1f}% del Reddito", delta_color="inverse")

st.markdown("---")

col_sx, col_dx = st.columns([2, 1])

with col_sx:
    st.subheader("Ripartizione Proporzionale dei Costi Mensili")
    labels = ['Acquisizione/Svalutazione', 'Carburante/Energia', 'Spese Fisse (Ass/Bollo)', 'Manutenzione Stimata']
    valori = [quota_acquisizione_m, costo_carburante_m, fissi_m, manut_m]
    
    # Rimuove le voci a zero (es. nel caso del noleggio) per non sporcare il grafico
    dati_filtrati = {l: v for l, v in zip(labels, valori) if v > 0}
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(dati_filtrati.keys(), dati_filtrati.values(), color=['#9b59b6', '#3498db', '#f1c40f', '#2ecc71'])
    ax.set_ylabel('Euro (€) / Mese')
    plt.xticks(rotation=15)
    st.pyplot(fig)

with col_dx:
    st.subheader("Informativa Finanziaria")
    
    if tipo_acquisto == "Finanziamento / Maxi-Rata (VFG)":
        st.write(f"🏦 **Capitale finanziato:** {prezzo_auto - anticipo:.2f} €")
        st.write(f"📉 **Interessi totali passivi:** {max(0, interessi_totali):.2f} €")
        st.write(f"🏁 **Maxirata finale (VFG):** {maxirata:.2f} €")
    elif tipo_acquisto == "Noleggio a Lungo Termine":
        st.write("ℹ️ **Vantaggio Noleggio:** Assicurazione Kasko, RC, Bollo e manutenzioni ordinarie e straordinarie sono azzerate perché incluse nel canone.")
        st.write(f"📉 **Costo totale del contratto:** {(quota_acquisizione_m * durata_nolo_mesi):.2f} €")
    else:
        st.write(f"💰 **Esborso iniziale immediato:** {prezzo_auto:.2f} €")
        st.write("ℹ️ L'acquisto in contanti elimina gli interessi bancari, ma ti espone interamente alla svalutazione dell'auto sul mercato dell'usato.")

    st.markdown("---")
    st.subheader("Sostenibilità del Budget")
    if incidenza > 30:
        st.error(f"Sconsigliato: Questo veicolo richiede il {incidenza:.1f}% del tuo stipendio. Supera la soglia di sicurezza del 30%.")
    elif incidenza > 20:
        st.warning(f"Attenzione: L'auto incide per il {incidenza:.1f}% sulle tue entrate. Impegno finanziario moderato.")
    else:
        st.success(f"Approvato: L'impatto mensile è solo del {incidenza:.1f}%. Perfettamente sostenibile.")

st.markdown("---")
st.subheader("🛒 Ottimizza la spesa (Link Affiliati)")
a1, a2, a3 = st.columns(3)
with a1:
    st.link_button("🛡️ Trova un'Assicurazione più economica", "https://www.segugio.it")
with a2:
    st.link_button("📋 Verifica lo storico dei Km (CarVertical)", "https://www.carvertical.com")
with a3:
    st.link_button("🏦 Confronta Prestiti Auto alternativi", "https://www.facile.it")
