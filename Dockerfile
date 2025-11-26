FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# Usa più mirror PyPI per maggiore resilienza
RUN pip install --no-cache-dir \
    -i https://pypi.org/simple \
    --extra-index-url https://pypi.python.org/simple \
    --extra-index-url https://mirrors.aliyun.com/pypi/simple \
    --extra-index-url https://pypi.mirrors.ustc.edu.cn/simple \
    -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
