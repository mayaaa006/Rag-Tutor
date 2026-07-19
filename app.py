import streamlit as st
import time
from dotenv import load_dotenv

# Import our custom modules
from ui import render_sidebar, copy_button
from document_handler import process_documents
from llm_handler import generate_answer

# Load environment variables
load_dotenv()

st.title("NotePilot - AI powered personalized notes.⭐")

# --- 1. Render Sidebar & Get User Inputs ---
uploaded_files, response_style, custom_instructions = render_sidebar()

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

    # Append and show user question
    messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.write(user_question)

    # Generate and show assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = generate_answer(user_question, vectorstore, response_style, custom_instructions)
            
        if answer:
            st.write(answer)
            messages.append({"role": "assistant", "content": answer})
            copy_button(answer)