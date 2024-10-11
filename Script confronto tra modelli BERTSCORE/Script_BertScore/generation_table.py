import os
import pandas as pd
import matplotlib.pyplot as plt
import re

def load_base_files(models_dir):
    #-------------------------------------------------------------------------------
    # Carico i file pre-fine-tuning per "scores" e "responses"
    pre_scores_df = None
    pre_responses_df = None    
    for file_name in os.listdir(models_dir):
        if "scores" in file_name:
            pre_scores_df = os.path.join(models_dir, file_name)  # pre_scores_df = "models_dir/pre_fine_tuning_scores.xlsx".
        elif "responses" in file_name:
            pre_responses_df = os.path.join(models_dir, file_name)

    if not pre_scores_df or not pre_responses_df:
        raise FileNotFoundError("File di base pre-fine-tuning non trovati nella cartella principale.")
    #-------------------------------------------------------------------------------
    # lettura dei file
    pre_scores_df = pd.read_excel(pre_scores_df)
    pre_responses_df = pd.read_excel(pre_responses_df)
    #-------------------------------------------------------------------------------
    # lettura di mean precision (C'è dello spazio quindi va gestito)
    mean_precision = pre_scores_df.get("Mean_Precision")
    if mean_precision is not None:
        mean_precision_value = mean_precision.values[0]
        print(f"Mean-Precision: {mean_precision_value}")
    else:
        print("La colonna 'Mean-Precision' non è stata trovata.")
    #-------------------------------------------------------------------------------
    # Creazione dei due dizionari per salvare i dati di base
    scores_dict = {
        "Base": {
            "Mean Precision": mean_precision_value,
            "Mean Recall": pre_scores_df["Mean_Recall"].values[0],
            "Mean F1": pre_scores_df["Mean_F1"].values[0]
        }
    }
    responses_dict = {
        "Base": {
            "Questions": list(pre_responses_df["DOMANDE"]),
            "Responses": list(pre_responses_df["RISPOSTE_GENERATE"]),
            "Original Responses": list(pre_responses_df["RISPOSTE_ORIGINALI"])
        }
    }
    #-------------------------------------------------------------------------------
    return scores_dict, responses_dict

def extract_tensor_value(tensor_str):
    # Usa una regex per estrarre il valore all'interno di 'tensor()'
    match = re.search(r'tensor\(([\d.]+)\)', tensor_str)
    if match:
        return float(match.group(1))
    else:
        return tensor_str

def get_scores(scores_df):
    #-------------------------------------------------------------------------------
    # Ottiengo l'ultima riga di ogni colonna
    mean_precision_tensor = scores_df["Precision"].iloc[-1]
    mean_recall_tensor = scores_df["Recall"].iloc[-1]
    mean_f1_tensor = scores_df["F1"].iloc[-1]
    #-------------------------------------------------------------------------------
    if isinstance(mean_precision_tensor, (int, float)) or isinstance(mean_recall_tensor, (int, float)) or isinstance(mean_f1_tensor, (int, float)):
        mean_precision_value = mean_precision_tensor
        mean_recall_value = mean_recall_tensor
        mean_f1_value = mean_f1_tensor
    else:
        # Estraggo i valori numerici dai tensor
        mean_precision_value = extract_tensor_value(mean_precision_tensor)
        mean_recall_value = extract_tensor_value(mean_recall_tensor)
        mean_f1_value = extract_tensor_value(mean_f1_tensor)    
    #-------------------------------------------------------------------------------
    return mean_precision_value, mean_recall_value, mean_f1_value

def createDictionaryXLSX(bResponses, n_epochs, df, dict_xlxs):    
    if bResponses:
        #-------------------------------------------------------------------------------
        dict_xlxs[n_epochs] = {
            "Questions": list(df["DOMANDE"]),
            "Responses": list(df["RISPOSTE_GENERATE"])
        }
    else:
        #-------------------------------------------------------------------------------
        # Debug: Stampa i nomi delle colonne
        #print(f"Nomi delle colonne per {n_epochs}: {df.columns}")
        # # Stampa il DataFrame completo
        # print("DataFrame completo:")
        # print(df)  
        #-------------------------------------------------------------------------------
        mean_precision_value, mean_recall_value, mean_f1_value =  get_scores(df)
        dict_xlxs[n_epochs] = {
            "Mean Precision": mean_precision_value,
            "Mean Recall": mean_recall_value,
            "Mean F1": mean_f1_value
        }        

