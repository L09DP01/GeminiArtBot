#!/usr/bin/env python3
"""
Test script to verify Supabase database connection and user operations
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Variables d'environnement manquantes!")
    print("Assurez-vous d'avoir un fichier .env avec:")
    print("- SUPABASE_URL")
    print("- SUPABASE_KEY")
    exit(1)

SUPABASE_API_URL = f"{SUPABASE_URL}/rest/v1"

def test_connection():
    """Test basic connection to Supabase"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    try:
        response = requests.get(f"{SUPABASE_API_URL}/users?limit=1", headers=headers)
        print(f"🔗 Test de connexion: {response.status_code}")
        if response.status_code == 200:
            print("✅ Connexion à Supabase réussie!")
            return True
        else:
            print(f"❌ Erreur de connexion: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_user_operations():
    """Test user creation and retrieval"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    test_user_id = 123456789  # Test user ID
    
    # Test user creation
    payload = {
        "id": test_user_id,
        "credits": 3,
        "language": "fr"
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_API_URL}/users",
            headers=headers,
            json=payload
        )
        print(f"👤 Création utilisateur: {response.status_code}")
        if response.status_code == 201:
            print("✅ Utilisateur créé avec succès!")
        elif response.status_code == 409:
            print("ℹ️ Utilisateur existe déjà (normal)")
        else:
            print(f"❌ Erreur création: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur création utilisateur: {e}")
        return False
    
    # Test user retrieval
    try:
        response = requests.get(
            f"{SUPABASE_API_URL}/users?id=eq.{test_user_id}",
            headers=headers
        )
        print(f"🔍 Récupération utilisateur: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            if users:
                print(f"✅ Utilisateur trouvé: {users[0]}")
                return True
            else:
                print("❌ Utilisateur non trouvé")
                return False
        else:
            print(f"❌ Erreur récupération: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur récupération utilisateur: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de la base de données Supabase")
    print("=" * 40)
    
    if test_connection():
        print("\n" + "=" * 40)
        test_user_operations()
    
    print("\n" + "=" * 40)
    print("📝 Instructions:")
    print("1. Créez un fichier .env avec vos clés Supabase")
    print("2. Exécutez les migrations dans Supabase")
    print("3. Vérifiez que RLS est configuré correctement")
    print("4. Redémarrez votre bot")
