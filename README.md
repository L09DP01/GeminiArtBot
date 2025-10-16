# GeminiArtBot

Un bot Telegram qui génère des images IA à partir de prompts textuels en utilisant l'API OpenRouter (modèle Gemini 2.5 Flash Image Preview).

## Fonctionnalités

- Génération d'images IA à partir de descriptions textuelles
- Système de crédits (3 crédits gratuits à l'inscription)
- Historique des prompts stocké dans Supabase
- Gestion automatique des utilisateurs

## Prérequis

- Python 3.8+
- Un compte Telegram et un bot token (via @BotFather)
- Un projet Supabase configuré
- Une clé API OpenRouter

## Installation

1. Cloner le projet et installer les dépendances :

```bash
pip install -r requirements.txt
```

2. Copier le fichier `.env.example` vers `.env` :

```bash
cp .env.example .env
```

3. Remplir les variables d'environnement dans `.env` :

```env
TELEGRAM_TOKEN=votre_token_telegram
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre_cle_supabase
API_KEY_REF=votre_cle_openrouter
```

## Configuration Telegram

1. Créer un bot via @BotFather sur Telegram
2. Récupérer le token du bot
3. Configurer le webhook pour pointer vers votre serveur :

```bash
curl -X POST "https://api.telegram.org/bot<VOTRE_TOKEN>/setWebhook?url=https://votre-domaine.com/webhook"
```

## Configuration Supabase

Les tables nécessaires ont déjà été créées via migration :

- **users** : stocke les utilisateurs avec leurs crédits
- **prompts** : historique des générations d'images

Les politiques RLS (Row Level Security) sont automatiquement configurées.

## Démarrage

### Mode développement

```bash
python app.py
```

### Mode production (avec Gunicorn)

```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 4
```

## Utilisation du Bot

1. Démarrer une conversation avec votre bot sur Telegram
2. Envoyer `/start` pour s'inscrire et recevoir 3 crédits gratuits
3. Envoyer un texte descriptif pour générer une image
4. Utiliser `/credits` pour vérifier le solde de crédits

## Commandes disponibles

- `/start` - Inscription et message de bienvenue
- `/credits` - Afficher le nombre de crédits restants
- Tout autre texte - Générer une image à partir du prompt

## Structure du projet

```
.
├── app.py              # Application Flask principale
├── requirements.txt    # Dépendances Python
├── .env               # Variables d'environnement (non versionné)
├── .env.example       # Template des variables d'environnement
└── README.md          # Documentation
```

## Coût par génération

Chaque génération d'image coûte 1 crédit. Quand les crédits arrivent à 0, l'utilisateur ne peut plus générer d'images.

## Dépannage

Si le bot ne répond pas :

1. Vérifier que le webhook est correctement configuré
2. Vérifier les logs du serveur Flask
3. Vérifier que toutes les variables d'environnement sont correctement définies
4. Vérifier la connexion à Supabase
5. Vérifier que la clé API OpenRouter est valide

## Technologies utilisées

- **Flask** - Framework web Python
- **Supabase** - Base de données PostgreSQL hébergée
- **OpenRouter** - API pour accéder aux modèles IA (Gemini)
- **Telegram Bot API** - Interface avec Telegram

## Support

Pour toute question ou problème, vérifier les logs de l'application et les réponses de l'API.
