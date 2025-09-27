FROM python:3.11-slim

WORKDIR /app

RUN apt update && apt install -y git && apt install tree

RUN groupadd --gid 1000 vscode && useradd --uid 1000 --gid 1000 -m vscode

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

COPY . .

USER vscode

CMD ["watchmedo", "auto-restart", "--directory=.", "--pattern=*.py", \
     "--recursive", "--", "celery", "-A", "app.worker.celery_app", "worker", "-l", "info"]
