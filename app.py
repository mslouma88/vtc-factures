import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import plotly.express as px
from streamlit_option_menu import option_menu
import datetime

# Configuration de la page Streamlit
st.set_page_config(
    page_title="📊 Gestion Factures VTC",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            color: #1E88E5;
            padding: 20px;
        }
        .stat-card {
            padding: 20px;
            border-radius: 10px;
            background-color: #f8f9fa;
            margin: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('data/vtc_factures.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS factures
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         numero_facture TEXT,
         date_course TIMESTAMP,
         depart TEXT,
         arrivee TEXT,
         kilometrage REAL,
         duree INTEGER,
         tarif_base REAL,
         montant_total REAL,
         tva REAL,
         client_email TEXT,
         statut TEXT DEFAULT 'émise',
         notes TEXT)
    ''')
    conn.commit()
    conn.close()

# Fonction de génération de PDF améliorée
def generer_facture_pdf(data):
    doc = SimpleDocTemplate(f"factures/facture_{data['numero_facture']}.pdf", pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé
    styles.add(ParagraphStyle(
        name='Custom',
        fontSize=12,
        spaceAfter=30,
        textColor=colors.HexColor('#1E88E5')
    ))
    
    # En-tête avec logo
    if os.path.exists('logo.png'):
        elements.append(Image('logo.png', width=100, height=100))
    
    # Informations principales
    elements.append(Paragraph("🚗 FACTURE VTC", styles['Heading1']))
    elements.append(Spacer(1, 20))
    
    # Informations du chauffeur
    company_info = [
        ["🏢 VTC Service Pro"],
        ["📍 123 rue de Paris"],
        ["📮 75000 Paris"],
        ["📱 +33 6 12 34 56 78"],
        ["📧 contact@vtcpro.fr"],
        [f"📄 Facture N° {data['numero_facture']}"],
        [f"📅 Date: {data['date_course'].strftime('%d/%m/%Y %H:%M')}"]
    ]
    
    for info in company_info:
        elements.append(Paragraph(info[0], styles['Custom']))
    
    elements.append(Spacer(1, 20))
    
    # Détails de la course
    details = [
        ['🚩 Départ', data['depart']],
        ['🏁 Arrivée', data['arrivee']],
        ['📏 Kilométrage', f"{data['kilometrage']} km"],
        ['⏱️ Durée', f"{data['duree']} min"],
        ['💰 Tarif de base', f"{data['tarif_base']:.2f} €"],
        ['📊 TVA (20%)', f"{data['tva']:.2f} €"],
        ['💶 Montant total TTC', f"{data['montant_total']:.2f} €"]
    ]
    
    t = Table(details)
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1E88E5')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5'))
    ]))
    
    elements.append(t)
    doc.build(elements)
    return f"factures/facture_{data['numero_facture']}.pdf"

# Fonctions statistiques
def calculer_statistiques(df):
    if df.empty:
        return {}
    
    stats = {
        'total_courses': len(df),
        'ca_total': df['montant_total'].sum(),
        'km_total': df['kilometrage'].sum(),
        'duree_moyenne': df['duree'].mean(),
        'ticket_moyen': df['montant_total'].mean(),
        'courses_jour': df.groupby(df['date_course'].dt.date)['numero_facture'].count().mean()
    }
    return stats

# Interface principale améliorée
def main():
    init_db()
    
    st.markdown("<h1 class='main-title'>🚗 Gestion des Factures VTC</h1>", unsafe_allow_html=True)
    
    # Menu latéral amélioré
    with st.sidebar:
        selected = option_menu(
            menu_title="📋 Menu Principal",
            options=[
                "Nouvelle Facture",
                "Historique",
                "Tableau de Bord",
                "Paramètres"
            ],
            icons=['plus-circle', 'clock-history', 'graph-up', 'gear'],
            menu_icon="list",
            default_index=0,
        )
        
    
    if selected == "Nouvelle Facture":
        st.subheader("📝 Création d'une nouvelle facture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date_course = st.date_input("📅 Date de la course")
            heure_course = st.time_input("⏰ Heure de la course")
            depart = st.text_input("🚩 Lieu de départ")
            arrivee = st.text_input("🏁 Lieu d'arrivée")
        
        with col2:
            kilometrage = st.number_input("📏 Kilométrage (km)", min_value=0.0)
            duree = st.number_input("⏱️ Durée (minutes)", min_value=0)
            tarif_base = st.number_input("💰 Tarif de base (€)", min_value=0.0)
            email_client = st.text_input("📧 Email du client")
            notes = st.text_area("📝 Notes additionnelles")
        
        if st.button("🔨 Générer la facture"):
            if not all([depart, arrivee, kilometrage, duree, tarif_base, email_client]):
                st.error("⚠️ Veuillez remplir tous les champs obligatoires!")
                return
            
            datetime_course = datetime.combine(date_course, heure_course)
            numero_facture = f"VTC-{datetime_course.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
            
            tva = tarif_base * 0.20
            montant_total = tarif_base + tva
            
            # Création du dictionnaire des données
            data = {
                'numero_facture': numero_facture,
                'date_course': datetime_course,
                'depart': depart,
                'arrivee': arrivee,
                'kilometrage': kilometrage,
                'duree': duree,
                'tarif_base': tarif_base,
                'tva': tva,
                'montant_total': montant_total,
                'client_email': email_client,
                'notes': notes,
                'statut': 'émise'
            }
            
            # Génération du PDF
            if not os.path.exists('factures'):
                os.makedirs('factures')
            
            try:
                fichier_pdf = generer_facture_pdf(data)
                
                # Sauvegarde en base de données
                conn = sqlite3.connect('data/vtc_factures.db')
                df = pd.DataFrame([data])
                df.to_sql('factures', conn, if_exists='append', index=False)
                conn.close()
                
                st.success("✅ Facture générée avec succès!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération de la facture: {str(e)}")
    
    elif selected == "Historique":
        st.subheader("📚 Historique des factures")
        
        # Filtres améliorés
        col1, col2, col3 = st.columns(3)
        with col1:
            date_debut = st.date_input("📅 Date de début")
        with col2:
            date_fin = st.date_input("📅 Date de fin")
        with col3:
            statut_filter = st.selectbox(
                "🔍 Statut",
                ["Tous", "émise", "payée", "annulée"]
            )
        

        conn = sqlite3.connect('data/vtc_factures.db')
        df = pd.read_sql_query("SELECT * FROM factures", conn)
        conn.close()
        
        if not df.empty:
            df['date_course'] = pd.to_datetime(df['date_course'])
            
            # Application des filtres
            mask = (df['date_course'].dt.date >= date_debut) & \
                   (df['date_course'].dt.date <= date_fin)
            if statut_filter != "Tous":
                mask &= (df['statut'] == statut_filter)
            
            df_filtered = df.loc[mask]
            
            # Affichage des données avec mise en forme
            st.dataframe(
                df_filtered.style.format({
                    'montant_total': '{:.2f} €',
                    'kilometrage': '{:.1f} km',
                    'duree': '{:.0f} min'
                })
            )
            
            # Export
            if st.button("📥 Exporter en Excel"):
                df_filtered.to_excel("export_factures.xlsx", index=False)
                st.success("✅ Export réalisé avec succès!")
    
    elif selected == "Tableau de Bord":
        st.subheader("📊 Tableau de bord")
        
        # Période d'analyse
        col1, col2 = st.columns(2)
        with col1:
            periode = st.selectbox(
                "📅 Période d'analyse",
                ["7 derniers jours", "30 derniers jours", "Cette année", "Tout"]
            )
        
        conn = sqlite3.connect('data/vtc_factures.db')
        df = pd.read_sql_query("SELECT * FROM factures", conn)
        conn.close()
        
        if not df.empty:
            df['date_course'] = pd.to_datetime(df['date_course'])
            
            # Filtrage par période
            today = datetime.now()
            if periode == "7 derniers jours":
                df = df[df['date_course'] >= today - timedelta(days=7)]
            elif periode == "30 derniers jours":
                df = df[df['date_course'] >= today - timedelta(days=30)]
            elif periode == "Cette année":
                df = df[df['date_course'].dt.year == today.year]
            
            # Statistiques globales
            stats = calculer_statistiques(df)
            
            # Affichage des KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                    <div class='stat-card'>
                        <h3>🚗 Courses</h3>
                        <p>{}</p>
                    </div>
                """.format(stats['total_courses']), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class='stat-card'>
                        <h3>💰 CA Total</h3>
                        <p>{:.2f} €</p>
                    </div>
                """.format(stats['ca_total']), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                    <div class='stat-card'>
                        <h3>📏 Distance</h3>
                        <p>{:.1f} km</p>
                    </div>
                """.format(stats['km_total']), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                    <div class='stat-card'>
                        <h3>💶 Ticket moyen</h3>
                        <p>{:.2f} €</p>
                    </div>
                """.format(stats['ticket_moyen']), unsafe_allow_html=True)
            
            # Graphiques
            col1, col2 = st.columns(2)
            
            with col1:
                # Évolution du CA
                fig_ca = px.line(
                    df.groupby(df['date_course'].dt.date)['montant_total'].sum().reset_index(),
                    x='date_course',
                    y='montant_total',
                    title="📈 Évolution du chiffre d'affaires"
                )
                st.plotly_chart(fig_ca)
            
            with col2:
                # Répartition des courses par jour
                fig_courses = px.bar(
                    df.groupby(df['date_course'].dt.date)['numero_facture'].count().reset_index(),
                    x='date_course',
                    y='numero_facture',
                    title="📊 Nombre de courses par jour"
                )
                st.plotly_chart(fig_courses)
    
    elif selected == "Paramètres":
        st.subheader("⚙️ Paramètres")
        
        # Paramètres de l'entreprise
        st.subheader("🏢 Informations de l'entreprise")
        company_settings = {
            'name': st.text_input("🏪 Nom de l'entreprise", value="VTC Service Pro"),
            'address': st.text_input("📍 Adresse", value="123 rue de Paris"),
            'postal_code': st.text_input("📮 Code postal", value="75000"),
            'city': st.text_input("🏙️ Ville", value="Paris"),
            'phone': st.text_input("📱 Téléphone", value="+33 6 12 34 56 78"),
            'email': st.text_input("📧 Email", value="contact@vtcpro.fr"),
            'siret': st.text_input("📑 Numéro SIRET", value="123 456 789 00000"),
            'tva_number': st.text_input("💶 Numéro de TVA", value="FR 12 345678900")
        }

        # Paramètres de facturation
        st.subheader("💰 Paramètres de facturation")
        col1, col2 = st.columns(2)
        with col1:
            default_rate = st.number_input("🏷️ Tarif horaire par défaut (€/h)", value=45.0)
            min_fare = st.number_input("💶 Tarif minimum de la course (€)", value=15.0)
        with col2:
            tva_rate = st.number_input("📊 Taux de TVA (%)", value=20.0)
            km_rate = st.number_input("🚗 Prix au kilomètre (€/km)", value=1.5)

        # Paramètres d'email
        st.subheader("📧 Configuration email")
        email_settings = {
            'smtp_server': st.text_input("🖥️ Serveur SMTP", value="smtp.gmail.com"),
            'smtp_port': st.number_input("🔌 Port SMTP", value=587),
            'email_user': st.text_input("👤 Adresse email"),
            'email_password': st.text_input("🔑 Mot de passe", type="password")
        }

        # Personnalisation des factures
        st.subheader("🎨 Personnalisation des factures")
        col1, col2 = st.columns(2)
        with col1:
            primary_color = st.color_picker("🎨 Couleur principale", value="#1E88E5")
            logo = st.file_uploader("🖼️ Logo de l'entreprise", type=['png', 'jpg', 'jpeg'])
        with col2:
            footer_text = st.text_area("📝 Texte de pied de page", value="Merci de votre confiance!")
            invoice_prefix = st.text_input("🏷️ Préfixe des numéros de facture", value="VTC-")

        # Sauvegarde des paramètres
        if st.button("💾 Sauvegarder les paramètres"):
            try:
                # Création d'un dictionnaire de configuration
                config = {
                    'company': company_settings,
                    'billing': {
                        'default_rate': default_rate,
                        'min_fare': min_fare,
                        'tva_rate': tva_rate,
                        'km_rate': km_rate
                    },
                    'email': email_settings,
                    'appearance': {
                        'primary_color': primary_color,
                        'footer_text': footer_text,
                        'invoice_prefix': invoice_prefix
                    }
                }
                
                # Sauvegarde du logo si uploadé
                if logo is not None:
                    with open('logo.png', 'wb') as f:
                        f.write(logo.getbuffer())
                
                # Sauvegarde de la configuration dans un fichier JSON
                import json
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
                
                st.success("✅ Paramètres sauvegardés avec succès!")
                st.balloons()
            
            except Exception as e:
                st.error(f"❌ Erreur lors de la sauvegarde des paramètres: {str(e)}")

        # Bouton de réinitialisation
        if st.button("🔄 Réinitialiser les paramètres"):
            try:
                if os.path.exists('config.json'):
                    os.remove('config.json')
                if os.path.exists('logo.png'):
                    os.remove('logo.png')
                st.success("✅ Paramètres réinitialisés avec succès!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors de la réinitialisation: {str(e)}")

    now = datetime.datetime.now()
    st.sidebar.write(f"© {now.year} VTC MEJRI ")
if __name__ == "__main__":
    main()