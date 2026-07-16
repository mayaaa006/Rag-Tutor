import streamlit as st

st.title("RAG Tutor - Session State Test")

input = st.chat_input("Type something...")

uploaded_file = st.sidebar.file_uploader("Upload a PDF", type="pdf")

if "messages" not in st.session_state:
    st.session_state.messages = []

if uploaded_file is not None:
    st.write(f"Received file: {uploaded_file.name}")



if input:
    st.session_state.messages.append({
        "role":"user",
        "content":input
    })
    st.session_state.messages.append({
    "role": "assistant",
    "content": "This is a placeholder answer"
})
    

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


