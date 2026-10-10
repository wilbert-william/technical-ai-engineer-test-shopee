import os

from dotenv import load_dotenv

load_dotenv()

LANGFUSE_TRACING = os.getenv("LANGFUSE_TRACING", "false").lower() == "true"

langfuse_client = None
langfuse_handler = None

if LANGFUSE_TRACING:
    from langfuse import get_client
    from langfuse.langchain import CallbackHandler

    langfuse_client = get_client()
    langfuse_handler = CallbackHandler()


def flush_langfuse():
    if langfuse_client:
        langfuse_client.flush()