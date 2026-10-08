FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./ 
COPY README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev
EXPOSE 5000
CMD ["uv", "run", "flask", "--app", "llm_man_1.api:app", "run", "--host=0.0.0.0", "--port=5000"]
