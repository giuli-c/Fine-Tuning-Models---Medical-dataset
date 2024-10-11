import logging
import os
import glob
import pandas as pd

from .grafici import load_data_from_json, plot_metrics
from .grafici_confronto import load_data_from_json_confronto, extend_epochs

def enable_logging(level=logging.INFO):
    logging.basicConfig(level=level)
    return logging.getLogger(__name__)

logger = enable_logging

def main(models_dir, output_base_dir):
    df_all_data = pd.DataFrame

    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    # Creazione del grafico per ogni modello.
    # for model_name in os.listdir(models_dir):
    #     print('>>>>>>>>> MODEL NAME: ' + model_name)
    #     model_dir = os.path.join(models_dir, model_name)
    #     print('>>>>>>>>> MODEL DIR: ' + model_dir)

    #     if os.path.isdir(model_dir):    #verifica se è una directory
    #         #prendo tutti i file json della sottocartella del modello
    #         json_files = glob.glob(os.path.join(model_dir, '*.json'))

    #         if not json_files:
    #             print(f"Nessun file JSON trovato nella directory {model_dir}. Continuo con la prossima directory.")
    #             continue

    #         # Carica i dati dai file JSON
    #         df = load_data_from_json(json_files)

    #         # Directory di output per i grafici del modello corrente
    #         output_dir = os.path.join(output_base_dir, model_name)

    #         if not os.path.exists(output_dir):
    #             os.makedirs(output_dir)

    #         # Crea i grafici per confrontare le metriche
    #         if plot_metrics(df, output_dir, model_name):
    #             print("CREATO GRAFICO PER " + model_name)

    # Creazione del grafico per ogni metrica con modelli a confronto.
    for model_name in os.listdir(models_dir):
        print('>>>>>>>>> MODEL NAME: ' + model_name)
        model_dir = os.path.join(models_dir, model_name)
        print('>>>>>>>>> MODEL DIR: ' + model_dir)

        if os.path.isdir(model_dir):    #verifica se è una directory
            #prendo tutti i file json della sottocartella del modello
            json_files = glob.glob(os.path.join(model_dir, '*.json'))

            if not json_files:
                print(f"Nessun file JSON trovato nella directory {model_dir}. Continuo con la prossima directory.")
                continue

            # Carica i dati dai file JSON
            bAddEpochs = False
            df_model = load_data_from_json_confronto(json_files, model_name, bAddEpochs)

            if bAddEpochs:
                df_concat = extend_epochs(df_model)
                df_model = df_concat

            df_all_data = pd.concat([df_all_data, df_model], ignore_index=True)

    print("DATAFRAME A CONFRONTO:")
    print(df_all_data)

    # Directory di output per i grafici del modello corrente
    output_dir_tot = os.path.join(output_base_dir, "Confronto_modelli")

    if not os.path.exists(output_dir_tot):
        os.makedirs(output_dir_tot)

    # Creazione dei grafici per il confronto tra modelli per ogni metrica
    #if plot_metrics(df, output_dir_tot):
    #    print("CONFRONTO GRAFICI CREATI. ")