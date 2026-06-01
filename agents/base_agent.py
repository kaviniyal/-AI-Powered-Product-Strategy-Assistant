from openai import OpenAI
import httpx


MODEL = "gpt-4o-mini"
API_KEY = "learner030"
BASE_URL = "https://keygateway.arshnivlabs.com/v1"


def _make_client():
    return OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        http_client=httpx.Client(verify=False),
    )


class BaseAgent:
    def __init__(self, name: str, role: str):
        self.client = _make_client()
        self.name = name
        self.role = role

    def run(self, user_prompt: str, context: str = "") -> str:
        content = f"{context}\n\n{user_prompt}" if context else user_prompt
        response = self.client.chat.completions.create(
            model=MODEL,
            max_tokens=500,
            messages=[
                {"role": "system", "content": self.role},
                {"role": "user", "content": content},
            ],
        )
        return response.choices[0].message.content
