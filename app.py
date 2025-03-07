import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import io
import plotly.express as px
from PIL import Image
import yfinance as yf


st.set_page_config(page_title="Calculateur de Zakat", page_icon="🕌", layout="centered")

# Détecter si le format est mobile
if st.session_state.get("viewport_width", 800) < 600:
    sidebar = st.sidebar
else:
    sidebar = st

# Fonction pour changer le texte selon la langue
def set_language(language):
    if language == "English":
        return {
            "selectLang": "Select language",
            "title": "🕌 Zakat Calculator 🕌",
            "intro": "This calculator helps you determine the amount of Zakat you need to pay based on your assets.\nEnter your assets and debts below, then click 'Calculate Zakat' to see the results.",
            "TitleActif": "Enter your assets",
            "cash": "Cash",
            "gold_value": "Current gold value",
            "investments": "Investments",
            "real_estate": "Real estate for resale",
            "debts": "Immediate debts",
            "calculate_zakat": "Calculate Zakat",
            "result": "Result",
            "total_assets": "Total subject to Zakat",
            "nisab": "Current Nisab threshold",
            "zakat_due": "Zakat due",
            "not_due": "You are not liable for Zakat this year",
            "download_pdf": "Download PDF",
            "download_excel": "Download Excel",
            "compare_assets": "Assets vs Nisab Comparison",
            "refresh_gold_price": "Refresh Gold Price",
            "last_update": "Last Update",
            "zakat_chart_title": "Assets vs Nisab Comparison"
        }
    elif language == "العربية":  # Ajuster pour un affichage correct en arabe
        return {
            "selectLang": "العربية",
            "title": "🕌 حاسبة الزكاة 🕌",
            "intro": "تساعدك هذه الآلة الحاسبة في تحديد مقدار الزكاة الذي يجب دفعه بناءً على أصولك.\nأدخل أصولك وديونك أدناه، ثم انقر على 'احسب الزكاة' لعرض النتائج.",
            "TitleActif": "أدخل أصولك",
            "cash": "نقد",
            "gold_value": "القيمة الحالية للذهب",
            "investments": "الاستثمارات)",
            "real_estate": "العقارات للبيع",
            "debts": "الديون الفورية",
            "calculate_zakat": "احسب الزكاة",
            "result": "النتيجة",
            "total_assets": "إجمالي الأصول الخاضعة للزكاة",
            "nisab": "الحد الأدنى للنصاب",
            "zakat_due": "الزكاة المستحقة",
            "not_due": "أنت لست ملزمًا بدفع الزكاة هذه السنة",
            "download_pdf": "تحميل PDF",
            "download_excel": "تحميل Excel",
            "compare_assets": "مقارنة الأصول مع النصاب",
            "refresh_gold_price": "تحديث سعر الذهب",
            "last_update": "آخر تحديث",
            "zakat_chart_title": "مقارنة الأصول مع النصاب"
        }
    else:  # Français par défaut
        return {
            "selectLang": "Sélectionner la langue",
            "title": "🕌 Calculateur de Zakat 🕌",
            "intro": "Ce calculateur vous permet de déterminer le montant de la Zakat à payer en fonction de vos actifs.\nEntrez vos actifs et dettes dans les champs ci-dessous, puis cliquez sur 'Calculer la Zakat' pour voir les résultats.",
            "TitleActif": "Entrer vos actifs",
            "cash": "Argent liquide",
            "gold_value": "Valeur actuelle de l'or",
            "investments": "Investissements",
            "real_estate": "Biens destinés à la revente",
            "debts": "Dettes immédiates",
            "calculate_zakat": "Calculer la Zakat",
            "result": "Résultat",
            "total_assets": "Total soumis à la Zakat",
            "nisab": "Seuil du Nisab actuel",
            "zakat_due": "Zakat due",
            "not_due": "Vous n'êtes pas redevable de la Zakat cette année",
            "download_pdf": "Télécharger PDF",
            "download_excel": "Télécharger Excel",
            "compare_assets": "Comparaison Actifs vs Nisab",
            "refresh_gold_price": "Actualiser le prix de l'or",
            "last_update": "Dernière mise à jour",
            "zakat_chart_title": "Comparaison Actifs vs Nisab"
        }

