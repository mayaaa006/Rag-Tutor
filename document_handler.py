import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import time

def process_documents(uploaded_files):
    if not uploaded_files:
        return None

    current_names = [f.name for f in uploaded_files]

    if "vectorstore" not in st.session_state or st.session_state.get("processed_files") != current_names:
        if "last_processed_time" not in st.session_state:
            st.session_state.last_processed_time = 0

        COOLDOWN_SECONDS = 30
        time_since_last = time.time() - st.session_state.last_processed_time

        if time_since_last < COOLDOWN_SECONDS:
            wait_time = int(COOLDOWN_SECONDS - time_since_last)
            st.sidebar.warning(f"Please wait {wait_time}s before processing new documents.")
            return st.session_state.get("vectorstore")  # keep using the old one meanwhile

        all_chunks = []
        save_dir = "../files"
        os.makedirs(save_dir, exist_ok=True)

        for file in uploaded_files:
            file_path = f"{save_dir}/{file.name}"
            with open(file_path, "wb") as f:
                f.write(file.getvalue())

            if file.name.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            else:
                loader = Docx2txtLoader(file_path)

            pages = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            chunks = text_splitter.split_documents(pages)
            all_chunks.extend(chunks)

        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
            vectorstore = FAISS.from_documents(all_chunks, embeddings)
            st.session_state.vectorstore = vectorstore
            st.session_state.processed_files = current_names
            st.session_state.last_processed_time = time.time()
            return vectorstore
        except Exception as e:
            st.session_state.last_processed_time = time.time()
            return None

    return st.session_state.vectorstore