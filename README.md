# 🌹 Loulou - Poèmes Quotidiens

Un agent IA qui envoie chaque jour un poème d'un grand auteur français, accompagné d'une analyse, d'une anecdote et d'une question ouverte, directement dans votre boîte mail.

---

## 📌 Fonctionnalités

- **Génération de poèmes** : Utilise l'agent Mistral `ag_01a136da2b79714f9b339f3c3140d133` pour créer des poèmes uniques.
- **Base de données** : Stocke les poèmes envoyés dans **Supabase** pour éviter les doublons.
- **Envoi d'emails** : Envoye automatiquement le poème du jour via **SMTP (Gmail)**.
- **Planification** : Prêt pour un déploiement sur **Trainway** avec exécution quotidienne.

---

## ⚙️ Prérequis

- Python 3.10+
- Un compte [Mistral AI](https://mistral.ai/) avec accès à l'API
- Un projet [Supabase](https://supabase.com/) pour stocker les poèmes
- Un compte email (ex: Gmail) pour l'envoi des emails

---

## 🛠 Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-utilisateur/Loulou-poemes.git
   cd Loulou-poemes
   ```

2. **Créer un environnement virtuel** :
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```
   *Ou avec `uv` (recommandé) :*
   ```bash
   uv sync
   ```

4. **Configurer les variables d'environnement** :
   Créez un fichier `.env` à la racine du projet avec les variables suivantes :
   ```env
   # Mistral
   MISTRAL_API_KEY=votre_clé_api_mistral

   # Supabase
   SUPABASE_URL=https://votre-projet.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   # Email (Gmail)
   EMAIL_SENDER=votre@gmail.com
   EMAIL_PASSWORD=votre_mot_de_passe_app  # Utilisez un "App Password" si 2FA activé
   EMAIL_RECIPIENT=destinataire@gmail.com
   ```

---

## 📦 Dépendances

Les dépendances principales sont :
- `mistralai` : Pour interagir avec l'API Mistral et ses agents.
- `supabase` : Pour stocker et gérer les poèmes dans la base de données.
- `python-dotenv` : Pour charger les variables d'environnement.

---

## 🚀 Utilisation

### **Localement**
Pour tester le script localement :
```bash
python main.py
```

### **Avec Trainway**
1. **Créez un fichier `trainway.yaml`** (déjà inclus dans le projet) :
   ```yaml
   agent:
     name: loulou-poemes
     runtime: python3.10
     schedule: "0 9 * * *"  # Tous les jours à 9h
     env:
       - MISTRAL_API_KEY
       - SUPABASE_URL
       - SUPABASE_KEY
       - EMAIL_SENDER
       - EMAIL_PASSWORD
       - EMAIL_RECIPIENT
   ```

2. **Déployez sur Trainway** :
   - Suivez la [documentation Trainway](https://docs.trainway.io/) pour importer votre projet.
   - Configurez les variables d'environnement dans l'interface Trainway.
   - L'agent s'exécutera automatiquement selon le `schedule`.

---

## 🗃 Structure du Projet

```
Loulou-poemes/
├── .env                  # Variables d'environnement (à ne pas commiter)
├── .gitignore            # Fichiers ignorés par Git
├── README.md             # Documentation
├── main.py              # Script principal
├── pyproject.toml       # Configuration du projet
├── requirements.txt     # Dépendances (si utilisé)
├── trainway.yaml        # Configuration pour Trainway
└── uv.lock              # Verrouillage des dépendances (uv)
```

---

## 📝 Structure d'un Poème

Chaque poème généré suit ce format :
1. **Titre et auteur** en gras (ex: **🌹 "Le Dormeur du val" - Arthur Rimbaud**)
2. **Introduction** courte entre guillemets
3. **Poème** entre balises `>`
4. **Analyse** sous **🔍 Analyse**
5. **Anecdote** sous **💡 Anecdote**
6. **Question ouverte** à la fin

---

## 🔧 Configuration Supabase

1. **Créez une table `poemes`** dans votre projet Supabase avec le schéma suivant :
   ```sql
   CREATE TABLE IF NOT EXISTS poemes (
       id SERIAL PRIMARY KEY,
       titre TEXT NOT NULL,
       auteur TEXT NOT NULL,
       contenu TEXT NOT NULL,
       date_envoi TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```
   *Note : Le script crée automatiquement cette table si elle n'existe pas.*

2. **Récupérez vos identifiants** :
   - `SUPABASE_URL` : Disponible dans **Paramètres du projet > API**
   - `SUPABASE_KEY` : Générez une clé anonyme ou de service dans **Paramètres du projet > API**

---

## 📧 Configuration Email (Gmail)

1. **Activez l'option "App Passwords"** si vous utilisez la 2FA :
   - Allez dans [Google Account Security](https://myaccount.google.com/security).
   - Activez la 2FA si ce n'est pas déjà fait.
   - Générez un **App Password** pour utiliser avec ce script.

2. **Objets des emails** :
   Le sujet de l'email suit le format :
   `🌹 {Titre} - {Auteur} | Poème du jour - {Date}`

---

## 🔒 Sécurité

- **Ne commitez jamais** votre fichier `.env` ou les clés API dans Git.
- Utilisez des **App Passwords** pour Gmail plutôt que votre mot de passe principal.
- Restreignez les permissions de votre clé Supabase.

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Ouvrez une issue ou proposez une pull request.

---

## 📜 Licence

Ce projet est sous licence **MIT**.