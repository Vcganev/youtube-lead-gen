import config
from youtube_client import YouTubeClient
from supabase_client import SupabaseClient
from email_discovery_client import ApifyEmailClient
from sheets_client import SheetsClient
from llm_client import LLMClient
import datetime
import time

def run_pipeline(config_overrides=None, status_callback=None):
    """
    Runs the lead generation pipeline.
    
    Args:
        config_overrides (dict): Optional dictionary to override config settings.
        status_callback (func): Optional function to handle log messages.
    """
    
    def log(message):
        print(message)
        if status_callback:
            status_callback(message)

    log("🚀 Starting YouTube Lead Gen System...")
    
    # Apply overrides
    keywords = config.SEARCH_KEYWORDS
    allowed_countries = config.ALLOWED_COUNTRIES
    min_subs = config.MIN_SUBSCRIBERS
    max_subs = config.MAX_SUBSCRIBERS
    max_channels = config.MAX_CHANNELS_PER_KEYWORD
    
    if config_overrides:
        keywords = config_overrides.get('keywords', keywords)
        allowed_countries = config_overrides.get('allowed_countries', allowed_countries)
        min_subs = config_overrides.get('min_subs', min_subs)
        max_subs = config_overrides.get('max_subs', max_subs)
        max_channels = config_overrides.get('max_channels', max_channels)

    # Initialize Clients
    youtube = YouTubeClient()
    supabase = SupabaseClient()
    
    apify_token = None
    if config_overrides:
        apify_token = config_overrides.get('apify_token')
        
    apify = ApifyEmailClient(token=apify_token)
    sheets = SheetsClient()
    llm = LLMClient()
    
    total_leads_generated = 0
    
    for keyword in keywords:
        log(f"\n🔎 Searching for keyword: {keyword}")
        
        # 1. Search Channels
        log(f"   🔎 Searching with limit: {max_channels}")
        channel_ids = youtube.search_channels(keyword, max_results=max_channels)
        log(f"   Found {len(channel_ids)} channels.")
        
        if not channel_ids:
            continue
            
        # 2. Get Channel Details
        channels_data = youtube.get_channel_details(channel_ids)
        
        for channel in channels_data:
            channel_id = channel['id']
            title = channel['snippet']['title']
            log(f"   👉 Processing: {title} ({channel_id})")
            
            # 3. Filter by Country
            country = channel['snippet'].get('country')
            if country not in allowed_countries:
                log(f"      ❌ Skipped: Country {country} not in allowed list.")
                continue
                
            # 4. Filter by Subscribers
            stats = channel['statistics']
            subs = int(stats.get('subscriberCount', 0))
            if not (min_subs <= subs <= max_subs):
                log(f"      ❌ Skipped: Subscribers {subs} out of range.")
                continue
                
            # 5. Duplicate Check
            if supabase.check_channel_exists(channel_id):
                log(f"      ❌ Skipped: Already in database.")
                continue
                
            # 6. Email Discovery
            # Always use channel ID for the URL as requested
            channel_url = f"https://www.youtube.com/channel/{channel_id}"
                
            log(f"      🕵️ Scraping emails from {channel_url}...")
            emails = apify.get_emails(channel_url)
            
            # Filter emails
            valid_emails = []
            ignored_keywords = ['support', 'info', 'contact', 'help', 'sales']
            for email in emails:
                if not any(k in email.lower() for k in ignored_keywords):
                    valid_emails.append(email)
            
            if not valid_emails:
                log(f"      ❌ Skipped: No valid personal emails found (Found: {emails}).")
                continue
                
            primary_email = valid_emails[0]
            log(f"      ✅ Found email: {primary_email}")
            
            # 7. Enrichment (LLM)
            log(f"      🧠 Enriching with AI...")
            latest_video = youtube.get_latest_video(channel_id)
            last_video_title = latest_video['title'] if latest_video else "No video found"
            
            enrichment = llm.enrich_lead(channel['snippet'], last_video_title)
            
            # Process contact name (First Name only)
            raw_name = enrichment.get('contact_name', 'Unknown')
            if raw_name and raw_name.lower() != 'unknown':
                contact_name = raw_name.split()[0] # First name
            else:
                contact_name = "there"
                
            # Process product name
            product_name = enrichment.get('product_name')
            if not product_name or product_name.lower() == 'unknown':
                product_name = "offer"

            # 8. Prepare Lead Data
            lead_data = {
                "timestamp": str(datetime.datetime.now()),
                "source_keyword": keyword,
                "email": primary_email,
                "email_source": "Apify",
                "all_emails": valid_emails,
                "channel_id": channel_id,
                "channel_url": channel_url,
                "channel_title": title,
                "channel_description_short": enrichment.get('channel_description_short'),
                "country": country,
                "subscriber_count": subs,
                "view_count": stats.get('viewCount'),
                "video_count": stats.get('videoCount'),
                "contact_name": contact_name,
                "contact_name_confidence": enrichment.get('contact_name_confidence'),
                "product_type": enrichment.get('product_type'),
                "product_description": enrichment.get('product_description'),
                "product_name": product_name,
                "website_url": "",
                "last_video_title": last_video_title,
                "last_video_paraphrase": enrichment.get('last_video_paraphrase'),
                "email_status": "Found",
                "notes": "",
                "supabase_id": ""
            }
            
            # 9. Save to Storage
            if supabase.save_lead(lead_data):
                log(f"      💾 Saved to Supabase.")
            else:
                log(f"      ⚠️ Failed to save to Supabase.")
                
            if sheets.append_lead(lead_data):
                log(f"      📝 Saved to Google Sheet.")
            else:
                log(f"      ⚠️ Failed to save to Google Sheet.")
                
            total_leads_generated += 1
            
    log(f"\n🎉 Run Complete. Total Leads Generated: {total_leads_generated}")
    return total_leads_generated

if __name__ == "__main__":
    run_pipeline()
