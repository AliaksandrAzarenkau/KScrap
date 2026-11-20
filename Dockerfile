FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR .

COPY reqirements.txt .
RUN pip install -r reqirements.txt

COPY . .

CMD ["python", "tbot.py"]