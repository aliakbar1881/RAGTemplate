from core.rag_base import RAGBase
from rag.generator import Generator
from rag.retriever import Retriver
import numpy as np


class RAG(RAGBase):
    def __init__(self, model_name, retriever_name, vector_path, data_path, device):
        self.model_name = model_name
        self.retriever_name = retriever_name
        self.vector_path = vector_path
        self.data_path = data_path
        self.generator = Generator(model_name)
        self.retriever = Retriver(vector_path, data_path, retriever_name, device)

    def query(self, query, top_k):
        results = self._retrieve(query, top_k)
        if results:
            data = [res.page_content.strip() for res in results]
            resp = self._generate(query, data)
        else:
            data = ["شما محتوایی بارگداری نکرده اید."]
            resp = self._generate(query, data)

        sanitized_results = []
        for res in results:
            meta = getattr(res, "metadata", {})
            if isinstance(meta, dict):
                clean_meta = {}
                for k, v in meta.items():
                    if isinstance(v, np.generic):
                        clean_meta[k] = v.item()
                    else:
                        clean_meta[k] = v
            else:
                clean_meta = {}

            sanitized_doc = {
                "page_content": res.page_content,
                "metadata": clean_meta
            }
            sanitized_results.append(sanitized_doc)

        return sanitized_results, resp

    def _generate(self, query, data):
        prompt = f"""
محتوای ارایه شده : {data}
سوال : {query}

لطفا بر اساس محتوای ارایه شده به سوال کامل و دقیق جواب بده دقت کن که بیشتر جواب تولید کنی و دقیق باشی
        """
        return self.generator.generate(prompt)

    def _retrieve(self, query, top_k):
        return self.retriever.retrieve(query, top_k)

    def update_retriever(self):
        """Retriever را با اسناد جدید در data_path دوباره بارگذاری می‌کند."""
        self.retriever.reload_documents()