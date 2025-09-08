# app/tasks.py

import os
import requests
import json
from celery import Celery
from dotenv import load_dotenv
load_dotenv()  # Loads .env into os.environ

# Initialize Celery
MODEL_NAME = os.getenv("MODEL_NAME", "qwen:0.5b")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

@celery.task(name="tasks.analyze_fraud_with_llm", bind=True, max_retries=3)
def analyze_fraud_with_llm(self, transaction, history):
    """
    Offloaded task: Ask Qwen LLM if transaction is fraudulent.
    Runs in background Celery worker.
    """
    OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    prompt = f"""
You are a fraud detection assistant for a FinTech company.
Analyze the following transaction and user history to determine if it is likely fraudulent.

Transaction: {json.dumps(transaction, indent=2)}

User's recent transaction history (last 5):
{json.dumps(history, indent=2)}

Answer in JSON format only:
{{
  "is_fraud": true/false,
  "risk_score": 0.0 to 1.0,
  "reason": "brief explanation"
}}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_ctx": 2048
        }
    }

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        if resp.status_code != 200:
            raise Exception(f"Ollama error: {resp.text}")

        result = resp.json()
        response_text = result.get("response", "{}")
        parsed = json.loads(response_text)
        return parsed

    except Exception as exc:
        print(f"Task failed, retrying...: {exc}")
        raise self.retry(exc=exc, countdown=5)