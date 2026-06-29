from abc import ABC, abstractmethod
class GeneratorBase(ABC):
    @abstractmethod
    def config(self):
        pass

    @abstractmethod
    def generate(self, query, top_k, top_p, do_sample, max_length):
        pass
