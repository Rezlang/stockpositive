import os
from pathlib import Path

from dotenv import load_dotenv
from httpx_oauth.clients.google import GoogleOAuth2


load_dotenv()

env_path = Path("../") / ".env"
load_dotenv(dotenv_path=env_path)

GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")

google_oauth_client = GoogleOAuth2(
    client_id=GOOGLE_OAUTH_CLIENT_ID,
    client_secret=GOOGLE_OAUTH_CLIENT_SECRET
)

# TODO: Apple OAuth configuration
# Apple OAuth requires:
# 1. Apple Developer Account and Service ID
# 2. Private key (.p8 file), Team ID, and Key ID
# Uncomment when credentials are available:
#
# APPLE_OAUTH_CLIENT_ID = os.getenv("APPLE_OAUTH_CLIENT_ID", "")
# APPLE_OAUTH_CLIENT_SECRET = os.getenv("APPLE_OAUTH_CLIENT_SECRET", "")
# APPLE_TEAM_ID = os.getenv("APPLE_TEAM_ID", "")
# APPLE_KEY_ID = os.getenv("APPLE_KEY_ID", "")
# APPLE_PRIVATE_KEY = os.getenv("APPLE_PRIVATE_KEY", "")
#
# from httpx_oauth.clients.apple import AppleOAuth2
# apple_oauth_client = AppleOAuth2(
#     client_id=APPLE_OAUTH_CLIENT_ID,
#     client_secret=APPLE_OAUTH_CLIENT_SECRET,
#     team_id=APPLE_TEAM_ID,
#     key_id=APPLE_KEY_ID,
#     private_key=APPLE_PRIVATE_KEY,
# )