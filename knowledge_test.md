## Questions

1. Describe differences between REST API, MCP in the context of AI. 
2. How REST API, MCP, can improve the AI use case. 
3. How do you ensure that your AI agent answers correctly? 
4. Describe what can you do with Docker / Containerize environment in the context of AI 
5. How do you finetune the LLM model from raw ? 

##  Answer 

### 1. Describe differences between REST API, MCP in the context of AI.  
In the context of AI, REST API and MCP solve different problems, 
    
    - REST API is a application to application communication system, using HTTP/HTTPS interface. For AI application, REST API is not a specific tools built for AI, it mainly used for client system communication or sending receiving data. REST API can be used for AI application for AI tool calling, so developers can build some custom REST API, and AI can send or receive date based on the API provides. For AI agent development, we can give the agent access to some API like:

        GET /customers/{id}

        POST /customers/search

        POST /orders

        DELETE /orders/{id}
    
    but we still need to build an integration layer telling the agent how these API should be used.

    - MCP (Model Context Protocol) is a context communication system designed for AI model or AI agent. The interface transport for MCP is using MCP protocol with standarized interface. For AI agents applications, for tool calling using native concept of MCP. MCP server could expose 
  
        Tool:
        search_customers

        Input:
        {
        "query": string,
        "limit": integer
        }

        so, the LLM can reason like "I need information about customers and the MCP have search_customers available to call.

        The important part is, the AI application doesn't need a custom integration for every individual tool in the same way like REST APIs.

    In a nutshell, REST API is an integration system to system mechanism, MCP is an AI tools or context protocol

### 2. How REST API, MCP, can improve the AI use case. 
REST API and MCP improve AI systems in different layer, the main purpose is not to making AI smarter but it makes the AI more capable, reliable, and connected to real system. 

If we are rely on main knowledge of the AI model, the response of the AI will be very general, if we ask about "give me data about sales performance of this product", the AI will answer based on their cut off training knowledge and the answer will be very general or the LLM model could not answer it or it will hallucinate.

With REST API and or MCP, our agent can read and write data so it can gain practical purposes like better accuracy, actionability, automation, security, etc. 

The architecture of the agents more or less:
- AI agent do some planning, reasoning, decision making
- with MCP or REST API agent can connect to the internal system with tool calling
- Agent can get or write internal data, makes those connection usable as a tool ecosystem for AI Agent

### 3. How do you ensure that your AI agent answers correctly? 
In my opinion, make sure that AI agent answers correctly is the hardest part of AI system engineering. 

personally, I do several step to make sure AI agent answer correctly, at high level, it can be devided into two main parts, engineering/architecture level and observability and testing level.

at engineering or architecture level, we need to make sure that our agent designed spesifically based on our main goals. If we need to make chatbot about company document, we need to use RAG and some supporting architecture. We do not want to use voice agent architecture to build RAG agent chatbot. After we designed our agents, we need to provide some supporting tools for our agents, like blob storage, agent sandbox for executing code, etc. After that we need to make some system prompting, to explain to our AI our workflow, our context, and AI persona. 

at observability and testing level, we need to make sure that our agent answer correctly based on our provided data. first, we need to gather documents and context to feed to AI as a context. Then we need to create some question test and the answer, we can test our agents manually or we can automatically test our agents using "LLM as a judge" feature (my experience using langfuse). 

after we got the testing result, we can fix the problems, before we fixed it, we need to specified if the problem is on engineering/architecture level, or on prompting level until the result achieved.

### 4. Describe what can you do with Docker / Containerize environment in the context of AI 
Docker can be used not only to deploy AI agents, but also to provide an isolated sandbox environment, so the agents can safely execute code. This method allows the agent to execute its generated code in a controlled environment without directly accessing the host system.

The sandbox can be configured with restricted permissions, limited CPU, memory resources, network access, and file storage. This is useful for AI agents that need to execute code, process data, run calculations, as part of the workflow.

Docker also help us to build a consistent CI/CD pipeline for AI applications. we can test the same container image that will eventually be deployed to production.

### 5. How do you finetune the LLM model from raw ? 
I do not have enterprise experience in finetuning LLM yet, but I have hands on experience finetuning a pretrained LLM as personal project.

I used unsloth to finetune Google Gemma model, I obtained a pretrained model from Hugging Face. I prepared and formatted the dataset into an instruction-based format, then configured the tokenizer and training parameters.

For the finetuning, I used LoRA (Low-Rank Adaptation), which allowed me to update only a small portion of the model parameters instead of finetuning the entire model.
After training, I evaluated the finetuned model by testing its responses against the target use case and comparing them with the original pretrained model.

I used LoRA because I did not need to finetune the entire Gemma model. LoRA freeze the base model and trains small low rank adapters, reduces GPU memory and computational requirements while still allowing the model to train to my specific dataset.