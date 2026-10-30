FROM python:3.12-slim

WORKDIR /app


RUN pip install --no-cache-dir torch==2.14.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
# CRUCIAL: Makes sure Linux gives the container rights to run start.sh
RUN chmod +x start.sh

EXPOSE 8000
EXPOSE 8501

ENV FAST_API=inference_pipeline.py

CMD ["./start.sh"]