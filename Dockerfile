FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml requirements.lock ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.lock \
    && pip install --no-cache-dir --no-deps .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "deskline.api.main:app", "--host", "0.0.0.0", "--port", "8000"]