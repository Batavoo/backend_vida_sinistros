import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from agent import get_agent_executor

# Carregar variáveis de ambiente (sua chave da API)
load_dotenv()

# Validar se a chave da API da OpenAI foi configurada
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi definida.")

# Inicializar a aplicação FastAPI
app = FastAPI(
    title="Chatbot de Análise de Dados com Excel",
    description="Uma API para fazer perguntas em linguagem natural sobre um arquivo de planilha Excel.",
    version="1.0.0",
)

# Criar o executor do agente uma vez, quando a aplicação inicia
try:
    agent_executor = get_agent_executor()
except FileNotFoundError:
    # Se o arquivo .xlsx não for encontrado, encerre a aplicação com uma mensagem clara
    raise RuntimeError("Erro: O arquivo 'sinistros_simplificado.xlsx' não foi encontrado. Por favor, adicione o arquivo ao diretório do projeto.")
except Exception as e:
    raise RuntimeError(f"Erro ao inicializar o agente: {e}")


# Modelo de dados para a requisição do chat
class ChatRequest(BaseModel):
    question: str


# Endpoint da API para interagir com o chatbot
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
        # A resposta do `create_sql_agent` vem em um formato um pouco diferente
        response = agent_executor.invoke({"input": question})
        return {"answer": response.get("output")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar sua pergunta: {e}")