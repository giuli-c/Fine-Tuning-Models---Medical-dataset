import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .generali import extract_epochs_from_filename, convert_scientific_to_decimal

metrics_interested = {'loss', 'token_accuracy', 'next_token_perplexity'}

# Carico i dati dal file jsonF
def load_data_from_json_confronto(files, model_name, bAddEpochs):
    data = []
    epochs_tot = [1,2,3,4,5,6,80,90,100,110,120,130]

    for file in files:
        # -------------------------------------------------------------------------
        with open(file, 'r') as f:
            epochs = extract_epochs_from_filename(os.path.basename(file))

            if len(epochs) < len(epochs_tot):  # sono su Mistral e Biomistral che ha solo 6 epoche assegno un valore vuoto
                bAddEpochs = True

            json_data = json.load(f)
            # NOME DEL FILE senza percorso completo.
            #test_name = os.path.basename(file).replace('.json', '')
            # ------------------------------------------------------------------
            # itero su tutte le key del dictionary (training, validation, test)
            # ------------------------------------------------------------------
            for dataset in json_data.keys():         
                print('*********** DATASET: ' + dataset)
                if 'RISPOSTE' not in json_data[dataset]:    #Non entro nella prima key così
                    continue
                # --------------------------------------------------
                # Itero solo sulle metriche mi interessano (lista > json_data nella sezione risposte)
                # --------------------------------------------------
                for metric in metrics_interested:                     
                    if metric in json_data[dataset]['RISPOSTE']:    # controllo se esiste nella sezione risposte del dataset
                        # -------------------------------------------------------------------------------------------------------
                        # creo un dataset tabellare per associare ogni epoca con il valore della metrica corrispondente
                        # zip() combina due (o più) liste in modo da creare coppie di elementi.
                        # In questo caso, prende la lista delle epoche (epochs) e la lista dei valori della metrica corrispondenti e le unisce.
                        # -------------------------------------------------------------------------------------------------------
                        for epoch, value in zip(epochs, json_data[dataset]['RISPOSTE'][metric]): # usa le epoche estratte dal nome del file #in enumerate(json_data[dataset]['RISPOSTE'][metric], start=1): # itero attraverso i valori della metrica, per ogni epoca (start1 = epoca parte da 1 e non da 0)
                            if metric == 'token_accuracy':                                
                                value_convert = convert_scientific_to_decimal(value)
                            if metric == 'next_token_perplexity':
                                value_convert = int(value)
                            else:
                                value_convert = value
                            data.append({
                                'model' : model_name,
                                'epoch' : int(epoch),
                                'dataset' : dataset,
                                'metric' : metric,
                                'value' : value_convert
                            })
            # ---------------------------------------------------------------------
    df = pd.DataFrame(data)
    print(df)
    return df

def extend_epochs(df):
    """
    Aggiunge le epoche 80, 90, 100, 110, 120, 130 con valori a 0, per le metriche che non le hanno nei DataFrame.
    """
    extended_data = []
    additional_epochs=[80, 90, 100, 110, 120, 130]

    for metric in metrics_interested:
        for epoch in additional_epochs:
            # Aggiungi le epoche mancanti con valore 0
            extended_data.append({
                'epoch': epoch,
                'metric': metric,
                'value': 0,
                'model': df['model'].iloc[0],  # Aggiungi il nome del modello
                'dataset': 'extended'
            })

    # Converti i dati aggiuntivi in DataFrame
    extended_df = pd.DataFrame(extended_data)
    
    # Concatena i dati originali con i dati estesi
    return pd.concat([df, extended_df], ignore_index=True)