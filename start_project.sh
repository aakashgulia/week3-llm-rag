#!/bin/bash

cd ~/projects/week3-llm-rag
source venv/bin/activate

echo "Starting Retrieval Service..."
uvicorn retrieval_service:app --host 0.0.0.0 --port 8001 > retrieval.log 2>&1 &

echo "Starting Inference Service..."
uvicorn inference_service:app --host 0.0.0.0 --port 8002 > inference.log 2>&1 &

echo "Starting Main FastAPI..."
uvicorn app:app --host 0.0.0.0 --port 8501 > app.log 2>&1 &

echo "Starting Streamlit..."
streamlit run streamlit_app.py --server.port 8502 > streamlit.log 2>&1 &

echo ""
echo "===================================="
echo "  Project started successfully!"
echo "===================================="
echo "Streamlit: http://localhost:8502"
echo ""
echo "Press Enter to close this launcher."
read
