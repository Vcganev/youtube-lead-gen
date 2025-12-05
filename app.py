import streamlit as st
import config
from pipeline import run_pipeline
import threading
import queue

st.set_page_config(page_title="YouTube Lead Gen", page_icon="🚀", layout="wide")

st.title("🚀 YouTube Lead Generation System")

# Sidebar Configuration
st.sidebar.header("Configuration")

# Keywords
default_keywords = "\n".join(config.SEARCH_KEYWORDS)
keywords_input = st.sidebar.text_area("Search Keywords (one per line)", value=default_keywords, height=150)
keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]

# Countries
all_countries = ["US", "UK", "CA", "DE", "AU", "NZ", "IE"]
default_countries = config.ALLOWED_COUNTRIES
selected_countries = st.sidebar.multiselect("Allowed Countries", all_countries, default=default_countries)

# Subscribers
min_subs = st.sidebar.number_input("Min Subscribers", value=config.MIN_SUBSCRIBERS, step=1000)
max_subs = st.sidebar.number_input("Max Subscribers", value=config.MAX_SUBSCRIBERS, step=1000)

# Limits
max_channels = st.sidebar.number_input("Max Channels per Keyword", value=config.MAX_CHANNELS_PER_KEYWORD, min_value=1, max_value=50)

# Apify Token Override
st.sidebar.markdown("---")
apify_input = st.sidebar.text_input("Apify API Token (or Run URL)", help="Paste your API Token or the full Run URL here to override the default.")

def extract_token(input_str):
    if not input_str:
        return None
    if "token=" in input_str:
        try:
            return input_str.split("token=")[1].split("&")[0]
        except:
            return input_str
    return input_str

apify_token = extract_token(apify_input)
if apify_token:
    st.sidebar.success("✅ Token detected")

# Main Area
st.markdown("### 📊 Execution Log")
log_container = st.empty()
log_text = ""

if st.button("Start Lead Generation", type="primary"):
    if not keywords:
        st.error("Please enter at least one keyword.")
    else:
        st.info("Starting process... This may take a while.")
        
        # Prepare overrides
        overrides = {
            'keywords': keywords,
            'allowed_countries': selected_countries,
            'min_subs': min_subs,
            'max_subs': max_subs,
            'max_channels': max_channels,
            'apify_token': apify_token
        }
        
        # Callback to update UI
        def status_update(msg):
            global log_text
            log_text += msg + "\n"
            log_container.code(log_text)

        # Run pipeline
        try:
            total = run_pipeline(config_overrides=overrides, status_callback=status_update)
            st.success(f"🎉 Process Complete! Generated {total} leads.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            import traceback
            st.code(traceback.format_exc())

st.markdown("---")
st.markdown("### 📝 Recent Leads (Preview)")
st.info("Check your Google Sheet for the full list of leads.")
