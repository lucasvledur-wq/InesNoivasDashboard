"""
Generate a Google Ads API refresh token via OAuth2 flow.

Steps:
1. Create OAuth2 credentials in Google Cloud Console (Desktop app type)
2. Enable the Google Ads API
3. Run this script and follow the instructions
"""

import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/adwords"]

CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("Erro: defina GOOGLE_ADS_CLIENT_ID e GOOGLE_ADS_CLIENT_SECRET no .env")
    exit(1)

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
credentials = flow.run_local_server(port=8080)

print("\n" + "=" * 60)
print("REFRESH TOKEN (copie para o .env):")
print("=" * 60)
print(credentials.refresh_token)
print("=" * 60)