# HTML et CSS pour afficher les drapeaux en haut à droite
st.markdown(
    """
    <style>
        //Cacher les icone de streamlit
        #MainMenu {visibility: hidden;}
        footer, header {visibility: hidden;}
        
        ._container_gzau3_1, .st-emotion-cache-gi0tri {
            display: none;
        }
        ._viewerBadge_nim44_23
        {
            display: none;
        }
        ._profileContainer_gzau3_53
        {
            display: none;
        }
        
        .st-emotion-cache-mtjnbi {
            padding: 2rem 1rem 10rem;
        }
     

        @media (max-width: 768px) {
            .title {
                font-size: 6vw;
            }
        }

        /* ======= BOUTONS ======= 
        .stButton>button {
            width: 100%;
            font-size: 1rem;
            padding: 10px;
        }*/

        /* ======= TABLEAUX ======= */
        .dataframe {
            overflow-x: auto;
        }

        /* ======= INPUTS ======= */
        .stTextInput, .stNumberInput, .stSelectbox {
            width: 100%;
        }

        /* ======= RESPONSIVE POUR MOBILE ======= */
        @media (max-width: 600px) {
            html, body, [class*="st-emotion-cache"] {
                font-size: 3vw;
            }
            
            .stButton>button {
                font-size: 4vw;
            }
        }
        .language-selector {
            position: absolute;
            top: -10px;
            right: 10px;
            display: flex;
            gap: 10px;
        }
        .flag-button {
            background: none;
            border: none;
            cursor: pointer;
        }
    </style>
    <div class="language-selector">
        <form action="" method="get">
            <button class="flag-button" name="lang" value="Français">
                <img src="https://flagcdn.com/20x15/fr.png">
            </button>
            <button class="flag-button" name="lang" value="English">
                <img src="https://flagcdn.com/20x15/gb.png">
            </button>
            <button class="flag-button" name="lang" value="العربية">
                <img src="https://flagcdn.com/20x15/sa.png">
            </button>
        </form>
    </div>
    """,
    unsafe_allow_html=True
)

# Récupérer la langue sélectionnée
#query_params = st.experimental_get_query_params()

# Récupérer la langue sélectionnée depuis les paramètres de l'URL
lang_list = st.query_params.get_all("lang")

# Vérifier si la liste est vide et définir une langue par défaut
selected_language = lang_list[0] if lang_list else "Français"

# Récupérer les traductions selon la langue choisie
translations = set_language(selected_language)


# Appliquer du CSS personnalisé pour l'alignement à droite en arabe
if selected_language == "العربية":
    st.markdown("""
        <style>
            body {
                direction: rtl;
                text-align: right;
                }
            .css-1v3fvcr {
                direction: rtl;
                text-align: right;
            }
            .css-1u9tbx2 {
                direction: rtl;
                text-align: right;
            }
        </style>
    """, unsafe_allow_html=True)

st.markdown(f" <p style='text-align: center; font-size: 2.3rem'>{translations['title']}</p>", unsafe_allow_html=True)
st.markdown(translations['intro'])

prixParDefaut = 87
last_update = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Met à jour la date et l'heure

def get_gold_price():
    try:
        gold = yf.Ticker("GC=F")  # Futures Or (Gold)
        gold_price = gold.history(period="1d")["Close"].iloc[-1]
        
        # Convertir en EUR si nécessaire
        eur_usd = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
        gold_price_eur = gold_price / eur_usd  # Convertir USD → EUR
        return round(gold_price_eur / 31.1035, 2)  # Prix par gramme en EUR

    except requests.exceptions.RequestException:
        return prixParDefaut
    except Exception:
        return prixParDefaut

# Actualiser le prix
if st.button(f"🔄 {translations['refresh_gold_price']}"):
    gold_price = get_gold_price()
    st.rerun()

gold_price = get_gold_price()

col1, col2 = st.columns(2)
with col1:
    # Affiche la valeur actuelle de l'or en gramme
    st.write(f"🏅 {translations['gold_value']} : {gold_price:.2f} €/g")
