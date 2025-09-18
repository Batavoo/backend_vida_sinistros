import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import langchain
from langchain.cache import InMemoryCache

# ATIVAÇÃO DO CACHE:
# Isso fará com que qualquer chamada de LLM com os mesmos inputs seja retornada do cache.
langchain.llm_cache = InMemoryCache()

from agent import get_agent_executor

# Carregar variáveis de ambiente
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi definida.")

app = FastAPI(
    title="Chatbot de Análise de Dados com Excel",
    description="Uma API para fazer perguntas em linguagem natural sobre um arquivo de planilha Excel.",
    version="1.0.0",
)

try:
    agent_executor = get_agent_executor()
except FileNotFoundError:
    raise RuntimeError("Erro: O arquivo 'sinistros_simplificado.xlsx' não foi encontrado. Por favor, adicione o arquivo ao diretório do projeto.")
except Exception as e:
    raise RuntimeError(f"Erro ao inicializar o agente: {e}")


class ChatRequest(BaseModel):
    question: str


@app.post("/chat", summary="Envia uma pergunta para o agente")
async def chat(request: ChatRequest):
    """
    Recebe uma pergunta em linguagem natural, a processa com o agente LangChain
    e retorna a resposta.
    """
    question = request.question
    if not question:
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    try:
        response = agent_executor.invoke({"input": question})
        return {"answer": response.get("output")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar sua pergunta: {e}")