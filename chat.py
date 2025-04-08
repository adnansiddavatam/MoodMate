import streamlit as st
from openai import OpenAI
import os
import pandas as pd
from datetime import datetime
import time
from dotenv import load_dotenv
import webbrowser

# Load environment variables
load_dotenv()
client = OpenAI()

# Streamlit page config
st.set_page_config(page_title="MoodMate 💬", layout="centered")

# Custom Google Chrome path (edit if different on your system)
CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(CHROME_PATH))

# Set up logging
LOG_FILE = "mood_log.csv"

# UI title
st.title("🧠 MoodMate")
st.markdown("A friendly AI companion here to support you. Talk about your feelings, and I’ll listen, support, and help if I can.")

st.divider()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Detect if user input may require a web search
def should_search_web(text):
    triggers = ["where can i", "any resources", "find help", "support group", "therapist", "counselor", "how do i get help", "near me", "in calgary"]
    return any(phrase in text.lower() for phrase in triggers)

# Open Chrome with a search
def open_chrome_search(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.get('chrome').open(search_url)

# Chat form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area("💬 What's on your mind?", height=100, placeholder="I've been feeling really stressed out lately...")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Add user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Build prompt for GPT
    with st.spinner("MoodMate is thinking..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "You're MoodMate, an empathetic AI who helps users understand and talk about their emotions. "
                    "Offer warm support, insight, and if they mention needing help or info, offer to look it up online."
                )},
                *st.session_state.messages
            ]
        )

        reply = response.choices[0].message.content.strip()

        # Typing effect
        response_container = st.empty()
        typed = ""
        for char in reply:
            typed += char
            response_container.markdown(f"""
            <div style='background-color:#f8d7da; padding:10px; border-radius:10px; margin-bottom:10px'>
                <strong>MoodMate:</strong> {typed}
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.015)

        # Save full message
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Log the chat to CSV
        df = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_input,
            "ai_response": reply
        }])
        if os.path.exists(LOG_FILE):
            df.to_csv(LOG_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(LOG_FILE, index=False)

        # Ask to search web if appropriate
        if should_search_web(user_input):
            st.markdown("🔎 It sounds like you might be looking for real-world resources.")
            if st.button("Search in Chrome"):
                open_chrome_search(user_input)

# Display past messages
st.markdown("## 🗨️ Your Conversation")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style='background-color:#d1ecf1; padding:10px; border-radius:10px; margin-bottom:10px; text-align:right'>
            <strong>You:</strong> {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color:#f8d7da; padding:10px; border-radius:10px; margin-bottom:10px'>
            <strong>MoodMate:</strong> {msg["content"]}
        </div>
        """, unsafe_allow_html=True)

# Show mood history
with st.expander("📈 View Mood Log"):
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.info("No mood history available yet.")
