from langchain.agents import create_agent

from backend.utils import llm, prompt

class Agents:
    def __init__(self):
        self.llm = llm.load_llm
        self.system_prompt = prompt.system_prompt

    def ai_agent(self, user_input: str):
        agent = create_agent(
            model=self.llm,
            system_prompt=self.system_prompt,
            
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