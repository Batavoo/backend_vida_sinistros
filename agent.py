import os
import pandas as pd
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent

DB_FILE = "sinistros.db"

def get_db_connection(xls_file='sinistros_simplificado.xlsx', table_name='sinistros'):
    engine = create_engine(f'sqlite:///{DB_FILE}')
    df = pd.read_excel(xls_file)
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    df.to_sql(table_name, engine, index=False, if_exists='replace')
    db = SQLDatabase(engine=engine, sample_rows_in_table_info=0)
    return db

def get_agent_executor():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    db = get_db_connection()
    AGENT_PREFIX = """
    Você é um agente de IA que atua como um analista de dados especialista em SQL.
    Sua tarefa é ajudar os usuários a obter insights respondendo às suas perguntas sobre os dados.
    Responda sempre em português.
    """
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,
        prefix=AGENT_PREFIX
    )
    return agent_executor