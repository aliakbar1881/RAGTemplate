from abc import ABC, abstractmethod


class RetriverBase(ABC):
    def __init__(self, store_path):
        self.store_path = store_path

    @abstractmethod
    def retrieve(self, query, top_k):
        pass