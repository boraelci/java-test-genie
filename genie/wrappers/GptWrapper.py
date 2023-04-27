import openai
import os
import tiktoken


class GptWrapper:
    def __init__(self, system_prompt_path):
        with open(system_prompt_path, "r") as f:
            self.system_prompt = f.read()

    def query(self, message):
        openai.api_key = os.environ["OPENAI_API_KEY"]
        # model = "gpt-4-0314"
        model = "gpt-3.5-turbo-0301"
        input_token_count = self.get_input_token_count(model, message)
        max_tokens = min(2048, 3900 - input_token_count)
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message},
            ],
            max_tokens=max_tokens,
        )
        content = response["choices"][0]["message"]["content"]
        return content

    def get_input_token_count(self, model, input):
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(input))