## 📸 PlacaView – Reconhecimento de Placas com FastAPI, Next.js e MongoDB

**PlacaView** é um sistema web para reconhecimento automático de placas de veículos (ANPR) com persistência em MongoDB, API em FastAPI e frontend em Next.js. Suporta upload de arquivos e captura em base64 (webcam), registra entrada/saída e disponibiliza histórico e CRUD de registros.

### 🔎 Principais recursos

- **Upload e OCR de placas** (detecção + OCR via FastALPR + OpenCV)
- **Registro de hora de entrada e saída**
- **Listagem, busca, atualização e exclusão** de registros
- **Serviço de imagens** salvas em disco
- **Documentação interativa da API** em `/docs`

## 🧱 Arquitetura e stack

- **Backend**: FastAPI (Python), CORS habilitado, rota base `\( /api/v1 \)`
- **OCR/Detecção**: FastALPR (YOLO v9 + OCR CCT-XS) sobre OpenCV
- **Banco**: MongoDB 7
- **Frontend**: Next.js 15 (React 19)
- **Infra**: Docker Compose (serviços `mongodb`, `backend`, `frontend`), Nginx opcional para produção
- **Captura embarcada (opcional)**: diretório `CameraAndLaser/` com firmware para câmera/laser

## 📦 Como rodar (Docker Compose)

### 1. Clonar o repositório
```bash
git clone <URL_DO_REPO>
cd CFA
```

### 2. Subir os serviços
```bash
docker compose -f infra/docker-compose.yml up -d --build
```

### 3. Acessos
- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- Docs (Swagger): `http://localhost:8000/docs`

> Observação: no Compose, o frontend já recebe `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## 🖥️ Como rodar localmente (sem Docker)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
cp env.local.example .env.local # ajuste NEXT_PUBLIC_API_URL se necessário
npm install
npm run dev
```

## ⚙️ Variáveis de ambiente

### Backend (`backend/.env`)
- `MONGODB_URI` (ex.: `mongodb://localhost:27017/` ou `mongodb://mongodb:27017/` no Docker)
- `DATABASE_NAME` (ex.: `ocr_db`)
- `COLLECTION_NAME` (ex.: `placas`)
- `UPLOAD_FOLDER` (ex.: `uploads`)
- `MAX_FILE_SIZE` (bytes, ex.: `52428800`)

Exemplo disponível em `backend/env.example`.

### Frontend (`frontend/.env.local`)
- `NEXT_PUBLIC_API_URL` (ex.: `http://localhost:8000` ou `http://backend:8000` no Docker)

Exemplo disponível em `frontend/env.local.example`.

## 🔗 Endpoints principais

Base da API: `http://localhost:8000/api/v1`

- `GET /health` — healthcheck
- `POST /placas/upload_image` — upload de arquivo (`image`) ou base64 (`image_base64`)
- `GET /placas` — lista registros (param opcional `limit`)
- `GET /placas/{placa_id}` — busca por ID
- `POST /placas/search` — busca por placa (body `{ placa: string }`)
- `PUT /placas/{placa_id}` — atualiza campos (entrada/saída etc.)
- `POST /placas/clear/{placa_id}` — marca saída (`hora_saida`)
- `DELETE /placas/{placa_id}` — exclui registro
- `GET /placas/images/{filename}` — serve imagem salva

Documentação completa no Swagger: `http://localhost:8000/docs`

## 📂 Estrutura de pastas

- `backend/` — API FastAPI, serviços de OCR e banco
- `backend/app/services/alpr/` — implementação FastALPR (detector e OCR)
- `frontend/` — Next.js (upload, listagem, busca, edição)
- `infra/` — `docker-compose.yml`, Nginx opcional, seed de Mongo, uploads de exemplos
- `CameraAndLaser/` — código para microcontrolador (opcional)

## 🧪 Fluxos suportados

- **Upload de arquivo** via frontend → backend salva imagem original, roda ANPR, persiste documento com `placa`, `hora_entrada`, `image_base64` anotada e `original_path`.
- **Captura base64 (webcam)** via frontend → mesmo pipeline do upload de arquivo.
- **Saída** via `POST /placas/clear/{id}` → preenche `hora_saida`.

## 🛠 Desenvolvimento

- Frontend: `npm run dev`, `npm run build`, `npm run start`, `npm run lint`
- Backend: `uvicorn app.main:app --reload`
- Lint/format: siga o estilo existente; evite arquivos com mais de 1600 linhas.

## ❗ Solução de problemas

- API não sobe no Docker: verifique `infra/docker-compose.yml` e o healthcheck em `http://localhost:8000/health`.
- OCR não retorna placa: confira dependências do backend e suporte a instruções da CPU/GPU; veja logs do container `placaview-backend`.
- Imagens não servidas: garanta que `UPLOAD_FOLDER` exista e contenha o arquivo solicitado; caminho base: `/api/v1/placas/images/{filename}`.

## 📜 Licença

Uso acadêmico/demonstrativo. Ajuste conforme a sua necessidade.