def dictionary_scores(dict_scores):
    # lambda x è una funzione
    # x.isdigit() verifica se x è composto solo da cifre, True -> lo trasforma in un intero 
    # | False -> lo straforma in float('inf'), ovvero in un infinito positivo. In questo modo viene messo al primo posto.
    sorted_epochs = sorted(dict_scores.keys(), key=lambda x: (x != "Base", int(x) if x.isdigit() else float('inf')))

    # dict.items(restituisce coppia (epoca, valore))
    scores_json = {
        "Mean Precision": {epoch:  dict_scores[epoch]["Mean Precision"] for epoch in sorted_epochs},
        "Mean Recall": {epoch:  dict_scores[epoch]["Mean Recall"] for epoch in sorted_epochs},
        "Mean F1": {epoch:  dict_scores[epoch]["Mean F1"] for epoch in sorted_epochs},
    }
    return scores_json

def extract_relevant_response(full_response):
    # Cerca la stringa di delimitazione e ottieni tutto ciò che segue
    full_response = full_response.strip()
    delimiter = "### Risposta (Assicurati che la tua risposta termini con un punto e abbia senso compiuto):".strip()
    if delimiter in full_response:
        relevant_response = full_response.split(delimiter)[-1].strip()
    else:
        relevant_response = full_response.strip()  # Se la stringa non è trovata, restituisci l'intera risposta
    
    return relevant_response

def process_model_files(models_dir, scores_dict_xlxs, responses_dict_xlxs, scores_files, responses_files):
    #-------------------------------------------------------------------------------
    # Processo i file scores
    for scores_file in scores_files:
        scores_file_path = os.path.join(models_dir, scores_file)
        scores_df = pd.read_excel(scores_file_path)

        n_epochs = scores_file.split('_')[-1].replace('.xlsx', '')  # Estrai il numero di epoche dal nome del file

        createDictionaryXLSX(False, n_epochs, scores_df, scores_dict_xlxs)
    print("DICTIONARY SCORES COMPLETATO.")
    #-------------------------------------------------------------------------------
    # Processo i file responses
    for responses_file in responses_files:
        responses_file_path = os.path.join(models_dir, responses_file)
        responses_df = pd.read_excel(responses_file_path)
        n_epochs = responses_file.split('_')[-1].replace('.xlsx', '')  # Estrai il numero di epoche dal nome del file

        createDictionaryXLSX(True, n_epochs, responses_df, responses_dict_xlxs)
    print("DICTIONARI RESPOSNSES COMPLETATO.")

def create_score_table(scores_dict):
    #-------------------------------------------------------------------------------
    # Creazione della tabella per i punteggi
    df_scores = pd.DataFrame(scores_dict).T
    #-------------------------------------------------------------------------------
    # Separare la riga "Base" dalle altre per ordinare solo gli epoch numerici
    base_row = df_scores.loc['Base']    # estrae la riga che ha l'indice "Base".
    epoch_df = df_scores.drop('Base')   # rimuove la riga con l'indice "Base" dal DataFrame, creandone uno nuovo.
    
    # Converto l'indice delle epoche a numerico per ordinamento
    epoch_df.index = epoch_df.index.astype(int)    
    # Ordino le epoche in ordine crescente
    epoch_df = epoch_df.sort_index()    
    # Reinserisco la riga "Base" in cima
    df_scores_sorted = pd.concat([pd.DataFrame(base_row).T, epoch_df])
    #-------------------------------------------------------------------------------
    return df_scores_sorted

