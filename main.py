import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import time

from agent import get_agent_executor

load_dotenv()

# --- NOSSO CACHE DE APLICAÇÃO ---
# Um dicionário simples para armazenar as respostas.
# A chave é a pergunta, o valor é a resposta.
# Nota: Este cache é em memória e será resetado com o servidor.
application_cache = {}
# -----------------------------

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi definida.")

app = FastAPI(
    title="Chatbot de Análise de Dados com Excel",
    description="Uma API para fazer perguntas em linguagem natural sobre um arquivo de planilha Excel.",
    version="2.0.0", # Versão 2.0, porque agora funciona!
)

try:
    agent_executor = get_agent_executor()
except Exception as e:
    raise RuntimeError(f"Erro ao inicializar o agente: {e}")

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    duration_seconds: float
    is_from_cache: bool

@app.post("/chat", response_model=ChatResponse, summary="Envia uma pergunta para o agente com cache de aplicação")
async def chat(request: ChatRequest):
    question = request.question.strip().lower() # Normalizar a pergunta para melhorar o cache
    if not question:
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    # 1. VERIFICAR O CACHE PRIMEIRO
    if question in application_cache:
        cached_data = application_cache[question]
        return ChatResponse(
            answer=cached_data["answer"],
            duration_seconds=0.0, # Instantâneo
            is_from_cache=True
        )

    # 2. SE NÃO ESTIVER NO CACHE, EXECUTAR O AGENTE
    try:
        start_time = time.time()
        response = agent_executor.invoke({"input": question})
        end_time = time.time()
        
        duration = end_time - start_time
        final_answer = response.get("output")

        # 3. SALVAR O NOVO RESULTADO NO CACHE
        application_cache[question] = {"answer": final_answer}

        return ChatResponse(
            answer=final_answer,
            duration_seconds=duration,
            is_from_cache=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar sua pergunta: {str(e)}")
