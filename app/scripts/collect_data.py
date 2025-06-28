# app/scripts/collect_data.py

import requests
import pandas as pd
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import text

from app.db.database import SessionLocal
from app.db.models import Ticker, HistoricoAcao, ColetaLog

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def salvar_log_no_banco(db_session, mensagem: str, status: str = "INFO"):
    """Salva um log na tabela 'coleta_logs' de forma segura."""
    try:
        log_entry = ColetaLog(mensagem=mensagem, status=status)
        db_session.add(log_entry)
        db_session.commit()
    except Exception as e:
        logging.error(f"Falha ao salvar log no banco de dados: {e}")
        db_session.rollback()

class DataCollector:
    def __init__(self):
        self.db_session = SessionLocal()
        self.base_url = "https://statusinvest.com.br/acoes/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        logging.info("✅ Coletor de dados inicializado.")
    def get_tickers_from_db(self) -> list:
        logging.info("Buscando lista de tickers do banco de dados...")
        try:
            all_tickers_objects = self.db_session.query(Ticker).all()
            tickers_list = [ticker.codigo for ticker in all_tickers_objects]
            if not tickers_list:
                logging.warning("⚠️ Nenhum ticker encontrado no banco de dados para coletar dados.")
                return []
            logging.info(f"📊 {len(tickers_list)} tickers encontrados para monitoramento: {tickers_list}")
            return tickers_list
        except Exception as e:
            logging.error(f"❌ Erro ao buscar tickers do banco de dados: {e}")
            return []
    def fetch_stock_data(self, tickers: list) -> pd.DataFrame:
        all_data = []
        for ticker in tickers:
            try:
                url = f"{self.base_url}{ticker}"
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    logging.error(f"❌ Erro ao acessar {url}, código {response.status_code}")
                    continue
                soup = BeautifulSoup(response.text, "html.parser")
                def clean_value(value_str):
                    if not value_str: return None
                    try:
                        cleaned_str = value_str.replace("R$", "").strip().replace(".", "").replace("%", "").replace(",", ".")
                        return float(cleaned_str)
                    except (ValueError, AttributeError):
                        return None
                price_tag = soup.find("strong", class_="value")
                close_price = clean_value(price_tag.text) if price_tag else None
                indicators = {}
                indicator_elements = soup.find_all("h3", class_="title")
                for element in indicator_elements:
                    title = element.text.strip()
                    value_element = element.find_next_sibling("strong", class_="value")
                    if value_element:
                        indicators[title] = clean_value(value_element.text)
                stock_info = {"date": datetime.now().date(), "ticker": ticker, "close": close_price, "variacao_percentual": indicators.get("Variação (dia)"), "price_earnings": indicators.get("P/L"), "dividend_yield": indicators.get("Dividend Yield"), "roe": indicators.get("ROE"), "market_value": indicators.get("Valor de mercado"),"volume": indicators.get("Volume (média 21 dias)")}
                all_data.append(stock_info)
                logging.info(f"✅ Dados coletados para {ticker}")
            except Exception as e:
                logging.error(f"❌ Erro geral ao buscar dados de {ticker}: {e}")
        if all_data:
            return pd.DataFrame(all_data)
        else:
            logging.warning("⚠️ Nenhum dado válido encontrado para os tickers.")
            return pd.DataFrame()
    def save_to_database(self, df: pd.DataFrame):
        if df.empty:
            logging.warning(f"⚠️ Nenhum dado para salvar na tabela acoes_historico.")
            return
        try:
            engine = self.db_session.get_bind()
            df.to_sql("acoes_historico", engine, if_exists="append", index=False)
            logging.info(f"✅ Dados salvos na tabela acoes_historico com sucesso!")
        except Exception as e:
            logging.error(f"❌ Erro ao salvar dados no banco: {e}")


def run_collection():
    """
    Função principal que executa a coleta e agora também é responsável
    por registrar seus próprios logs de início e fim no banco de dados.
    """
    db = SessionLocal()
    try:
        salvar_log_no_banco(db, "🚀 Processo de coleta de dados iniciado.", "INFO")
        
        collector = DataCollector()
        collector.db_session = db 
        
        tickers_to_fetch = collector.get_tickers_from_db()
        
        if tickers_to_fetch:
            df_prices = collector.fetch_stock_data(tickers_to_fetch)
            collector.save_to_database(df_prices)
            salvar_log_no_banco(db, "✅ Processo de coleta finalizado com sucesso!", "SUCCESS")
            print("\n✅ Processo de coleta finalizado com sucesso!")
        else:
            msg = "ℹ️ Nenhum ticker no banco de dados para coletar. Processo não executado."
            salvar_log_no_banco(db, msg, "WARNING")
            print(f"\n{msg}")
            
    except Exception as e:
        msg_erro = f"❌ Erro crítico durante a execução da coleta: {e}"
        salvar_log_no_banco(db, msg_erro, "ERROR")
        logging.error(msg_erro, exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    run_collection()