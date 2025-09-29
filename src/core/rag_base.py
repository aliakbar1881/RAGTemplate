from abc import ABC, abstractmethod


class RAGBase(ABC):
    @abstractmethod
    def _retrieve(self, query):
        pass
    
    @abstractmethod
    def _generate(self, query, data):
        pass

    @abstractmethod
    def query(self):
        pass
