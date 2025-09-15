import os
import pandas as pd
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent


def get_db_connection(xls_file='sinistros_simplificado.xlsx', table_name='sinistros_simplificado'):
    """
    Carrega um arquivo .xlsx para um banco de dados SQLite em memória.
    Retorna uma conexão SQLDatabase da LangChain.
    """
    if not os.path.exists(xls_file):
        raise FileNotFoundError(f"O arquivo {xls_file} não foi encontrado.")

    # Lê o arquivo Excel. Por padrão, lê a primeira aba.
    df = pd.read_excel(xls_file)

    # Cria um motor de banco de dados SQLite em memória
    engine = create_engine('sqlite:///:memory:')

    # Limpa os nomes das colunas para serem compatíveis com SQL
    # (Removendo espaços, parênteses, etc.)
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    df.to_sql(table_name, engine, index=False, if_exists='replace')

    # Cria uma instância do SQLDatabase da LangChain
    db = SQLDatabase(engine=engine)
    return db

def get_agent_executor():
    """
    Cria e retorna o agente executor que pode responder perguntas sobre o banco de dados.
    """
    # Inicializa o LLM (usando GPT-4o)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Conecta ao banco de dados em memória com os dados do XLSX
    db = get_db_connection()

    # Define o prompt do sistema para o agente
    AGENT_PREFIX = """
    Você é um agente de IA que atua como um analista de dados especialista em SQL.
    Sua tarefa é ajudar os usuários a obter insights respondendo às suas perguntas sobre os dados.
    Responda sempre em português.
    """

    # Cria o agente SQL
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,
        prefix=AGENT_PREFIX
    )

    return agent_executor