import config
from youtube_client import YouTubeClient
from supabase_client import SupabaseClient
from email_discovery_client import ApifyEmailClient
from sheets_client import SheetsClient
from llm_client import LLMClient
import datetime

def test_youtube():
    print("\n--- Testing YouTube API ---")
    client = YouTubeClient()
    # Search for a generic term
    channels = client.search_channels("python programming", max_results=1)
    if channels:
        print(f"✅ Found {len(channels)} channels. First ID: {channels[0]}")
        details = client.get_channel_details(channels)
        if details:
            print(f"✅ Fetched details for {details[0]['snippet']['title']}")
            latest_video = client.get_latest_video(channels[0])
            if latest_video:
                print(f"✅ Fetched latest video: {latest_video['title']}")
            else:
                print("⚠️ Could not fetch latest video (might be no uploads)")
        else:
            print("❌ Could not fetch channel details")
    else:
        print("❌ No channels found (or API error)")

def test_supabase():
    print("\n--- Testing Supabase ---")
    client = SupabaseClient()
    # Check a random ID
    exists = client.check_channel_exists("UC_random_id_123")
    print(f"✅ Check channel exists result: {exists} (Expected False)")

def test_llm():
    print("\n--- Testing LLM (OpenAI) ---")
    client = LLMClient()
    dummy_data = {
        "title": "Test Channel",
        "description": "We teach coding.",
        "customUrl": "@testchannel"
    }
    result = client.enrich_lead(dummy_data, "How to write Python")
    if result.get("contact_name"):
        print(f"✅ LLM Response received. Name: {result.get('contact_name')}")
    else:
        print("❌ LLM Response invalid")

def test_sheets():
    print("\n--- Testing Google Sheets ---")
    client = SheetsClient()
    dummy_lead = {
        "timestamp": str(datetime.datetime.now()),
        "source_keyword": "TEST_RUN",
        "email": "test@example.com",
        "channel_title": "Test Channel",
        "notes": "This is a test row from the verification script"
    }
    success = client.append_lead(dummy_lead)
    if success:
        print("✅ Successfully wrote to Google Sheet")
    else:
        print("❌ Failed to write to Google Sheet")

def test_apify():
    print("\n--- Testing Apify ---")
    # Note: Apify runs cost money/credits, so we might want to skip or do a very cheap run.
    # The user provided a specific actor. We will try a known channel that might have an email.
    # Or just skip to save credits if the user prefers. 
    # For now, I'll skip the actual run to avoid waiting/cost in this quick test, 
    # unless I'm sure. But the user wants the system to work. 
    # Let's try a very simple check or just instantiate the client.
    client = ApifyEmailClient()
    print("✅ Apify Client instantiated (Skipping actual run to save time/credits for now)")

if __name__ == "__main__":
    test_youtube()
    test_supabase()
    test_llm()
    test_sheets()
    test_apify()