with col2:
    if last_update:
        # Affiche la derniere date de refresh
        st.write(f"🕒 {translations['last_update']} : {last_update}")

nisab = gold_price * 85


with st.expander(f"💰 {translations['TitleActif']}", expanded=True):
    #cash = sidebar.number_input(f"💰 {translations['cash']}", min_value=0.0, format="%.2f")
    cash = sidebar.number_input(f"💰 {translations['cash']}", min_value=0.0, format="%.2f", help="Argent en votre possession")
    gold = sidebar.number_input(f"🏅 {translations['gold_value']}", min_value=0.0, format="%.2f", help="Valeur actuelle totale de l'or possédé")
    investments = sidebar.number_input(f"📈 {translations['investments']}", min_value=0.0, format="%.2f", help="Total des investissements (actions, crypto, etc.)")
    real_estate_resale = sidebar.number_input(f"🏠 {translations['real_estate']}", min_value=0.0, format="%.2f", help="Valeur des biens destinés à la revente")

    sidebar.header(f"💳 {translations['debts']}")
    debts = sidebar.number_input(f"💳 {translations['debts']}", min_value=0.0, format="%.2f", help="Montant total des dettes immédiates")

# Fonction pour générer le fichier Excel avec les résultats
def generate_excel(total_assets, nisab, zakat_due, last_update, gold_price, cash, gold, investments, real_estate_resale, debts):
    # Créer un DataFrame avec les informations pertinentes
    data = {
        "Description": ["Total Assets", "Nisab", "Zakat Due", "Last Update", "Gold Price", "Cash", "Gold", "Investments", "Real Estate Resale", "Debts"],
        "Amount (€)": [total_assets, nisab, zakat_due, last_update, gold_price, cash, gold, investments, real_estate_resale, debts]
    }
    
    df = pd.DataFrame(data)
    
    # Création du fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Zakat Calculation")
    output.seek(0)

    return output

# Initialisation des variables AVANT la condition
total_assets = 0
zakat_due = 0  # On initialise zakat_due ici pour éviter le NameError

# Bouton placé juste après le dernier champ
if cash > 0 or gold > 0 or investments > 0 or real_estate_resale > 0 or debts > 0:
    if sidebar.button(f"📊 {translations['calculate_zakat']}"):
        total_assets = cash + gold + investments + real_estate_resale - debts
        st.subheader(f"📊 {translations['result']}")
        st.write(f"{translations['total_assets']} : **{total_assets:.2f} €**")
        st.write(f"📏 {translations['nisab']} : **{nisab:.2f} €**")
        if total_assets >= nisab:
            zakat_due = total_assets * 0.025
            st.success(f"✅ {translations['zakat_due']} : **{zakat_due:.2f} €**")
        else:
            st.warning(f"❌ {translations['not_due']}")

        st.subheader(f"📊 {translations['compare_assets']}")
        
        # Affiche le graphique avec titre traduit
        #fig = px.bar(x=[translations['total_assets'], translations['nisab']], y=[total_assets, nisab], 
         #   labels={"x": translations['total_assets'], "y": "Montant (€)"}, 
         #   title=translations['zakat_chart_title'])
        #st.plotly_chart(fig)
        
        # Graphique interactif
        df = pd.DataFrame({"Catégorie": [translations['total_assets'], translations['nisab']], "Valeur": [total_assets, nisab]})
        fig = px.bar(df, x="Catégorie", y="Valeur", title=translations['zakat_chart_title'], text_auto='.2f')
        fig.update_layout(
            font=dict(
                color="white",
                family="Courier New, monospace",
                size=18  # Set the font size here
            )
        )
        st.plotly_chart(fig)
        
        # Générer le fichier Excel avec les résultats
        excel_file = generate_excel(total_assets, nisab, zakat_due, last_update, gold_price, cash, gold, investments, real_estate_resale, debts)

        # Bouton pour télécharger le fichier Excel, placé après le calcul des actifs
        st.download_button(
            label=f"📥 {translations['download_excel']}",
            data=excel_file,
            file_name="zakat_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    sidebar.warning(f"❌ {translations['not_due']}")
