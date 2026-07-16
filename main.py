from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
load_dotenv()

print("---------- START=> -----------")
loader = PyPDFLoader("test.pdf")
pages = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(pages)

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
faiss = FAISS.from_documents(chunks, embeddings)

question = input("Write you question: ")
relevant_chunks = faiss.similarity_search(question, k = 4)
context = "\n\n".join(chunk.page_content for chunk in relevant_chunks)

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash")
result = model.invoke(f"Answer the question using only the following context. If the answer isn't in the context, say you don't know. Context: {context} Question:{question}")

if isinstance(result.content, str):
    print(result.content)
else:
    for block in result.content:
        if block.get("type") == "text":
            print(block["text"])
