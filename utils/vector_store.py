import chromadb
import re
import httpx
from openai import OpenAI


API_KEY = "learner030"
BASE_URL = "https://keygateway.arshnivlabs.com/v1"
MODEL = "gpt-4o-mini"


class VectorStore:
    def __init__(self):
        self.client = chromadb.EphemeralClient()
        self.oai = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
            http_client=httpx.Client(verify=False),
        )
        self.collection = self.client.get_or_create_collection("product_insights")
        self._populated = False

    def _chunk_text(self, text: str, chunk_size: int = 400) -> list:
        sentences = re.split(r"(?<=[.!\n])\s+", text)
        chunks, current = [], ""
        for s in sentences:
            if len(current) + len(s) < chunk_size:
                current += " " + s
            else:
                if current:
                    chunks.append(current.strip())
                current = s
        if current:
            chunks.append(current.strip())
        return chunks

    def populate(self, results: dict, data_context: str):
        if self._populated:
            return
        docs, ids, metas = [], [], []
        all_text = {"data_summary": data_context, **results}
        idx = 0
        for section, content in all_text.items():
            for chunk in self._chunk_text(str(content)):
                docs.append(chunk)
                ids.append(f"{section}_{idx}")
                metas.append({"section": section})
                idx += 1
        if docs:
            self.collection.add(documents=docs, ids=ids, metadatas=metas)
        self._populated = True

    def query(self, question: str, n_results: int = 4) -> str:
        results = self.collection.query(query_texts=[question], n_results=n_results)
        if results and results["documents"]:
            return "\n\n".join(results["documents"][0])
        return ""

    def chat(self, question: str) -> str:
        context = self.query(question)
        response = self.oai.chat.completions.create(
            model=MODEL,
            max_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Product Strategy Assistant. Answer questions based on the "
                        "provided business analysis context. Be concise and insightful."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                },
            ],
        )
        return response.choices[0].message.content
