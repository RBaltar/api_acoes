import time
from sqlalchemy.exc import OperationalError
from app.db.database import engine
from app.db import models

from app.db.models import Ticker, HistoricoAcao, Indice, LogRequisicao, Usuario, EventoCorporativo

def create_database_tables():
    print("Iniciando a criação das tabelas no banco de dados...")

    try:
        time.sleep(2)
        
        print(f"Conectando ao banco de dados em: {engine.url}")
        models.Base.metadata.create_all(bind=engine)
        
        print("\n✅ Tabelas verificadas/criadas com sucesso!")
        print("   - tickers")
        print("   - acoes_historico")
        print("   - indices")
        print("   - usuarios")
        print("   - logs_requisicoes")
        print("   - eventos_corporativos  <-- Tabela de eventos adicionada!")

    except OperationalError as e:
        print("\n❌ Erro de conexão com o banco de dados.")
        print("   Por favor, verifique os seguintes pontos:")
        print("   1. O seu servidor PostgreSQL está em execução?")
        print("   2. As credenciais (usuário, senha, host, nome do banco) no arquivo .env estão corretas?")
        print(f"   Detalhes do erro: {e}")
    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado durante a criação das tabelas: {e}")

if __name__ == "__main__":
    create_database_tables()