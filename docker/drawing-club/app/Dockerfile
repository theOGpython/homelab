FROM python:3.12-alpine
WORKDIR /app
COPY server.py .
COPY public ./public
USER 1000:1000
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8000/healthz || exit 1
CMD ["python", "-u", "server.py"]
