FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy from the backend directory to the image
COPY --chown=user backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user backend/ .

# Ensure the uploads directory exists and is writable by the user
RUN mkdir -p uploads && chmod 777 uploads

ENV HOST=0.0.0.0
ENV PORT=7860

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 7860"]
