FROM python:3.9-slim
RUN pip install streamlit boto3
COPY . /app
WORKDIR /app
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
