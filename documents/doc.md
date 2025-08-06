```markdown
# Instagram Script-Writer — Development Documentation

> **Purpose:** A full-stack Python pipeline that learns your Instagram video‐script style and generates fresh, platform-optimized content on demand.  
> **Tech stack:** Python 3.10+, OpenAI API, Pinecone (or equivalent vector DB), LangChain, Streamlit (or FastAPI), Docker, GitHub Actions, pytest.

---

## 📂 Repository Layout
```

instagram-script-writer/
├── docker/
│ ├── Dockerfile
│ └── docker-compose.yml
├── scripts/ # Raw .txt files of your historic Instagram scripts
├── src/
│ ├── **init**.py
│ ├── config.py # Environment configuration
│ ├── ingest.py # Ingest & index scripts into Pinecone
│ ├── generator.py # Retrieval-augmented generation logic
│ ├── polish.py # Two-stage “draft → polish” chain
│ ├── utils.py # QC: length checks, duplication filters
│ └── app.py # Streamlit (or FastAPI) web UI
├── tests/ # pytest test modules
│ ├── test_ingest.py
│ ├── test_generator.py
│ ├── test_polish.py
│ └── test_utils.py
├── .github/
│ └── workflows/
│ └── ci.yml # CI: lint, test, build, push Docker
├── requirements.txt
└── README.md # (this file)

````

---

## ⚙️ 1. Environment & Dependencies

1. **Python 3.10+**
2. **Virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
````

3. **Install**

   ```bash
   pip install -r requirements.txt
   ```

4. **Docker & Docker-Compose** (optional, for containerized deployment)
5. **Environment variables** (in `.env` or your CI settings):

   ```
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENV=your_pinecone_environment  # e.g. us-west1-gcp
   PINECONE_INDEX=ig-scripts
   MODEL_FINE_TUNED=your_fine_tuned_model_name
   ```

---

