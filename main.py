import os
import smtplib
import sqlite3
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
from mistralai.client import Mistral
import json
import time
import sys
import supabase
from supabase import create_client, Client

# Initialiser le client Supabase
supabase: Client = create_client(
    supabase_url=os.environ.get("SUPABASE_URL"),
    supabase_key=os.environ.get("SUPABASE_KEY")
)

# ======================
# CONFIGURATION INITIALE
# ======================
load_dotenv()

# Vérification des variables d'environnement requises
required_vars = ["MISTRAL_API_KEY", "EMAIL_SENDER", "EMAIL_PASSWORD", "EMAIL_RECIPIENT"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    raise ValueError(f"Variables d'environnement manquantes : {', '.join(missing_vars)}")

# Configuration des accès
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT")

# ======================
# BASE DE DONNÉES (Supabase)
# ======================
def init_db():
    """Initialise la table poemes si elle n'existe pas"""
    try:
        supabase.table("poemes").select("*").execute()
    except:
        # La table n'existe pas, on la crée via SQL
        supabase.execute(
            """
            CREATE TABLE IF NOT EXISTS poemes (
                id SERIAL PRIMARY KEY,
                titre TEXT NOT NULL,
                auteur TEXT NOT NULL,
                contenu TEXT NOT NULL,
                date_envoi TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        )

def poemes_deja_envoyes():
    """Récupère les poèmes déjà envoyés"""
    response = supabase.table("poemes").select("titre, auteur").execute()
    return [f"{poem['titre']} - {poem['auteur']}" for poem in response.data]

def sauvegarder_poeme(titre, auteur, contenu):
    """Sauvegarde un nouveau poème"""
    date_actuelle = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    supabase.table("poemes").insert({
        "titre": titre,
        "auteur": auteur,
        "contenu": contenu,
        "date_envoi": date_actuelle
    }).execute()

# ======================
# FONCTIONS D'ENVOI
# ======================
def envoyer_email(poeme, titre, auteur):
    """Envoie le poème par email"""
    msg = EmailMessage()
    msg.set_content(poeme)
    msg["Subject"] = f"🌹 {titre} - {auteur} | Poème du jour - {datetime.now().strftime('%d %B %Y')}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email envoyé : {titre} - {auteur}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")
        raise

# ======================
# FONCTION PRINCIPALE
# ======================
def obtenir_poeme_du_jour():
    """Obtient un nouveau poème de l'agent Loulou"""
    client = Mistral(api_key=MISTRAL_API_KEY)

    # Récupérer les poèmes déjà envoyés
    poemes_exclus = poemes_deja_envoyes()

    # Préparer la requête
    date_du_jour = datetime.now().strftime('%d %B %Y')
    user_message = (
        f"Nous sommes le {date_du_jour}. "
        f"{'Évite ces poèmes déjà partagés : ' + ', '.join(poemes_exclus) + '.' if poemes_exclus else ''} "
        "Donne-moi un poème d'un grand auteur français avec :\n"
        "1. Le titre et l'auteur en gras au début (ex: **🌹 \"Le Dormeur du val\" - Arthur Rimbaud (1870)**)\n"
        "2. Une introduction courte entre guillemets\n"
        "3. Le poème complet (ou extrait significatif) entre des balises >\n"
        "4. Une analyse sous **🔍 Analyse**\n"
        "5. Une anecdote sous **💡 Anecdote**\n"
        "6. Une question ouverte à la fin\n"
        "Format le tout de manière claire et visuellement agréable."
    )

    inputs = [{"role": "user", "content": user_message}]

    try:
        response = client.beta.conversations.start(
            agent_id="ag_01a136da2b79714f9b339f3c3140d133",
            agent_version=0,
            inputs=inputs,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Erreur Mistral API : {e}")
        raise

def traiter_poeme(poeme_brut):
    """Extrait les métadonnées du poème brut"""
    lines = poeme_brut.split('\n')

    # Extraire le titre et l'auteur (suppose que c'est la première ligne en gras)
    premiere_ligne = [l for l in lines if l.startswith('**🌹') or l.startswith('**')][0] if any(l.startswith('**🌹') or l.startswith('**') for l in lines) else "Poème inconnu - Auteur inconnu"

    # Nettoyer la première ligne pour extraire titre et auteur
    titre_auteur = premiere_ligne.replace('**', '').replace('🌹', '').strip()
    if " - " in titre_auteur:
        titre, auteur = titre_auteur.split(" - ", 1)
        auteur = auteur.split("(")[0].strip()  # Enlever la date si présente
    else:
        titre, auteur = "Poème du jour", "Auteur inconnu"

    return {
        "titre": titre,
        "auteur": auteur,
        "contenu": poeme_brut
    }

# ======================
# PROGRAMME PRINCIPAL
# ======================
def main():
    print(f"🌅 Début de l'exécution à {datetime.now().strftime('%H:%M:%S')}")

    # Initialiser la base de données
    init_db()

    try:
        # Obtenir un nouveau poème
        poeme_brut = obtenir_poeme_du_jour()

        # Extraire les métadonnées
        poeme_data = traiter_poeme(poeme_brut)

        # Afficher dans le terminal
        print("\n--- 🌹 Poème du jour par Loulou 🌹 ---\n")
        print(poeme_brut)

        # Sauvegarder dans la base de données
        sauvegarder_poeme(poeme_data["titre"], poeme_data["auteur"], poeme_data["contenu"])

        # Envoyer par email
        envoyer_email(poeme_brut, poeme_data["titre"], poeme_data["auteur"])

        print(f"\n✨ Poème traitement terminé à {datetime.now().strftime('%H:%M:%S')}")

    except Exception as e:
        print(f"❌ Erreur fatale : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()