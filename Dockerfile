FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh && \
    addgroup --system --gid 1000 app && \
    adduser --system --uid 1000 --ingroup app --no-create-home app && \
    chown -R app:app /app

USER app

ENTRYPOINT ["./entrypoint.sh"]
