FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY customagenthf ./customagenthf

RUN pip install --no-cache-dir .

EXPOSE 8001

CMD ["customagenthf-service"]