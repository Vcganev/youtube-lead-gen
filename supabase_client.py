from supabase import create_client, Client
import config

class SupabaseClient:
    def __init__(self):
        self.url: str = config.SUPABASE_URL
        self.key: str = config.SUPABASE_KEY
        self.supabase: Client = create_client(self.url, self.key)
        self.table_name = "leads" # Assuming table name is 'leads'

    def check_channel_exists(self, channel_id):
        """
        Checks if a channel ID already exists in the database.
        """
        try:
            response = self.supabase.table(self.table_name).select("channel_id", count="exact").eq("channel_id", channel_id).execute()
            # If count is greater than 0, it exists
            # Note: The response format depends on the supabase-py version, but generally .data or .count works
            if response.data:
                return True
            return False
        except Exception as e:
            print(f"Supabase check error: {e}")
            # If error, assume it doesn't exist to be safe, or handle otherwise?
            # Better to log and maybe fail open or closed. Failsafe: return False (process it)
            return False

    def save_lead(self, lead_data):
        """
        Saves a lead to the database.
        """
        try:
            # Prepare data to match schema
            data = {
                "channel_id": lead_data.get("channel_id"),
                "primary_email": lead_data.get("email"),
                "all_emails": lead_data.get("all_emails", []), # JSON array
                "subscriber_count": lead_data.get("subscriber_count"),
                "contact_name": lead_data.get("contact_name"),
                "product_type": lead_data.get("product_type"),
                "product_description": lead_data.get("product_description"),
                "website_url": lead_data.get("website_url"),
                "last_video_title": lead_data.get("last_video_title"),
                "last_video_paraphrase": lead_data.get("last_video_paraphrase"),
                "timestamp": lead_data.get("timestamp")
            }
            
            self.supabase.table(self.table_name).insert(data).execute()
            return True
        except Exception as e:
            print(f"Supabase save error: {e}")
            return False
