import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import sys
from datetime import datetime
import io
import plotly.express as px

st.set_page_config(page_title="Calculateur de Zakat", page_icon="🕌", layout="wide")

st.markdown("""
## Calculateur de Zakat
Ce calculateur vous permet de déterminer le montant de la Zakat à payer en fonction de vos actifs. \n
Entrez vos actifs et dettes dans les champs ci-dessous, puis cliquez sur "Calculer la Zakat" pour voir les résultats.
""")


st.title("🕌 Calculateur de Zakat")

prixParDefaut = 87
last_update = None  # Variable pour stocker la date et l'heure de la dernière mise à jour

def get_gold_price():
    global last_update
    url = "https://www.bullion-rates.com/gold/EUR/spot-price.htm"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return prixParDefaut

        soup = BeautifulSoup(response.text, "html.parser")
        price_element = soup.find("td", class_="rate")
        if not price_element:
            price_element = soup.find("td", {"id": "gold-price"})
        
        if price_element:
            price_text = price_element.text.strip()
            gold_price_per_ounce = price_text.replace(" ", "")
            gold_price_per_ounce2 = float(gold_price_per_ounce.replace(",", "."))
            last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Met à jour la date et l'heure
            return gold_price_per_ounce2 / 31.1035
        else:
            return prixParDefaut

    except requests.exceptions.RequestException:
        return prixParDefaut
    except Exception:
        return prixParDefaut

if st.button("🔄 Actualiser le prix de l'or"):
    gold_price = get_gold_price()
    st.rerun()

gold_price = get_gold_price()

col1, col2 = st.columns(2)
with col1:
    st.write(f"🏅 Prix actuel de l'or : {gold_price:.2f} €/g")
with col2:
    if last_update:
        st.write(f"🕒 Dernière mise à jour : {last_update}")

nisab = gold_price * 85

# Détecter si le format est mobile
if st.session_state.get("viewport_width", 800) < 600:
    sidebar = st.sidebar
else:
    sidebar = st


sidebar.header("💰 Entrer vos actifs")

cash = sidebar.number_input("💰 Argent liquide", min_value=0.0, format="%.2f")
gold = sidebar.number_input("🏅 Valeur de l'or et de l'argent", min_value=0.0, format="%.2f")
investments = sidebar.number_input("📈 Investissements (actions, crypto, etc.)", min_value=0.0, format="%.2f")
real_estate_resale = sidebar.number_input("🏠 Biens destinés à la revente", min_value=0.0, format="%.2f")

sidebar.header("💳 Déduire vos dettes")
debts = sidebar.number_input("💳 Dettes immédiates", min_value=0.0, format="%.2f")


# Bouton placé juste après le dernier champ
if cash > 0 or gold > 0 or investments > 0 or real_estate_resale > 0 or debts > 0:
    if sidebar.button("📊 Calculez la Zakat"):
        total_assets = cash + gold + investments + real_estate_resale - debts
        st.subheader("📊 Résultat du calcul")
        st.write(f"Total soumis à la Zakat : **{total_assets:.2f} €**")
        st.write(f"📏 Seuil du Nisab actuel : **{nisab:.2f} €**")
        if total_assets >= nisab:
            zakat_due = total_assets * 0.025
            st.success(f"✅ Tu dois payer **{zakat_due:.2f} €** de Zakat.")
        else:
            st.warning("❌ Tu n'es pas redevable de la Zakat cette année.")
        
        st.subheader("📊 Comparaison Actifs vs Nisab")
        
        # Affiche le graphique
        fig = px.bar(x=["Total Actifs", "Nisab"], y=[total_assets, nisab], 
            labels={"x": "Catégorie", "y": "Montant (€)"}, 
            title="Comparaison Actifs vs Nisab")
        st.plotly_chart(fig)

        def generate_pdf(total_assets, nisab, zakat_due):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=14)
            pdf.cell(200, 10, "Rapport de Calcul de la Zakat", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, f"Total soumis à la Zakat : {total_assets:.2f} €", ln=True)
            pdf.cell(200, 10, f"Seuil du Nisab : {nisab:.2f} €", ln=True)
            if total_assets >= nisab:
                pdf.cell(200, 10, f"Zakat due : {zakat_due:.2f} €", ln=True)
            else:
                pdf.cell(200, 10, "Vous n'êtes pas redevable de la Zakat cette année.", ln=True)
            pdf.output("zakat_report.pdf")

        if st.button("📄 Générer un rapport PDF"):
            generate_pdf(total_assets, nisab, zakat_due)
            with open("zakat_report.pdf", "rb") as file:
                st.download_button("📥 Télécharger le PDF", file, file_name="zakat_report.pdf")
                
        def generate_excel_report(total_assets, nisab, zakat_due):
            df = pd.DataFrame({
                "Description": ["Total soumis à la Zakat", "Seuil du Nisab", "Zakat due"],
                "Montant (€)": [total_assets, nisab, zakat_due if total_assets >= nisab else "N/A"]
            })
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Zakat Report")
            output.seek(0)
            return output

        if st.button("📄 Générer un rapport Excel"):
            excel_file = generate_excel_report(total_assets, nisab, zakat_due)
            st.download_button("📥 Télécharger le fichier Excel", excel_file, file_name="zakat_report.xlsx")
else:
    sidebar.warning("❌ Veuillez remplir au moins un champ avant de calculer la Zakat.")
