import time
import logging
from collections import defaultdict
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

# Importações da nossa aplicação
from app.core.config import settings
from app.db import database, models
from app.api.v1.endpoints import acoes, usuarios, logs # <-- Importa todos os routers
from app.db.database import SessionLocal
from app.db.models import Usuario

# --- Lógica de Rate Limiting ---
requests_log = defaultdict(list)

def rate_limit_dependency(request: Request):
    if not settings.API_SAFE_MODE:
        return
    ip = request.client.host
    now = time.time()
    requests_log[ip] = [timestamp for timestamp in requests_log[ip] if now - timestamp < 60]
    if len(requests_log[ip]) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Limite de {settings.RATE_LIMIT_PER_MINUTE} requisições por minuto atingido."
        )
    requests_log[ip].append(now)

# --- Criação da Aplicação FastAPI ---
app = FastAPI(
    title="API de Ações da Bolsa",
    description="Uma API de alta performance para consulta de dados do mercado financeiro.",
    version="1.0.0"
)

# --- Middleware para Logging ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        status_code = 500
        logging.error(f"Erro não tratado na requisição: {e}")
        response = JSONResponse(status_code=500, content={"detail": "Ocorreu um erro interno no servidor."})

    db_log = SessionLocal()
    try:
        user_id = None
        api_key = request.headers.get("x-api-key")
        if api_key:
            stmt = select(Usuario).where(Usuario.api_key == api_key)
            user = db_log.execute(stmt).scalar_one_or_none()
            if user:
                user_id = user.id
        
        log_entry = models.LogRequisicao(
            usuario_id=user_id,
            method=request.method,
            endpoint=str(request.url.path),
            status_code=status_code,
            response_time_ms=int(process_time)
        )
        db_log.add(log_entry)
        db_log.commit()
    except Exception as e:
        logging.error(f"Erro ao salvar log no banco de dados: {e}")
        db_log.rollback()
    finally:
        db_log.close()
    return response

# --- Inclusão dos Routers da API ---
app.include_router(
    acoes.router,
    prefix="/api/v1/acoes",
    tags=["Ações e Índices"],
    dependencies=[Depends(rate_limit_dependency)]
)
app.include_router(
    usuarios.router,
    prefix="/api/v1/usuarios",
    tags=["Usuários"],
    dependencies=[Depends(rate_limit_dependency)]
)
app.include_router(
    logs.router,
    prefix="/api/v1/logs",
    tags=["Logs"],
    dependencies=[Depends(rate_limit_dependency)]
)

@app.get("/", summary="Health Check")
def read_root():
    return {"status": "API online e operacional!"}