# 📸 PlacaView – Estacionamento com OCR e MongoDB

**PlacaView** é um sistema web que realiza o reconhecimento de placas de veículos a partir de imagens usando OCR (EasyOCR) e registra entradas e saídas em um banco de dados MongoDB.

Ideal para controle automatizado de estacionamentos, com histórico, consulta e CRUD completo dos veículos.

---

## 🚀 Funcionalidades

- ✅ Upload de imagem com detecção automática de placa
- ✅ Registro da hora de entrada
- ✅ Armazenamento em MongoDB (imagem + dados)
- ✅ Histórico de veículos
- ✅ Exclusão de registros
- 🔍 Consulta por placa (em construção)
- ✏️ Edição (hora de saída etc.) (em construção)

---

## 🛠 Tecnologias utilizadas

- Python + Flask
- EasyOCR + OpenCV
- MongoDB (local ou Atlas)
- HTML + CSS (interface simples e responsiva)

---

## 📦 Instalação e Execução

### 1. Clone o projeto

```bash
git clone https://github.com/seu-usuario/placaview.git
cd placaview
```

### 2. Suba no docker
```bash
docker compose -f infra/docker-compose.yml up -d
```

### 3. Instale as dependências do frontend
```bash
npm i
```

### 4. Inicie o Frontend
```bash
npm run dev
```

Acesse em: http://127.0.0.1:3000 

🧪 Em desenvolvimento
Consulta por placa

Registro de hora de saída

Edição completa de registros


