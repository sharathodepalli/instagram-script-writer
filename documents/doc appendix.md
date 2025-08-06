Below is an **appendix** covering the additional “rest” of concerns—everything beyond the core pipeline you might need for a production-grade, maintainable, and secure system. Add this to your `README.md` (or as `APPENDIX.md`) in the workspace.

````markdown
# Appendix: Additional Production Concerns

---

## 1. Logging & Error Handling

### 1.1 Python Logging Setup

- Configure a root logger in `src/config.py` or a dedicated `logging.py`:

  ```python
  import logging, sys

  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s %(levelname)s %(name)s %(message)s",
      handlers=[logging.StreamHandler(sys.stdout)]
  )
  logger = logging.getLogger("ig_script_writer")
  ```
````

- In each module:

  ```python
  from config import logger
  logger.info("Ingest started for %d docs", len(docs))
  ```

### 1.2 Error Handling Patterns

- **Retries** for transient API failures (OpenAI, Pinecone):

  ```python
  import tenacity

  @tenacity.retry(
      wait=tenacity.wait_exponential(min=1, max=10),
      stop=tenacity.stop_after_attempt(5),
      retry=tenacity.retry_if_exception_type((openai.error.RateLimitError, pinecone.core.client.ApiException))
  )
  def call_openai(...):
      return openai.ChatCompletion.create(...)
  ```

- **Graceful exits**: catch and log exceptions at the CLI/UI boundary, then show a user-friendly message:

  ```python
  try:
      result = generate_script(topic)
  except Exception as e:
      logger.exception("Generation failed")
      st.error("Sorry, something went wrong. Please try again.")
  ```

---

## 2. Monitoring & Analytics

### 2.1 Usage Metrics

- **Count** number of generations per day/week
- **Latency** of each API call (ingest, generate, polish)
- Push metrics to a monitoring service (DataDog, Prometheus + Grafana).

### 2.2 Engagement Tracking

- After posting scripts, track Instagram metrics (views, likes, shares).
- Store performance data in a DB (Postgres/Mongo).

### 2.3 Feedback Loop

- Identify top-performing scripts → automatically re-embed into Pinecone → include in next fine-tune.

---

## 3. Security Best Practices

- **Secrets Management**:

  - Don’t commit `.env` to Git.
  - In CI, store keys as GitHub Secrets and reference via `${{ secrets.OPENAI_API_KEY }}`.

- **Least Privilege**:

  - Create a dedicated Pinecone API key scoped to only the “ig-scripts” index.

- **API Key Rotation**:

  - Schedule quarterly key rotation; update `.env` or CI secrets accordingly.

- **Dependency Scanning**:

  - Include a step in CI: `safety check` or GitHub’s Dependabot alerts.

---

## 4. Cost Management

- **OpenAI**:

  - Track token usage per run; aggregate daily.
  - Consider switching long-term to GPT-3.5 for polish if cost is too high.

- **Pinecone**:

  - Choose a vector index plan sized to your document count; scale up/down monthly.

- **Alerts**:

  - Budget notifications via AWS/Billing or manually review invoices monthly.

---

## 5. Performance Optimization

- **Batch Ingest**:

  - If you have hundreds of scripts, embed in batches of 100 to avoid rate-limits.

- **Cache Embeddings**:

  - Store embedding vectors alongside raw text so re-running `ingest.py` only processes new files.

- **Local Development**:

  - Use a small FAISS index in-memory for local testing to save Pinecone credits.

---

## 6. Code Style & Quality

- **Formatter**: Black
- **Linter**: Flake8 with these rules in `setup.cfg`:

  ```ini
  [flake8]
  max-line-length = 88
  extend-ignore = E203, W503
  ```

- **Type Checking**: Mypy (optional)
- **Pre-commit Hooks**:

  ```yaml
  repos:
    - repo: https://github.com/psf/black
      rev: stable
      hooks: [{ id: black }]
    - repo: https://gitlab.com/pycqa/flake8
      rev: 6.0.0
      hooks: [{ id: flake8 }]
  ```

---

## 7. A/B Testing Integration

- **Variant Generation**: let the model generate 2–3 variants per topic:

  ```python
  for i in range(3):
      draft = generate_script(topic, seed=i)
      ...
  ```

- **Test Deployment**:

  - Post each variant to a small segment of your audience (e.g. via Instagram Ads with custom audiences).

- **Statistical Analysis**: collect engagement metrics and choose the winner.
- **Auto-Feedback**: tag the winning script and feed back into your index/training set.

---

## 8. Automated Fine-Tune Scheduling

- Use a cron job or GitHub Actions scheduled workflow:

  ```yaml
  on:
    schedule:
      - cron: "0 0 1 * *" # 1st of every month at 00:00 UTC
  jobs:
    retrain:
      runs-on: ubuntu-latest
      steps:
        - name: Prepare data & JSONL
          run: python scripts/prepare_finetune_set.py
        - name: Trigger OpenAI Fine-tune
          env:
            OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          run: openai api fine_tunes.create -t fine_tune_data.jsonl -m gpt-3.5-turbo --n_epochs 2
  ```

---

## 9. Cloud Deployment (Optional)

- **Container Registry**: push your Docker image to AWS ECR / Docker Hub.
- **Orchestration**: deploy to Kubernetes (EKS/GKE) or serverless containers (AWS Fargate).
- **Ingress & TLS**: use an ingress controller or AWS ALB + ACM certificate for HTTPS.

---

_End of Appendix._

```

```
