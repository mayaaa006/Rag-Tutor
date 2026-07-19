import streamlit as st
import time
import base64
from dotenv import load_dotenv

# Import our custom modules
from ui import render_sidebar, copy_button
from document_handler import process_documents
from llm_handler import generate_answer
from storage import load_chats, save_chats

# Load environment variables
load_dotenv()
st.set_page_config(layout="wide")

# Login
if not st.user.is_logged_in:
    if st.query_params.get("login") == "true":
        st.login()

    # Open with UTF-8 encoding to preserve special characters
    with open("index.html", encoding="utf-8") as f:
        html_content = f.read()
    
    # Encode HTML to Base64 to safely embed it in an iframe
    b64_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    
    # Inject an iframe that perfectly covers the entire viewport 
    # This bypasses the st.components deprecation and fixes all scrolling issues
    st.markdown(
        f"""
        <style>
            header, footer {{ visibility: hidden !important; display: none !important; }}
            .stApp, .block-container {{ padding: 0 !important; margin: 0 !important; overflow: hidden !important; }}
        </style>
        <iframe src="data:text/html;base64,{b64_html}" 
                style="position:fixed; top:0; left:0; width:100vw; height:100vh; border:none; z-index:99999;">
        </iframe>
        """, 
        unsafe_allow_html=True
    )
    st.stop()

# after login check passes...
if "chats" not in st.session_state:
    st.session_state.chats = load_chats(st.user.email)
if "active_chat" not in st.session_state:
    st.session_state.active_chat = list(st.session_state.chats.keys())[0]

# LOGOUT
st.sidebar.write(f"Signed in as **{st.user.name}**")
if st.sidebar.button("Log out", type="primary"):
    st.logout()
    st.stop()

# --- Main App Begins ---

st.title("NotePilot - AI powered personalized notes.⭐")

# --- 1. Render Sidebar & Get User Inputs ---
uploaded_files, response_style, custom_instructions = render_sidebar(st.user.email)

# --- 2. Process Documents ---
vectorstore = process_documents(uploaded_files)
if uploaded_files and vectorstore is None:
    st.error("Couldn't process your documents right now — you may have hit the free-tier rate limit. Wait about a minute and try again.")
elif vectorstore is not None:
    st.session_state.vectorstore = vectorstore
    

# --- 3. Safety Check for Active Chats ---
# If all chats are deleted, prompt the user to make a new one to prevent crashing
if not st.session_state.chats or st.session_state.active_chat not in st.session_state.chats:
    st.warning("Please create a new chat from the sidebar.")
    st.stop()

# Get current messages array
messages = st.session_state.chats[st.session_state.active_chat]

# --- 4. Render Conversation History ---
for message in messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            copy_button(message["content"])

# --- 5. Handle New User Input ---
user_question = st.chat_input("Ask something about your files...")

if user_question:
    if not vectorstore:
        st.warning("Please upload documents first before asking questions.")
        st.stop()

    messages.append({"role": "user", "content": user_question})
    save_chats(st.user.email, st.session_state.chats)
    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = generate_answer(user_question, vectorstore, response_style, custom_instructions)

        if answer:
            st.write(answer)
            messages.append({"role": "assistant", "content": answer})
            save_chats(st.user.email, st.session_state.chats)
            copy_button(answer)