from openai import OpenAI
import config
import json

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def enrich_lead(self, channel_data, video_title):
        """
        Uses LLM to extract name, product info, and paraphrase video title.
        """
        
        prompt = f"""
        You are an expert lead researcher. Analyze the following YouTube channel data and the latest video title.
        
        Channel Title: {channel_data.get('title')}
        Description: {channel_data.get('description')}
        Custom URL: {channel_data.get('customUrl')}
        Latest Video Title: {video_title}
        
        Task 1: Extract the likely real name of the creator. If unknown, guess based on channel name or return "Unknown".
        Task 2: Detect the product or offer they sell. Choose from: coaching, consulting, agency, online course, community, software, physical product, mixed, unknown. Also provide a short description.
        Task 3: Extract the main topic of the video to complete the sentence 'got your video about...'. Example: 'AI agents' or 'your trip to Japan'. Do not include 'I watched...' or the full sentence.
        Task 4: Summarize the channel description into a short blurb.
        Task 5: Extract a short 'product name' that fits into the sentence: 'I also checked out your [Product name], good stuff.' If the product is complex or mixed, just return 'offer'.
        
        Return JSON format:
        {{
            "contact_name": "Name",
            "contact_name_confidence": "High/Medium/Low",
            "product_type": "Type",
            "product_description": "Description",
            "product_name": "Product Name",
            "last_video_paraphrase": "Paraphrase",
            "channel_description_short": "Summary"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM error: {e}")
            return {
                "contact_name": "Unknown",
                "contact_name_confidence": "Low",
                "product_type": "unknown",
                "product_description": "",
                "last_video_paraphrase": "",
                "channel_description_short": ""
            }
