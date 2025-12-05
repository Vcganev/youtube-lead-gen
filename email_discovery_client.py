from apify_client import ApifyClient
import config

class ApifyEmailClient:
    def __init__(self, token=None):
        self.token = token if token else config.APIFY_API_TOKEN
        self.client = ApifyClient(self.token)
        self.actor_id = config.APIFY_ACTOR_ID

    def get_emails(self, channel_url):
        """
        Runs the Apify actor to find emails for a given channel URL.
        """
        run_input = {
            "url": channel_url,
            "maxItems": 1,
            "extendOutputFunction": """($) => {
                return {}
            }""",
            "proxy": {
                "useApifyProxy": True
            }
        }
        
        try:
            # Run the actor and wait for it to finish
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # Fetch results from the dataset
            dataset_items = self.client.dataset(run["defaultDatasetId"]).list_items().items
            
            emails = []
            for item in dataset_items:
                # Handle 'email' field
                if 'email' in item and item['email']:
                    if isinstance(item['email'], str):
                        emails.append(item['email'])
                    elif isinstance(item['email'], list):
                        emails.extend([e for e in item['email'] if isinstance(e, str)])

                # Handle 'emails' field
                if 'emails' in item and item['emails']:
                    if isinstance(item['emails'], list):
                        emails.extend([e for e in item['emails'] if isinstance(e, str)])
                    elif isinstance(item['emails'], str):
                         emails.append(item['emails'])
            
            # Deduplicate
            return list(set(emails))
            
        except Exception as e:
            print(f"Apify error: {e}")
            return []
