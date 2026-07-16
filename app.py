from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import json
import streamlit.components.v1 as components

def copy_button(text):
    safe_text = json.dumps(text)
    components.html(f"""
        <button style="background: none; border: none; padding: 0; cursor: pointer;"onclick='navigator.clipboard.writeText({safe_text})'>📋</button>
    """, height=60)


st.title("RAG Tutor - Session State Test")

# --- Sidebar: file upload ---
uploaded_file = st.sidebar.file_uploader("Upload a PDF or DOCX", type=["pdf", "docx"])

response_style = st.sidebar.selectbox(
    "How should I answer?",
    ["Concise answer", "Detailed notes", "Explain in simple language", "Expand with related context"]
)
custom_instructions = st.sidebar.text_input("Anything specific? (optional)")
st.write(f"Style: {response_style}, Custom: {custom_instructions}")

# --- Init chat history (once) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Process PDF (once per uploaded file) ---
if uploaded_file is not None:
    if "vectorstore" not in st.session_state:
        if uploaded_file.name.endswith(".pdf"):
            file_path = "uploaded.pdf"
        elif uploaded_file.name.endswith(".docx"):
            file_path = "uploaded.docx"

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        if uploaded_file.name.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader =  Docx2txtLoader(file_path)# which loader for docx?

        pages = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(pages)

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vectorstore = FAISS.from_documents(chunks, embeddings)

        st.session_state.vectorstore = vectorstore
        st.write("PDF processed and ready!")

# --- Show past conversation history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- Chat input ---
user_question = st.chat_input("Ask something about your files...")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                relevant_chunks = st.session_state.vectorstore.similarity_search(user_question, k=4)
                context = "\n\n".join(chunk.page_content for chunk in relevant_chunks)

                model = ChatGroq(model="llama-3.3-70b-versatile")
                prompt = f"""Answer the question using only the following context. If the answer isn't in the context, say you don't know.

Response style: {response_style}
Additional instructions: {custom_instructions if custom_instructions else "None"}

Context: {context}

Question: {user_question}
"""

                result = model.invoke(prompt)
                if isinstance(result.content, str):
                    answer = result.content
                else:
                    answer = "".join(block["text"] for block in result.content if block.get("type") == "text")
            except Exception as e:
                answer = None
                st.error("Something went wrong while generating the answer. Please try again.")

        if answer:
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            copy_button(answer)
            