## 🔑 2. Configuration (`src/config.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV     = os.getenv("PINECONE_ENV", "us-west1-gcp")
PINECONE_INDEX   = os.getenv("PINECONE_INDEX", "ig-scripts")
MODEL_FINE_TUNED = os.getenv("MODEL_FINE_TUNED", "gpt-3.5-turbo-your-style")
```

- Loads secrets from environment.
- Defaults provided for Pinecone settings.

---

## 🛠️ 3. Ingestion & Indexing (`src/ingest.py`)

1. **Purpose:** Read your past scripts and embed them for retrieval.
2. **Workflow:**

   - Load all `scripts/*.txt`
   - Embed with `OpenAIEmbeddings()`
   - Upsert into Pinecone index

```python
import pinecone
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as LC_Pinecone
from config import PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX

def ingest():
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    loader = TextLoader("scripts/*.txt", encoding="utf-8")
    docs = loader.load()
    embeddings = OpenAIEmbeddings()
    LC_Pinecone.from_documents(docs, embeddings, index_name=PINECONE_INDEX)
    print(f"[✅] Ingested {len(docs)} documents into '{PINECONE_INDEX}'.")

if __name__ == "__main__":
    ingest()
```

- **Run:** `python src/ingest.py`

---

## 🤖 4. Script Generation (`src/generator.py`)

1. **Purpose:** Retrieve style-examples and generate a draft.
2. **Components:**

   - Pinecone retriever (top-3)
   - System persona message
   - Few-shot prompt template
   - OpenAI ChatCompletion

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as LC_Pinecone
import pinecone
from config import *

SYSTEM_PROMPT = """You are [Your Name]—witty, warm, and concise.
Use conversational language, short paragraphs, rhetorical questions.
Sprinkle in sensory details and end with a friendly CTA."""

PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["examples", "topic"],
    template="""
SYSTEM:
{system}

Here are 3 past Instagram scripts in my style:
{examples}

Now write a new Instagram Reel script on: "{topic}"
—include HOOK, BODY, CTA, CAPTION (≤125 chars),
VISUAL DIRECTIONS, and 5–7 HASHTAGS.
"""
)

def generate_script(topic: str) -> str:
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    db = LC_Pinecone.from_existing_index(PINECONE_INDEX, OpenAIEmbeddings())
    retriever = db.as_retriever(search_kwargs={"k": 3})
    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model=MODEL_FINE_TUNED, temperature=0.7),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": PROMPT_TEMPLATE}
    )
    return chain.run({"system": SYSTEM_PROMPT, "topic": topic})

if __name__ == "__main__":
    topic = input("Topic: ")
    print(generate_script(topic))
```

- **Run:** `python src/generator.py`

---

## ✨ 5. Two-Stage Polish (`src/polish.py`)

1. **Purpose:** Refine the draft for clarity, vividness, and voice.
2. **Second-pass model:** `gpt-4` (or whichever high-capability model you have access to).

```python
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def polish(draft: str) -> str:
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.5,
        messages=[
            {"role": "system", "content": "You are an expert copyeditor."},
            {"role": "user",   "content": "Polish this Instagram script—make it vivid, flawless, and still in the author’s voice:\n\n" + draft}
        ]
    )
    return resp.choices[0].message.content
```

- **Import and call** `polish()` after `generate_script()` in your pipeline.

---

## 🔍 6. Quality-Control Utilities (`src/utils.py`)

```python
from langchain.embeddings.openai import OpenAIEmbeddings
import numpy as np

def check_caption_length(caption: str) -> bool:
    """Return True if caption ≤125 characters."""
    return len(caption) <= 125

def semantic_similarity(a: str, b: str) -> float:
    """Compute cosine similarity between embeddings of two texts."""
    emb = OpenAIEmbeddings()
    ea = emb.embed_query(a)
    eb = emb.embed_query(b)
    return float(np.dot(ea, eb) / (np.linalg.norm(ea) * np.linalg.norm(eb)))
```

- Use these to **flag** scripts for re-generation if they violate length or duplicate existing content (>0.85 similarity).

---

## 🌐 7. Web UI (`src/app.py`)

### Streamlit version

```python
import streamlit as st
from generator import generate_script
from polish import polish
from utils import check_caption_length, semantic_similarity

st.title("Instagram Script Writer")

topic = st.text_input("Enter Topic")
if st.button("Generate"):
    with st.spinner("Generating draft…"):
        draft = generate_script(topic)
    with st.spinner("Polishing…"):
        final = polish(draft)
    st.subheader("Final Script")
    st.write(final)

    # QC
    caption = final.split("CAPTION:")[1].split("\n")[0].strip()
    if not check_caption_length(caption):
        st.warning("Caption exceeds 125 characters!")
```

- **Run:** `streamlit run src/app.py`

---

## 🐳 8. Docker Setup

### `docker/Dockerfile`

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### `docker/docker-compose.yml`

```yaml
version: "3.8"
services:
  web:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - PINECONE_ENV=${PINECONE_ENV}
      - PINECONE_INDEX=${PINECONE_INDEX}
      - MODEL_FINE_TUNED=${MODEL_FINE_TUNED}
    volumes:
      - ./scripts:/app/scripts
```

- **Build & run:** `docker-compose up --build`

---

## 🧪 9. Testing (`tests/`)

- **pytest** tests for each module.
- **Monkeypatch** or **fixtures** to stub OpenAI & Pinecone calls.
- Example: `test_utils.py` should assert `check_caption_length("abc") is True` and similarity bounds.

```bash
pytest --maxfail=1 --disable-warnings -q
```

---

## 🔄 10. CI/CD (`.github/workflows/ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install dependencies
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -r requirements.txt
      - name: Lint with flake8
        run: |
          source .venv/bin/activate
          pip install flake8
          flake8 src tests
      - name: Run pytest
        run: |
          source .venv/bin/activate
          pip install pytest
          pytest --maxfail=1 --disable-warnings -q
      - name: Build Docker image
        run: docker build -t instagram-script-writer .
```

---

## 🚀 11. Development Workflow

1. **Clone & setup** environment
2. **Write or update** `.txt` scripts in `scripts/`
3. **Ingest**: `python src/ingest.py`
4. **Generate**: CLI or `streamlit run src/app.py`
5. **Polish & QC** automatically in pipeline
6. **Commit & push** — CI will test and build
7. **Deploy** Docker container to your cloud

---

## 📈 12. Next Steps & Iteration

- **A/B test** generated scripts on Instagram; track engagement metrics.
- **Re-embed** top performers monthly; re-fine-tune quarterly.
- **Extend** UI: support Instagram Stories, Carousel scripts, and hashtag suggestions.
- **Add** analytics dashboard to monitor generation usage and performance.

---

_End of Development Documentation._

```

```
