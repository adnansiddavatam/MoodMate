import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load OpenAI key
load_dotenv()
client = OpenAI()

# App title
st.set_page_config(page_title="AI Mood Agent 💬", layout="centered")
st.title("🧠 AI Mood Agent")
st.caption("Talk to your friendly AI and log how you're feeling.")

# Session history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat interface
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area("You:", placeholder="Type how you're feeling...", height=100)
    submitted = st.form_submit_button("Send")

# On submit
if submitted and user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get response from OpenAI
    with st.spinner("AI is thinking..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "You're a friendly, supportive AI therapist. Respond to the user "
                    "with empathy, insights, or actionable advice. If helpful, offer useful suggestions or coping strategies."
                )},
                *st.session_state.messages
            ]
        )
        reply = response.choices[0].message.content.strip()
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Log to CSV
        log_entry = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_input,
            "ai_response": reply
        }])
        if os.path.exists("mood_log.csv"):
            log_entry.to_csv("mood_log.csv", mode="a", header=False, index=False)
        else:
            log_entry.to_csv("mood_log.csv", index=False)

# Display conversation history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**AI:** {msg['content']}")
