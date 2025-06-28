# popular_dados.py

import uuid
from datetime import date
from decimal import Decimal

# Importa a sessão do banco e todos os modelos necessários
from app.db.database import SessionLocal
from app.db.models import Usuario, Ticker, Indice, EventoCorporativo

def popular_dados_iniciais():
    """
    Insere dados iniciais essenciais no banco de dados se eles ainda não existirem.
    """
    db = SessionLocal()
    print("Iniciando a inserção de dados iniciais...")

    try:
        # --- 1. Criar um Usuário de Teste com Chave de API ---
        # Verifica se já existe um usuário de teste para não criar duplicado
        usuario_existente = db.query(Usuario).filter(Usuario.email == "usuario@teste.com").first()
        if not usuario_existente:
            api_key_unica = str(uuid.uuid4())
            novo_usuario = Usuario(
                nome="Usuário de Teste",
                email="usuario@teste.com",
                api_key=api_key_unica
            )
            db.add(novo_usuario)
            print("✅ Usuário de teste criado com sucesso!")
            print(f"🔑 Sua chave de API para testes é: {api_key_unica}")
        else:
            print("ℹ️  Usuário de teste já existe. Chave de API:", usuario_existente.api_key)

        # --- 2. Garantir que Tickers de Exemplo existam ---
        tickers_para_verificar = ["PETR4", "VALE3"]
        for ticker_code in tickers_para_verificar:
            ticker_existente = db.query(Ticker).filter(Ticker.codigo == ticker_code).first()
            if not ticker_existente:
                novo_ticker = Ticker(codigo=ticker_code, nome=f"Empresa {ticker_code}")
                db.add(novo_ticker)
                print(f"✅ Ticker de exemplo '{ticker_code}' criado.")

        # --- 3. Criar os Índices Principais ---
        indice_ibov = db.query(Indice).filter(Indice.nome == "IBOV").first()
        if not indice_ibov:
            ibov = Indice(nome="IBOV", valor_atual=Decimal("120000.00"), variacao_dia=Decimal("0.5"))
            db.add(ibov)
            print("✅ Índice IBOV de exemplo criado.")

        indice_ifix = db.query(Indice).filter(Indice.nome == "IFIX").first()
        if not indice_ifix:
            ifix = Indice(nome="IFIX", valor_atual=Decimal("3350.00"), variacao_dia=Decimal("-0.1"))
            db.add(ifix)
            print("✅ Índice IFIX de exemplo criado.")

        # --- 4. Criar Eventos Corporativos de Exemplo ---
        # Para garantir que não haja duplicatas, deletamos os antigos antes de inserir
        db.query(EventoCorporativo).filter(EventoCorporativo.ticker_codigo.in_(tickers_para_verificar)).delete(synchronize_session=False)

        eventos = [
            EventoCorporativo(ticker_codigo="PETR4", tipo_evento="DIVIDENDO", data_com=date(2024, 4, 25), data_pagamento=date(2025, 5, 20), valor=Decimal("0.5745")),
            EventoCorporativo(ticker_codigo="PETR4", tipo_evento="JCP", data_com=date(2023, 11, 21), data_pagamento=date(2024, 1, 15), valor=Decimal("0.6812")),
            EventoCorporativo(ticker_codigo="VALE3", tipo_evento="DIVIDENDO", data_com=date(2024, 3, 11), data_pagamento=date(2024, 3, 19), valor=Decimal("2.7386")),
        ]
        db.add_all(eventos)
        print("✅ Eventos corporativos de exemplo inseridos.")

        # Salva todas as alterações no banco de dados de uma vez
        db.commit()
        print("\nDados iniciais populados com sucesso no banco de dados!")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro ao popular o banco: {e}")
        db.rollback()
    finally:
        # Garante que a conexão seja sempre fechada
        db.close()

if __name__ == "__main__":
    popular_dados_iniciais()