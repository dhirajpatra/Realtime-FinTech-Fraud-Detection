
# 🕵️ FinTech Fraud Detection with LLM (Qwen 0.5B) + Aerospike + Ollama

> A lightweight, end-to-end fraud detection system using **Qwen 0.5B** via **Ollama**, storing user transaction history in **Aerospike**, served via **Flask**, orchestrated with **Docker Compose**, and optionally offloaded to **Celery workers** for async LLM inference.

---

## ✅ Features

- **Local LLM**: Uses `qwen:0.5b` (smallest Qwen model) via Ollama for fraud reasoning.
- **Real-time Storage**: Aerospike for low-latency user transaction history.
- **Async Processing**: Optional Celery + Redis for async LLM calls (see branch `async-celery`).
- **Dockerized**: Single `docker-compose up` to launch entire stack.
- **JSON API**: Simple REST endpoint to submit transactions and get fraud analysis.

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- At least 4GB RAM free (LLM + DB)

### Run

```bash
git clone https://github.com/yourusername/fintech-fraud-llm.git
cd fintech-fraud-llm
docker-compose up --build
```

> ⏳ First run may take 2-5 mins (pulling Qwen model + building images).

### Test

```bash
curl -X POST http://localhost:5000/detect-fraud \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "amount": 5000,
    "merchant": "Electronics Store",
    "location": "New York, USA",
    "timestamp": "2025-04-05T10:00:00Z"
  }'
```

✅ Sample Response:
```json
{
  "transaction_id": "1712345678",
  "user_id": "user123",
  "analysis": {
    "is_fraud": true,
    "risk_score": 0.85,
    "reason": "High amount + new location."
  }
}
```

---

## 🧩 Architecture

```
Client → Flask API → [Aerospike (History)] + [Ollama/Qwen (Analysis)] → Response
                          ↑
                    (Optional: Celery Async Worker)
```

---

## 📂 Project Structure

```
.
├── docker-compose.yml
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── README.md
└── (optional async branch: celery_worker.py, tasks.py, updated Dockerfile & compose)
```

---

## 🛠️ Future Enhancements

- Add React frontend
- Prometheus/Grafana monitoring
- Rule engine fallback
- Model fine-tuning on fraud datasets
- Kubernetes deployment

---

## 📜 License

MIT — Use freely for learning, prototyping, or commercial use.

---

> 💡 Tip: First inference is slow — Qwen loads into memory. Subsequent calls are faster!
``` 

---

✅ **To download this README.md**:

1. Copy the entire content above.
2. Paste into a new file named `README.md` in your project root.
3. Save it.

Or, if you’re in a terminal and want to generate it:

```bash
cat > README.md << 'EOF'
# 🕵️ FinTech Fraud Detection with LLM (Qwen 0.5B) + Aerospike + Ollama

> A lightweight, end-to-end fraud detection system using **Qwen 0.5B** via **Ollama**, storing user transaction history in **Aerospike**, served via **Flask**, orchestrated with **Docker Compose**, and optionally offloaded to **Celery workers** for async LLM inference.

---

## ✅ Features

- **Local LLM**: Uses `qwen:0.5b` (smallest Qwen model) via Ollama for fraud reasoning.
- **Real-time Storage**: Aerospike for low-latency user transaction history.
- **Async Processing**: Optional Celery + Redis for async LLM calls (see branch `async-celery`).
- **Dockerized**: Single `docker-compose up` to launch entire stack.
- **JSON API**: Simple REST endpoint to submit transactions and get fraud analysis.

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- At least 4GB RAM free (LLM + DB)

### Run

```bash
git clone https://github.com/yourusername/fintech-fraud-llm.git
cd fintech-fraud-llm
docker-compose up --build
```

> ⏳ First run may take 2-5 mins (pulling Qwen model + building images).

### Test

```bash
curl -X POST http://localhost:5000/detect-fraud \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "amount": 5000,
    "merchant": "Electronics Store",
    "location": "New York, USA",
    "timestamp": "2025-04-05T10:00:00Z"
  }'
```

✅ Sample Response:
```json
{
  "transaction_id": "1712345678",
  "user_id": "user123",
  "analysis": {
    "is_fraud": true,
    "risk_score": 0.85,
    "reason": "High amount + new location."
  }
}
```

---

## 🧩 Architecture

```
Client → Flask API → [Aerospike (History)] + [Ollama/Qwen (Analysis)] → Response
                          ↑
                    (Optional: Celery Async Worker)
```

---

## 📂 Project Structure

```
.
├── docker-compose.yml
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── README.md
└── (optional async branch: celery_worker.py, tasks.py, updated Dockerfile & compose)
```

---

## 🛠️ Future Enhancements

- Add React frontend
- Prometheus/Grafana monitoring
- Rule engine fallback
- Model fine-tuning on fraud datasets
- Kubernetes deployment

---

## 📜 License

MIT — Use freely for learning, prototyping, or commercial use.

---

> 💡 Tip: First inference is slow — Qwen loads into memory. Subsequent calls are faster!
