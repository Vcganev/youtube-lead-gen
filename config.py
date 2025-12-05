import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_env(key, default=None):
    """Helper to get env var from os or streamlit secrets."""
    value = os.getenv(key)
    if value:
        return value
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    return default

# API Keys
OPENAI_API_KEY = get_env("OPENAI_API_KEY")
APIFY_API_TOKEN = get_env("APIFY_API_TOKEN")
YOUTUBE_API_KEY = get_env("YOUTUBE_API_KEY")
SUPABASE_URL = get_env("SUPABASE_URL")
SUPABASE_KEY = get_env("SUPABASE_KEY")

# Debug Logging
print("--- CONFIG DEBUG ---")
print(f"OPENAI_API_KEY present: {bool(OPENAI_API_KEY)}")
print(f"SUPABASE_URL present: {bool(SUPABASE_URL)}")
if hasattr(st, "secrets"):
    print(f"Secrets keys: {list(st.secrets.keys())}")
else:
    print("st.secrets not available")
print("--------------------")

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE = get_env("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEET_ID = get_env("GOOGLE_SHEET_ID")
GOOGLE_SHEET_TAB_NAME = get_env("GOOGLE_SHEET_TAB_NAME", "Instantly")
INSTANTLY_HEADERS = [
    "name",             # A
    "email",            # B
    "YouTube handle",   # C
    "about link",       # D
    "transcript",       # E
    "Loom code",        # F
    "Loom URL",         # G
    "Spacer H",         # H
    "channel name",     # I
    "Spacer J",         # J
    "channel ID",       # K
    "product",          # L
    "product name"      # M
]

# Configuration
SEARCH_KEYWORDS = [
    "amazon fba",
    "etsy coaching",
    "shopify dropshipping",
    "digital marketing agency",
    "AI automation agency"
]

ALLOWED_COUNTRIES = ["US", "UK", "CA", "DE", "AU"]

MIN_SUBSCRIBERS = 1000
MAX_SUBSCRIBERS = 500000

MAX_CHANNELS_PER_KEYWORD = 10

# Apify Actor
APIFY_ACTOR_ID = "exporter24~youtube-email-scraper" 
# Note: The user provided a full run URL, but we might use the client or just the requests. 
# The URL provided: https://api.apify.com/v2/acts/exporter24~youtube-email-scraper/run-sync-get-dataset-items?token=...
# This suggests we can just hit this endpoint with the input.
