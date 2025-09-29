from src.core.retriver_base import RetriverBase
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List, Dict, Any
import os


class Retriver(RetriverBase):
    def __init__(self, vector_path, data_path, retriever_name, device):
        self.vector_path = vector_path
        self.data_path = data_path
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=retriever_name,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True}
        )
        self.vectorstore = self.load_vectorstore(self.embedding_model, self.vector_path)
        if self.vectorstore is None:
            documents = self.load_documents(data_path)
            chunks = self.split_documents(documents)
            if chunks:
                self.vectorstore = self.create_retriever(chunks, self.embedding_model)
                self.save_vectorstore(self.vectorstore, self.vector_path)

    def retrieve(self, query, top_k=10):
        if self.vectorstore:
            docs_and_scores = self.vectorstore.similarity_search_with_score(query, k=top_k)
            for doc, score in docs_and_scores:
                doc.metadata["score"] = float(score)
            return [doc for doc, _ in docs_and_scores]
        else:
            return []

    def load_documents(self, data_dir="./data"):
        pdf_loader = DirectoryLoader(data_dir, glob="*.pdf", loader_cls=PyPDFLoader)
        txt_loader = DirectoryLoader(data_dir, glob="*.txt", loader_cls=TextLoader)
        pdf_docs = pdf_loader.load()
        txt_docs = txt_loader.load()
        all_docs = pdf_docs + txt_docs
        return all_docs

    def split_documents(self, documents, chunk_size=1000, chunk_overlap=200):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        return chunks

    def create_retriever(self, documents, embedding_model):
        vectorstore = FAISS.from_documents(documents, embedding_model)
        return vectorstore

    def save_vectorstore(self, vectorstore, path="./faiss_index"):
        vectorstore.save_local(path)

    def load_vectorstore(self, embedding_model, path="./faiss_index"):
        if os.path.exists(os.path.join(path, "index.faiss")):
            vectorstore = FAISS.load_local(path, embedding_model, allow_dangerous_deserialization=True)
            return vectorstore
        else:
            return None

    def reload_documents(self):
        """
        تمام اسناد موجود در self.data_path را دوباره بارگذاری کرده،
        vectorstore را بازسازی و ذخیره می‌کند.
        """
        print("🔄 Reloading documents and rebuilding vectorstore...")
        documents = self.load_documents(self.data_path)
        chunks = self.split_documents(documents)
        if chunks:
            self.vectorstore = self.create_retriever(chunks, self.embedding_model)
            self.save_vectorstore(self.vectorstore, self.vector_path)
        else:
            self.vectorstore = None
            print("⚠️ No documents found to reload.")