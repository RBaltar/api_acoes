# scheduler.py

import schedule
import time
import logging

# O agendador agora só precisa importar e chamar a função principal da coleta.
from app.scripts.collect_data import run_collection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__ == '__main__':
    logging.info("Agendador de Coleta de Dados iniciado.")
    
    # Agenda a tarefa para rodar todos os dias no horário especificado
    schedule.every().day.at("03:00").do(run_collection)
    
    logging.info("Tarefa agendada. Próxima execução: " + str(schedule.next_run))

    while True:
        schedule.run_pending()
        time.sleep(60) # Verifica a cada minuto se é hora de rodar