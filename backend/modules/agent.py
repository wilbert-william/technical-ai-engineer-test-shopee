from langchain.agents import create_agent

from backend.utils import llm, prompt
from backend.modules.vector_db import VectorDB



class Agents:
    def __init__(self):
        self.llm = llm.load_llm
        self.system_prompt = prompt.system_prompt
        self.load_vector_db = VectorDB()

    def rag_tools(self, text, top_k):
        """AI RAG tools to retrieve vector db,
        input:
            text: string, initial input for vector db query
            top_k: integer, how many data will be retrieve, with initial value 3, you can add more limit to this input
        """
        data = self.load_vector_db.qdrant_retrieve(
            text = text,
            limit = top_k
        )

        return data

    def ai_agent(self, user_input: str):
        agent = create_agent(
            model=self.llm,
            system_prompt=self.system_prompt,
            tools=[self.rag_tools]
        )

        stream = agent.stream_events(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            },
            version="v3"
        )

        for message in stream.messages:
            for delta in message.text:
                yield delta