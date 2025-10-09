# Multi-stage build para otimizar tamanho e velocidade
FROM python:3.11-slim as builder

# Instala dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências pesadas primeiro (para melhor cache)
COPY requirements-heavy.txt .
RUN pip install --no-cache-dir --user -r requirements-heavy.txt

# Instala dependências principais
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage final - imagem de produção
FROM python:3.11-slim

# Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.local/bin:$PATH"

# Instala apenas dependências runtime essenciais
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copia dependências instaladas do builder
COPY --from=builder /root/.local /root/.local

# Define diretório de trabalho
WORKDIR /app

# Copia código da aplicação
COPY src/ .

# Cria diretório para uploads
RUN mkdir -p uploads

# Expõe porta 5000
EXPOSE 5000

# Comando para executar a aplicação
CMD ["python", "app.py"]
