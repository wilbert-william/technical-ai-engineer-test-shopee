# technical-ai-engineer-test-shopee

Technical test for shopee AI engineer position

## Engineering Knowledge AI Agent Test

The results of the Engineering Knowledge AI Agent Test are available in the [Knowledge Test](./1.knowledge_test/knowledge_test.md).

## Coding Test

### Running with the full dataset (for question no 1 and 2)

Please Place the provided datasets in the `data/` directory:

```
data/
├── customer-100000.csv
└── customers-2000000.csv
```

#### **1. Please parse this csv, get the insight of the data customer-100000.csv**

Please check [customers-small](./2.coding_test/1.customers-small.ipynb) notebook for the full answer

#### **2. Please parse large CSV, customers-2000000.csv and keep the memory low.**

Please check [customers-large](./2.coding_test/2.customers-large.ipynb) notebook for the full answer

#### **3. Explain how it's different from splitting the small vs large files.**

Please check [coding_test_no3.md](./2.coding_test/3.coding_test_no3.md) for the full answer

#### **4. Deploy the vector DB on your own, and implement the `vector cosine similarity` without using a high level library.** 

Please check [docker-compose.yml](./docker-compose.yml) to see how vector DB is deployed, I'm using qdrant.
Please check [cosine-similarity.ipynb](./2.coding_test/4.cosine-similarity.ipynb) for the answer how I implement vector cosine similarity without high level library, I'm using numpy

#### **5. Create a platform with UI**

### Application workflow (for question no 5)
![workflow](assets/workflow_diagram.jpg)

**Tech Stack**
- **Frontend:** Streamlit
- **Backend API:** FastAPI
- **OCR:** PaddleOCR
- **Vector Database:** Qdrant
- **AI Agent Framework:** LangChain
- **LLM:** gpt-6-luna
- **Observability:** Langfuse
- **Containerization:** Docker
- **Container Orchestration:** Docker Compose
- **CI/CD:** GitHub Actions


## How to run the app