def create_response_dict(responses_dict):
    # Inizio con le domande di base
    # SET: trasformo la lista di domande ("Questions") contenuta nel dizionario responses_dict, sotto la chiave "Base" in un insieme. 
    # In questo modo verranno rimossi i duplicati se presenti.
    base_questions = set(responses_dict["Base"]["Questions"])
    #-------------------------------------------------------------------------------
    # Trovo l'intersezione di domande comuni a tutte le epoche.
    # EPOCHE = key, chiave del dizionario.
    # risultato:  'base_questions' conterrà solo le domande che sono presenti in tutte le epoche nel dizionario.
    # ESEMPIO: 
    # base: ["Domanda1", "Domanda2", "Domanda3"], epoch_110: ["Domanda2", "Domanda3", "Domanda4"], epoch_120: ["Domanda3", "Domanda4", "Domanda5"]
    # iterazione 1: base_questions = {"Domanda1", "Domanda2", "Domanda3"}
    # iterazione 2: base_questions = {"Domanda2", "Domanda3"}
    # iterazione 3: base_questions = {"Domanda3"} >> Unica in comune
    for epoch in responses_dict.keys():
        base_questions &= set(responses_dict[epoch]["Questions"])
    #-------------------------------------------------------------------------------
    # Considero solo le domande comuni.
    # Nuova lista ordinata in ordine alfabetico.
    common_questions = sorted(list(base_questions))    
    response_data = []
    # ******************************************************************
    # Creo un nuovo dictionary per ogni domanda.
    # ESEMPIO:
    # responses_dict = {
    #     "Base": {
    #         "Questions": [Dom1, Dom2, Dom3],
    #         "Original Responses": [Risp_Orig1, Risp_Orig2, Risp_Orig3],
    #         "Responses": [Risp1_Base, Risp2_Base, Risp3_Base]
    #     },
    #     "110": {
    #         "Questions": [Dom1, Dom2, Dom3].
    #         "Responses": [Risp1_110, Risp2_110, Risp3_110]
    #     },
    #     "120": {
    #         "Questions": [Dom1, Dom2, Dom3],
    #         "Responses": [Risp1_120, Risp2_120, Risp3_120]
    #     }
    # }
    # >>> RESULT:
    # {
    #     "Domanda": "Dom1",
    #     "Risposta Originale": "Risp_Orig1",
    #     "Risposta Base": "Risp1_Base",
    #     "Risposta 80 epoche": "Risp1_110",
    #     "Risposta 90 epoche": "Risp1_120"
    # }
    # {
    #     "Domanda": "Dom2",
    #     "Risposta Originale": "Risp_Orig2",
    #     "Risposta Base": "Risp2_Base",
    #     "Risposta 80 epoche": "Risp2_110",
    #     "Risposta 90 epoche": "Risp2_120"
    # }
    # .....
    # ******************************************************************
    for question in common_questions:
        # Aggiungo una colonna per le risposte originali
        # Risposta Originale/Base: prendo la risposta originale associata a quella domanda dal dizionario con key "Base" (La riga corretta viene trovata utilizzando responses_dict["Base"]["Questions"].index(question), che cerca l'indice della domanda nella lista delle domande di base.)
        modello_response = extract_relevant_response(responses_dict["Base"]["Responses"][responses_dict["Base"]["Questions"].index(question)])
        response_row = {
            "Domanda": question,
            "Risposta Modello Base": modello_response,
            "Risposta Dataset": responses_dict["Base"]["Original Responses"][responses_dict["Base"]["Questions"].index(question)]            
        }
        #-------------------------------------------------------------------------------
        # Ordino le epoche, assicurandoti che "Base" sia sempre per prima, seguita dalle epoche in ordine crescente
        sorted_epochs = sorted(
            responses_dict.keys(), 
            key=lambda x: (x != "Base", int(x) if x.isdigit() else float('inf'))
        )
        #-------------------------------------------------------------------------------
        for epoch in sorted_epochs:
            if epoch != "Base":
                # Aggiungo la risposta per l'epoca corrente
                response_row[f"Risposta {epoch} epoche"] = responses_dict[epoch]["Responses"][responses_dict[epoch]["Questions"].index(question)]
        #-------------------------------------------------------------------------------
        response_data.append(response_row)
    return response_data

def create_response_table(response_data):
    #-------------------------------------------------------------------------------
    # Creazione del DataFrame
    df_responses = pd.DataFrame(response_data)
    #-------------------------------------------------------------------------------
    return df_responses

def custom_latex(latex_code):
    # Aggiungi manualmente alcune personalizzazioni, come il colore delle intestazioni
    latex_custom = r"""
\renewcommand{\arraystretch}{1.7}  % Aumenta lo spazio tra le righe (1.7 è il fattore di scala)

\centering
\begin{tabularx}{\textwidth}{|>{\centering\columncolor{blue!20}}p{1.7cm}|>{\centering\arraybackslash}X|>{\centering\arraybackslash}X|>{\centering\arraybackslash}X|}   % fisso la dimensione della colonna 1 e centro il nome in tutte
\hline
\rowcolor{blue!30}  % Colora la prima riga (intestazione)
""" + latex_code.replace(
    r'\toprule', r'\hline'
).replace(
    r'\midrule', r'\hline'
).replace(
    r'\bottomrule', r'\hline'
).replace(
    r'Epoche', r'\fontsize{13}{14}\textbf{Epoche}'
).replace(
    r'Mean Precision', r'\fontsize{13}{14}\textbf{Mean Precision}'
).replace(
    r'Mean Recall', r'\fontsize{13}{14}\textbf{Mean Recall}'
).replace(
    r'Mean F1', r'\fontsize{13}{14}\textbf{Mean F1}'
).replace(
    r'\\', r'\\ \fontsize{12}{12}\selectfont'
) + r"""
\end{tabularx}
"""

    return latex_custom