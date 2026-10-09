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

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            }
        )

        return result["messages"][-1].content