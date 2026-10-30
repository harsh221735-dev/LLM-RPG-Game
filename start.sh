#!/bin/bash
echo "starting backend"
uvicorn inference_pipeline:app --host 0.0.0.0 --port 8000 &

sleep 10

echo "starting frontend"
streamlit run frontend_init.py --server.port 8501 --server.address 0.0.0.0