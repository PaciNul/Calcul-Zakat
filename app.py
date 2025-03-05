import streamlit as st
import requests

# Fonction pour récupérer le Nisab
def get_nisab():
    url = "https://metals-api.com/api/latest?access_key=DEMO_KEY&base=EUR&symbols=XAU,XAG"
    response = requests.get(url).json()
    
    if "rates" in response:
        gold_price = response["rates"].get("XAU", 0)
        silver_price = response["rates"].get("XAG", 0)
        
        gold_nisab = gold_price / 31.1035 * 85
        silver_nisab = silver_price / 31.1035 * 595
        
        return min(gold_nisab, silver_nisab)
    else:
        return 450  # Valeur approximative par défaut

# Interface utilisateur avec Streamlit
st.title("📊 Calculateur de Zakat")

# Champs de saisie pour les actifs
cash = st.number_input("💰 Argent liquide (comptes, espèces) :", min_value=0.0, step=100.0)
gold = st.number_input("🏅 Valeur de l'or et de l'argent :", min_value=0.0, step=100.0)
investments = st.number_input("📈 Investissements (actions, crypto, etc.) :", min_value=0.0, step=100.0)
pee_savings = st.number_input("🏦 Montant disponible dans le PEE :", min_value=0.0, step=100.0)
receivables = st.number_input("📜 Créances certaines (argent qu'on te doit) :", min_value=0.0, step=100.0)

# Valeur des biens immobiliers
real_estate_resale = st.number_input("🏠 Valeur des biens immobiliers destinés à la revente :", min_value=0.0, step=1000.0)
rental_income = st.number_input("🏢 Revenus locatifs économisés :", min_value=0.0, step=100.0)
land_value = st.number_input("🌱 Valeur du terrain :", min_value=0.0, step=1000.0)

# Déduire les dettes
debts = st.number_input("💳 Dettes à payer immédiatement :", min_value=0.0, step=100.0)

# Bouton pour calculer la Zakat
if st.button("🧮 Calculer la Zakat"):
    total_assets = cash + gold + investments + pee_savings + receivables + real_estate_resale + rental_income + land_value - debts
    nisab = get_nisab()

    st.subheader(f"📊 Total soumis à la Zakat : {total_assets:.2f} €")
    st.subheader(f"📏 Seuil du Nisab actuel : {nisab:.2f} €")

    if total_assets >= nisab:
        zakat_due = total_assets * 0.025
        st.success(f"✅ Tu dois payer : {zakat_due:.2f} € de Zakat")
    else:
        st.warning("❌ Tu n'es pas redevable de la Zakat cette année.")
