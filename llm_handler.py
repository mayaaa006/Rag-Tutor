import streamlit as st
from langchain_groq import ChatGroq

def generate_answer(user_question, vectorstore, response_style, custom_instructions):
    try:
        relevant_chunks = vectorstore.similarity_search(user_question, k=4)
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
            return result.content
        else:
            return "".join(block["text"] for block in result.content if block.get("type") == "text")
            
    except Exception as e:
        st.error(f"Something went wrong while generating the answer: {e}")
        return None