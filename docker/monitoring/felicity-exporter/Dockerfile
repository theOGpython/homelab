FROM python:3.12-alpine
RUN adduser -D -u 10001 exporter
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY exporter.py .
USER exporter
EXPOSE 9878
CMD ["python", "-u", "exporter.py"]
