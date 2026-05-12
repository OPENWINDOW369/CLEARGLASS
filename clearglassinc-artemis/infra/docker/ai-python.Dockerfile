FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir pydantic pytest
COPY . .
CMD ["python", "-m", "pytest", "-q"]
