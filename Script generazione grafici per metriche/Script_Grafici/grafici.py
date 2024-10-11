import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .generali import extract_epochs_from_filename, convert_scientific_to_decimal

# Carico i dati dal file jsonF
def load_data_from_json(files):
    data = []
    metrics_interested = {'loss', 'token_accuracy', 'next_token_perplexity'}

    for file in files:
        epochs = extract_epochs_from_filename(os.path.basename(file))
        # -------------------------------------------------------------------------
        # Estraggo le info da un file JSON creando un dictionary per ogni modello.
        # Struttura del file json:
        #{
        #     "evaluation_frequency": {
        #         "frequency": 1,
        #         "period": "epoch"
        #     },
        #     "test": {
        #         "RISPOSTE": {
        #             "loss": [
        #                 1.0456860065460205 
        #         ],
        #             "next_token_perplexity": [
        #                 15994.330078125 
        #         ],
        #             "perplexity": [
        #                 31805.76953125 
        #         ],
        #             "sequence_accuracy": [
        #                 0.0
        #             ],
        #             "token_accuracy": [
        #                 0.00014350346464198083
        #             ]
        #         },
        #         "combined": {
        #             "loss": [
        #                 0.7709579467773438
        #             ]
        #         }
        #     },
        #     "training": {
        #         "RISPOSTE": {
        #             "loss": [
        #                 0.638498067855835
        #             ],
        #             "next_token_perplexity": [
        #                 14753.2021484375
        #             ],
        #             "perplexity": [
        #                 31705.345703125
        #             ],
        #             "sequence_accuracy": [
        #                 0.0
        #             ],
        #             "token_accuracy": [
        #                 0.00010560621012700722
        #             ]
        #         },
        #         "combined": {
        #             "loss": [
        #                 0.638498067855835
        #             ]
        #         }
        #     },
        #     "validation": {
        #         "RISPOSTE": {
        #             "loss": [
        #                 0.7538256049156189
        #             ],
        #             "next_token_perplexity": [
        #                 15146.62109375
        #             ],
        #             "perplexity": [
        #                 31712.181640625
        #             ],
        #             "sequence_accuracy": [
        #                 0.0
        #             ],
        #             "token_accuracy": [
        #                 8.444133709417656e-05
        #             ]
        #         },
        #         "combined": {
        #             "loss": [
        #                 0.7538256049156189
        #             ]
        #         }
        #     }
        # }
        # -------------------------------------------------------------------------
        with open(file, 'r') as f:
            json_data = json.load(f)
            # NOME DEL FILE senza percorso completo.
            test_name = os.path.basename(file).replace('.json', '')
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
                                'test' : test_name,
                                'epoch' : int(epoch),
                                'dataset' : dataset,
                                'metric' : metric,
                                'value' : value_convert
                            })
            # ---------------------------------------------------------------------
    df = pd.DataFrame(data)
    return df

# Creazione dei garfici
def plot_metrics(df, output_dir, model_name):
    try:
        sns.set(style="whitegrid")

        # Assicurati che il DataFrame contenga le colonne attese
        print("Colonne del DataFrame:", df.columns)

        # Definisci una palette di colori per i tre dataset
        palette = {"test": "blue", "training": "green", "validation": "orange"}
        
        print("------------- LOSSS HEAD()")
        print(df[df['metric'] == 'loss'])

        unique_epochs = sorted(df['epoch'].unique())

        # LOSS
        plt.figure(figsize=(14, 8))
        sns.lineplot(
            data=df[df['metric'] == 'loss'], 
            x='epoch', 
            y=df[df['metric'] == 'loss']['value'],
            hue='dataset', 
            style='dataset', 
            markers=True, 
            dashes=False, 
            palette=palette,
            linewidth=2.5
        )
        plt.title('Andamento della Loss per il modello' + model_name, fontsize = 24, pad = 20)
        plt.xlabel('Epoca', fontsize=18)
        plt.ylabel('Loss', fontsize=18)
        plt.gca().xaxis.label.set_size(16)
        plt.gca().yaxis.label.set_size(16)
        plt.gca().xaxis.labelpad = 15  # spazio all'etichetta dell'asse x
        plt.gca().yaxis.labelpad = 15  # spazio all'etichetta dell'asse y
        plt.legend(loc='upper right', fontsize=18)
        plt.xticks(ticks=unique_epochs, fontsize=18)  # Font degli assi più grande
        plt.yticks(fontsize=18)  # Font degli assi più grande
        plt.savefig(os.path.join(output_dir, 'Andamento_Loss_'+ model_name +'.png'))
        plt.close()

        # Perplexity
        print("------------- PERPLEXITY HEAD()")
        print(df[df['metric'] == 'next_token_perplexity'])

        plt.figure(figsize=(14, 8))
        sns.lineplot(
            data=df[df['metric'] == 'next_token_perplexity'],
            x='epoch', 
            y=df[df['metric'] == 'next_token_perplexity']['value'], 
            hue='dataset', 
            style='dataset', 
            markers=True, 
            dashes=False, 
            palette=palette,
            linewidth=2.5
        )
        plt.title('Andamento della Perplexity per il modello ' + model_name, fontsize = 24, pad = 20)
        plt.xlabel('Epoca', fontsize=18)
        plt.ylabel('Perplexity', fontsize=18)
        plt.gca().xaxis.label.set_size(16)
        plt.gca().yaxis.label.set_size(16)
        plt.gca().xaxis.labelpad = 15  # spazio all'etichetta dell'asse x
        plt.gca().yaxis.labelpad = 15  # spazio all'etichetta dell'asse y
        plt.legend(loc='upper right', fontsize=18)
        plt.xticks(ticks=unique_epochs, fontsize=18)  # Font degli assi più grande
        plt.yticks(fontsize=18)  # Font degli assi più grande
        plt.savefig(os.path.join(output_dir, 'Andamento_Perplexity_'+ model_name +'.png'))
        plt.close()

        # Accuratezza dei Token
        print("------------- token_accuracy HEAD()")
        print(df[df['metric'] == 'token_accuracy'])

        
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        plt.figure(figsize=(14, 8))
        sns.lineplot(
            data=df[df['metric'] == 'token_accuracy'], 
            x='epoch', 
            y=df[df['metric'] == 'token_accuracy']['value'], 
            hue='dataset', 
            style='dataset', 
            markers=True, 
            dashes=False, 
            palette=palette,
            linewidth=2.5
        )

        plt.title('Andamento della Token Accuracy per il modello ' + model_name, fontsize = 24, pad = 20)
        plt.xlabel('Epoca', fontsize=18)
        plt.ylabel('Token Accuracy', fontsize=18)
        plt.gca().xaxis.label.set_size(16)
        plt.gca().yaxis.label.set_size(16)
        plt.gca().xaxis.labelpad = 15  # spazio all'etichetta dell'asse x
        plt.gca().yaxis.labelpad = 15  # spazio all'etichetta dell'asse y
        plt.legend(loc='upper right', fontsize=18)
        plt.xticks(ticks=unique_epochs, fontsize=18)  # Font degli assi più grande
        plt.yticks(fontsize=18)  # Font degli assi più grande
        plt.savefig(os.path.join(output_dir, 'Andamento_TokenAccuracy_'+ model_name +'.png'))
        plt.close()
        
        return True  
    except Exception as e:
        print(f"Errore durante la creazione dei grafici: {e}")
        return False  