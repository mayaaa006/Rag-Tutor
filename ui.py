import streamlit as st
import json
from storage import save_chats

def inject_custom_css():
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] div[data-testid="stButton"] button,
        section[data-testid="stSidebar"] div[data-testid="stPopover"] button {
            background: none;
            border: none;
            text-align: left;
            width: 100%;
            padding: 6px 4px;
            color: inherit;
        }
        section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover,
        section[data-testid="stSidebar"] div[data-testid="stPopover"] button:hover {
            background-color: rgba(255,255,255,0.08);
            cursor: pointer;
        }
        /* --- Primary Button Override (Log Out) --- */
        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
            background-color: #DC9F85 !important;
            color: #181818 !important;
            border: 1px solid #66473B !important;
            border-radius: 4px !important;
            font-weight: 1000 !important;
            text-align: center !important; /* Overrides the left-alignment from your base CSS */
            transition: all 0.2s ease-in-out !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"]:hover {
            background-color: #EBDCC4 !important;
            border-color: #EBDCC4 !important;
            cursor: pointer !important;
        }
    </style>
    """, unsafe_allow_html=True)

def copy_button(text):
    safe_text = json.dumps(text)
    # Replaced components.html with st.html and removed the height keyword argument
    st.html(f"""
        <div style="height: 60px;">
            <button style="background: none; border: none; padding: 0; cursor: pointer;" onclick='navigator.clipboard.writeText({safe_text})'>📋</button>
        </div>
    """)

def render_sidebar(user_email):
    inject_custom_css()
    
    
    # --- File Upload ---
    uploaded_files = st.sidebar.file_uploader(
        "Upload PDFs or DOCX files (max 6)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files and len(uploaded_files) > 6:
        st.sidebar.error("You can upload a maximum of 6 documents. Please remove some.")
        uploaded_files = uploaded_files[:6]

    st.sidebar.divider() 
    
    # --- RAG Settings ---
    response_style = st.sidebar.selectbox(
        "How should I answer?",
        ["Concise answer", "Detailed notes", "Explain in simple language", "Expand with related context"]
    )
    custom_instructions = st.sidebar.text_input("Anything specific? (optional)")
    
    st.sidebar.divider() 

    # --- Init chat history ---
    if "chats" not in st.session_state:
        st.session_state.chats = {"Chat 1": []}
    if "active_chat" not in st.session_state:
        st.session_state.active_chat = "Chat 1"

    # --- Chat Management ---
    if st.sidebar.button("➕ New chat"):
        new_chat_name = f"Chat {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_chat_name] = []
        st.session_state.active_chat = new_chat_name
        save_chats(user_email, st.session_state.chats)

    st.sidebar.write("Your chats")
    
    # Use list() to avoid dictionary size changing during iteration
    for name in list(st.session_state.chats.keys()):
        col1, col2 = st.sidebar.columns([5, 1])
        with col1:
            label = f"● {name}" if name == st.session_state.active_chat else name
            if st.button(label, key=f"select_{name}"):
                st.session_state.active_chat = name
                st.rerun()
        with col2:
            with st.popover("⋮"):
                new_name = st.text_input("Rename", value=name, key=f"rename_{name}")
                if st.button("Save", key=f"save_{name}"):
                    if new_name and new_name != name:
                        st.session_state.chats[new_name] = st.session_state.chats.pop(name)
                        if st.session_state.active_chat == name:
                            st.session_state.active_chat = new_name
                        save_chats(user_email, st.session_state.chats)
                        st.rerun()
                if st.button("Delete", key=f"delete_{name}"):
                    del st.session_state.chats[name]
                    if st.session_state.active_chat == name:
                        st.session_state.active_chat = list(st.session_state.chats.keys())[0] if st.session_state.chats else None
                    save_chats(user_email, st.session_state.chats)
                    save_chats(user_email, st.session_state.chats)
                    st.rerun()

    if st.sidebar.button("Clear chat"):
        if st.session_state.active_chat in st.session_state.chats:
            st.session_state.chats[st.session_state.active_chat] = []
            st.rerun()

    return uploaded_files, response_style, custom_instructions