from src.core.generator_base import GeneratorBase
from src.utils.config import Config
from openai import OpenAI


class Generator(GeneratorBase):
    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name
        self.model = self.config(model_name)

    def generate(self, query, top_k=None, top_p=None, do_sample=None, max_length=None):
        response = self.model.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": query},
            ],
            stream=False
        )
        return response.choices[0].message.content

    def config(self, model_name):
        return OpenAI(api_key=Config.API_KEY, base_url='https://api.avalai.ir/v1')


if __name__ == "__main__":
    generator = Generator('deepseek-v3.1')
    print(generator.generate("hi how are you?"))