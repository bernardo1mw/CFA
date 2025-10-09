# Dockerfile para o frontend Next.js
FROM node:18-alpine

# Instala dependências do sistema
RUN apk add --no-cache libc6-compat

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependências
COPY package.json package-lock.json* ./

# Instala dependências
RUN npm ci --only=production

# Copia o código da aplicação
COPY . .

# Configura variáveis de ambiente
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NODE_ENV=production

# Build da aplicação
RUN npm run build

# Expõe a porta
EXPOSE 3000

# Comando para executar a aplicação
CMD ["npm", "start"]
