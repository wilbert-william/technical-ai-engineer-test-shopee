from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk

from backend.utils import llm, prompt
from backend.modules.vector_db import VectorDB
from backend.utils.checkpointer import checkpointer
from backend.utils.langfuse import LANGFUSE_TRACING, langfuse_handler


class Agents:
    def __init__(self):
        self.llm = llm.load_llm
        self.system_prompt = prompt.system_prompt
        self.load_vector_db = VectorDB()
        self.agent = create_agent(
            model=self.llm,
            system_prompt=self.system_prompt,
            tools=[self.rag_tools],
            checkpointer=checkpointer
        )

    def rag_tools(self, text: str, top_k: int = 3) -> list[dict]:
        """AI RAG tools to retrieve vector db,
        input:
            text: string, initial input for vector db query
            top_k: integer, how many data will be retrieve, with initial value 3, you can add more limit to this input
        """
        return self.load_vector_db.qdrant_retrieve(
            text=text,
            limit=top_k,
        )

    def ai_agent(self, user_input: str, session_id: str):
        config = {
            "configurable": {
                "thread_id": session_id,
            },
        }

        if LANGFUSE_TRACING:
            config["callbacks"] = [langfuse_handler]
            config["metadata"] = {
                "langfuse_session_id": session_id,
                "langfuse_tags": ["food-receipt-agent"],
            }

        for chunk, _ in self.agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
            stream_mode="messages",
        ):
            if not isinstance(chunk, AIMessageChunk):
                continue

            content = chunk.content

            if isinstance(content, str):
                if content:
                    yield content
            else:
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        if block.get("text"):
                            yield block["text"]
