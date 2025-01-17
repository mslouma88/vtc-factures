# 🚗 Application de Gestion de Factures VTC 📊

![Licence MIT](https://img.shields.io/badge/licence-MIT-green) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.27%2B-red)

Une application web moderne pour la gestion complète des factures de chauffeur VTC, construite avec Streamlit et Python.

## ✨ Fonctionnalités

- 📝 Création facile de factures avec interface intuitive
- 💰 Calcul automatique de la TVA et des totaux
- 📄 Génération automatique de factures PDF professionnelles
- 📧 Envoi automatique des factures par email
- 📊 Tableau de bord avec statistiques et visualisations
- 🗄️ Historique complet des factures avec filtrage
- 📱 Interface responsive pour tous les appareils

## 🚀 Installation

1. Clonez le repository :
```bash
git clone https://github.com/mslouma88/vtc-factures.git
cd vtc-factures
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
```

3. Activez l'environnement virtuel :
- Windows (PowerShell) :
```bash
.\venv\Scripts\Activate.ps1
```
- Windows (CMD) :
```bash
.\venv\Scripts\activate.bat
```
- Linux/macOS :
```bash
source venv/bin/activate
```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## 💻 Utilisation

1. Configurez vos paramètres d'email dans `config.py` :
```python
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "votre-email@gmail.com"
EMAIL_PASSWORD = "votre-mot-de-passe"
```

2. Lancez l'application :
```bash
streamlit run app.py
```

3. Ouvrez votre navigateur à l'adresse : http://localhost:8501

## 📱 Interface

### Page Principale
- 🆕 Création de nouvelle facture
- 📊 Vue d'ensemble des statistiques
- 📋 Liste des dernières factures

### Tableau de Bord
- 📈 Graphiques de performance
- 💰 Analyse du chiffre d'affaires
- 📉 Tendances mensuelles

## 🔧 Configuration Requise

- Python 3.8+
- Streamlit 1.27+
- Pandas 2.0+
- ReportLab 4.0+
- SQLite 3

## 📁 Structure du Projet

```
vtc-factures/
├── app.py              # Application principale
├── config.py           # Configuration
├── requirements.txt    # Dépendances
├── README.md          # Documentation
├── factures/          # Dossier des factures PDF
└── data/              # Base de données SQLite
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. 🍴 Forker le projet
2. 🔨 Créer une branche pour votre fonctionnalité
3. 📝 Commiter vos changements
4. 📤 Pusher vers la branche
5. 🔀 Ouvrir une Pull Request

## 📜 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## ✉️ Contact

- 👨‍💻 Créé par : MEJRI Salam
- 📧 Email : salam.mejri@gmail.com
- 🌐 LinkedIn : [Mon-Profil](https://linkedin.com/in/salam-mejri)


---
⭐️ N'oubliez pas de mettre une étoile si ce projet vous a été utile !


