FROM python:3.12-slim
RUN useradd --uid 10001 --no-create-home exporter
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY exporter.py .
USER exporter
EXPOSE 9877
CMD ["python", "-u", "exporter.py"]
