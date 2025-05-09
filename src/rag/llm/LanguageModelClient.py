from litellm import completion


class LanguageModelClient:
    """
    Client to interact with different Language Large Models (LLMs) via their APIs.
    """

    def __init__(self, api_key: str):
        """
        Initialize the LanguageModelClient with the given API key.

        :param api_key: The API key for authenticating with the llm providers.
        """
        self.api_key = api_key

    def get_answers_openai(self, prompt, model, max_tokens, temperature):
        """
        Sends a request to the OpenAI API with given parameters and retrieves the response.

        :param prompt: The prompt text to send to the OpenAI model.
        :param model: The identifier of the OpenAI model to use for the completion request.
        :param max_tokens: The maximum number of tokens to generate in the response.
        :param temperature: The temperature setting to control the randomness of the response.
        :return: The response from the OpenAI API.
        """
        # Assuming that `completion` is a function that sends requests to the OpenAI API
        response = completion(
            model=model,
            messages=[{"content": prompt, "role": "user"}],
            max_tokens=max_tokens,
            n=1,
            temperature=temperature,
            api_key=self.api_key
        )
        message = response['choices'][0]['message']['content']
        return message

    # Будущие методы для других языковых моделей можно добавить сюда:
    # def get_answers_other_llm(self, prompt, model_details):
    #     pass
