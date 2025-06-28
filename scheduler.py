import schedule
import time
import logging

from app.scripts.collect_data import run_collection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__ == '__main__':
    logging.info("Agendador de Coleta de Dados iniciado.")
    
    schedule.every().day.at("03:00").do(run_collection)
    
    logging.info("Tarefa agendada. Próxima execução: " + str(schedule.next_run))

    while True:
        schedule.run_pending()
        time.sleep(60)