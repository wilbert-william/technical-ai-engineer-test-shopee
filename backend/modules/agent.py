from datetime import datetime
from zoneinfo import ZoneInfo

from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk

from backend.utils import llm, prompt
from backend.modules.vector_db import VectorDB
from backend.utils.checkpointer import checkpointer
from backend.utils.langfuse import LANGFUSE_TRACING, langfuse_handler


class Agents:
    def __init__(self):
        self.llm = llm.load_llm
        self.load_vector_db = VectorDB()

    def rag_tools(self, text: str, top_k: int = 3) -> list[dict]:
        """Find uploaded receipt records that are relevant to a natural-language query.

        Call this tool for questions about the user's receipts, merchants, items,
        purchase dates, or expenses. Make the query specific enough to include
        names, date ranges, or item terms mentioned by the user. The result for
        each match includes structured fields (merchant_name, date, items,
        quantity, unit_price, total) and the raw OCR `text`. Use structured fields
        for facts and calculations; consult raw text only as supporting context
        when a structured value is missing or unclear. Results are ranked by
        semantic relevance, so inspect each returned payload before answering.

        Args:
            text: Natural-language description of the receipt information to find.
            top_k: Maximum number of relevant receipt records to return (default 3).
        """
        return self.load_vector_db.qdrant_retrieve(
            text=text,
            limit=top_k,
        )

    def ai_agent(self, user_input: str, session_id: str):
        current_datetime = datetime.now(ZoneInfo("Asia/Jakarta")).isoformat(
            timespec="seconds"
        )
        agent = create_agent(
            model=self.llm,
            system_prompt=prompt.system_prompt.format(
                current_datetime=current_datetime
            ),
            tools=[self.rag_tools],
            checkpointer=checkpointer,
        )

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

        for chunk, _ in agent.stream(
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
