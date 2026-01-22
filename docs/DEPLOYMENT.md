[⬅️ Back to README](../README.md)

---

# 🚀 Deployment Guide

InduSense Analytics is designed to be container-native. It can be deployed on any platform that supports Docker (AWS ECS, Azure App Service, Google Cloud Run) or directly on Streamlit Cloud.

---

## 🐳 Docker Deployment (Recommended)

### 1. Build the Image

The project includes a multi-stage Dockerfile optimized for size.

```bash
docker build -t indusense-gen:latest .
```

---

### 2. Run Container

Pass your API key as an environment variable.

```bash

docker run -p 8501:8501 \
  -e OPENAI_API_KEY="sk-..." \
  indusense-gen:latest
```

Access the app at `http://localhost:8501`.

---

## ☁️ Streamlit Cloud Deployment

For rapid hosting (free tier), this project is fully compatible with Streamlit Community Cloud.

1. Push code to GitHub.

2. Login to share.streamlit.io.

3. Select Repository: `ai-test-procedure-generator`.

4. Main File Path: `app/main.py`.

5. Advanced Settings:

- Add your `OPENAI_API_KEY` in the "Secrets" section.

---

## 📦 Requirements

Python 3.10+

512MB RAM (Minimum) / 1GB RAM (Recommended for PDF generation)

---
