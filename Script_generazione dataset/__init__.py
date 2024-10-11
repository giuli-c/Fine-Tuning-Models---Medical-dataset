import argparse
import os
import csv
import logging
from script_dataset import generate_question

# Definizione della funzione enable_logging
def enable_logging(level=logging.INFO):
    logging.basicConfig(level=level)
    return logging.getLogger(__name__)

# Configurazione dei log
LOG_INFO = logging.INFO
logger = enable_logging(level=LOG_INFO)
LATEX_FLOAT_PRECISION = 2

# Creazione del parser di argomenti da linea di comando
parser = argparse.ArgumentParser(description='Generation question & answer.')
# Se non specifico il percorso viene caricato dal percorso di default,
# altrimenti: python script_dataset.py --data-file /path/to/your/alternative.csv
parser.add_argument('--question-file', type=str, default='./data/Domande.csv', help='input file path')
parser.add_argument('--dataset-file', type=str, default='./data/DataSet.csv', help='output file path')

if __name__ == '__main__':
    args = parser.parse_args()
    #apertura del file(definizione del percorso assoluto: garantisco che il percorso sia corretto e completo)
    with open(os.path.abspath(args.question_file), 'r') as question_file:
        logger.info(f'Loading questions...')
        #reader = csv.reader(question_file)
        questions = []
        for line in question_file:
            questions = generate_question(questions, line, n=10)