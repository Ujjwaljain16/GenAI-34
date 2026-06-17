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
CMD ["python", "-u", "start.py"]
