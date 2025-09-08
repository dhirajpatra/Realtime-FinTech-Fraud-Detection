from flask import Flask, request, jsonify
from tasks import celery, analyze_fraud_with_llm
import requests
import json
import time
import os

import aerospike
from dotenv import load_dotenv
load_dotenv()  # Loads .env into os.environ

app = Flask(__name__)

# Config
MODEL_NAME = os.getenv("MODEL_NAME", "qwen:0.5b")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
AEROSPIKE_HOST = os.getenv("AEROSPIKE_HOST", "localhost")
AEROSPIKE_PORT = int(os.getenv("AEROSPIKE_PORT", 3000))

# Connect to Aerospike
config = {
    'hosts': [(AEROSPIKE_HOST, AEROSPIKE_PORT)],
    'policies': {'timeout': 1000}
}
client = aerospike.client(config).connect()

NAMESPACE = "fraudns"
SET = "transactions"

# Ensure Qwen is pulled
def ensure_qwen_model():
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags")
        models = resp.json().get("models", [])
        qwen_exists = any(m["name"] == MODEL_NAME for m in models)
        if not qwen_exists:
            print(f"🟡 Pulling {MODEL_NAME}...")
            requests.post(f"{OLLAMA_URL}/api/pull", json={"name": "qwen:0.5b"})
            print(f"✅ {MODEL_NAME} pulled.")
    except Exception as e:
        print("❌ Failed to pull model:", e)

ensure_qwen_model()

def get_user_history(user_id):
    """Fetch last 5 transactions for user from Aerospike"""
    try:
        key = (NAMESPACE, SET, f"user_{user_id}")
        _, meta, bins = client.get(key)
        return bins.get("history", [])
    except aerospike.exception.RecordNotFound:
        return []
    except Exception as e:
        print("Error fetching history:", e)
        return []

def update_user_history(user_id, new_transaction):
    """Append transaction to user history in Aerospike"""
    key = (NAMESPACE, SET, f"user_{user_id}")
    try:
        _, meta, bins = client.get(key)
        history = bins.get("history", [])
    except aerospike.exception.RecordNotFound:
        history = []

    history.append(new_transaction)
    if len(history) > 5:
        history = history[-5:]  # Keep last 5

    client.put(key, {"history": history})

# # now it moved to tasks.py
# def ask_llm_for_fraud_analysis(transaction, history):
#     """Use Qwen 0.5B to analyze if transaction is fraudulent"""

#     prompt = f"""
# You are a fraud detection assistant for a FinTech company.
# Analyze the following transaction and user history to determine if it is likely fraudulent.

# Transaction: {json.dumps(transaction, indent=2)}

# User's recent transaction history (last 5):
# {json.dumps(history, indent=2)}

# Answer in JSON format only:
# {{
#   "is_fraud": true/false,
#   "risk_score": 0.0 to 1.0,
#   "reason": "brief explanation"
# }}
# """

#     payload = {
#         "model": MODEL_NAME,
#         "prompt": prompt,
#         "stream": False,
#         "format": "json",  # force JSON output
#         "options": {
#             "temperature": 0.1,
#             "num_ctx": 2048
#         }
#     }

#     try:
#         resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
#         if resp.status_code != 200:
#             raise Exception(f"Ollama error: {resp.text}")

#         result = resp.json()
#         response_text = result.get("response", "{}")
#         return json.loads(response_text)

#     except Exception as e:
#         print("LLM Error:", e)
#         return {
#             "is_fraud": False,
#             "risk_score": 0.0,
#             "reason": "LLM analysis failed. Defaulting to safe."
#         }

@app.route('/detect-fraud', methods=['POST'])
def detect_fraud():
    data = request.get_json()

    required_fields = ["user_id", "amount", "merchant", "location", "timestamp"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Get user history
    history = get_user_history(data["user_id"])

    # 🐇 ASYNC: Send to Celery worker
    task = analyze_fraud_with_llm.delay(data, history)

    # Store transaction immediately (don't wait for LLM)
    update_user_history(data["user_id"], data)

    # Return task ID for polling
    return jsonify({
        "transaction_id": str(int(time.time())),
        "user_id": data["user_id"],
        "task_id": task.id,
        "status": "processing",
        "message": "Fraud analysis in progress. Poll /result/<task_id> for result."
    }), 202

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    """Poll for async task result"""
    task = analyze_fraud_with_llm.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is waiting to be processed...'
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result,
            'status': 'Completed'
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info) if task.info else 'Unknown error occurred.'
        }
    else:
        response = {
            'state': task.state,
            'status': 'Task is running...'
        }

    return jsonify(response)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)