import logging
import os
import json
from .generation_table import process_model_files, load_base_files, create_score_table, create_response_table, dictionary_scores, create_response_dict, custom_latex

def enable_logging(level=logging.INFO):
    logging.basicConfig(level=level)
    return logging.getLogger(__name__)

logger = enable_logging()

def save_dict_as_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)  # indent=4 crea un'indentazione con 4 spazi
        # ensure_ascii=False: non convertire i caratteri speciali in sequenze di escape Unicode

def save_latex_as_tex(data, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(data)

def creazione_file(scores_dict, responses_dict, model_output_dir):
    #-----------------------------------------------------------------------------------------------
    # ------ FILE EXCEL
    #-----------------------------------------------------------------------------------------------
    # Creazione delle tabelle dai dizionari per il file xlsx
    logger.debug("Creazione delle tabelle per scores e responses")
    df_scores = create_score_table(scores_dict)

    # La prima colonna non ha nome. Inserisco l'indice per poterl poi modificare il nome della colonna 'index'
    df_scores = df_scores.reset_index()
    # Rinomico la colonna dell'indice come "Epoche"
    df_scores.rename(columns={'index': 'Epoche'}, inplace=True)

    responses_dict_json = create_response_dict(responses_dict)
    df_responses = create_response_table(responses_dict_json)    

    # Salvataggio dei DataFrame come file Excel
    logger.debug("Salvataggio dei DataFrame come file Excel")
    df_scores.to_excel(os.path.join(model_output_dir, "confronto_scores.xlsx"), index=False)
    df_responses.to_excel(os.path.join(model_output_dir, "confronto_responses.xlsx"), index=False)
    #-----------------------------------------------------------------------------------------------
    # ------ FILE JSON
    #-----------------------------------------------------------------------------------------------
    # Creazione del dictionary, nell'ordine corretto per la stampa del json
    logger.debug("Creazione delle tabelle per scores e responses")
    scores_json = dictionary_scores(scores_dict)
    #responses_json = dictionary_responses(dict_response)

    # Salvataggio dei DataFrame come file json
    logger.debug("Salvataggio dei dataframe come file JSON")
    save_dict_as_json(scores_json, os.path.join(model_output_dir, "confronto_scores.json"))
    save_dict_as_json(responses_dict_json, os.path.join(model_output_dir, "confronto_responses.json")) 
    #-----------------------------------------------------------------------------------------------
    # ------ FILE LATEX (.tex)
    #-----------------------------------------------------------------------------------------------
    # Trasformazione del codice in testo per latex
    latex_scores = df_scores.to_latex(index=False,
                                      column_format="|c|c|c|c|",
                                      header=True,
                                      bold_rows=True)
    
    latex_custom_scores = custom_latex(latex_scores)
    # Salvataggio del codice LaTeX in un file .tex
    save_latex_as_tex(latex_custom_scores, os.path.join(model_output_dir, "confronto_scores.tex"))
    
def main(models_dir, output_base_dir):
    print(f"Starting main function with models_dir: {models_dir} and output_base_dir: {output_base_dir}")
    #-------------------------------------------------------------------------------
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)
    #-------------------------------------------------------------------------------
    # Carico i valori di base (pre fine-tuning)
    #scores_dict, responses_dict = load_base_files(models_dir)
    #logger.debug(f"Dati di base caricati: {scores_dict.keys()}, {responses_dict.keys()}")



    # Loop attraverso le cartelle dei modelli
    for model_name in os.listdir(models_dir):
        # Ignora la cartella "Result"
        if model_name == "Result":
            continue

        logger.debug(f'>>>>>>>>> MODEL NAME: {model_name}')
        model_dir = os.path.join(models_dir, model_name)
        logger.debug(f'>>>>>>>>> MODEL DIR: {model_dir}')

        if os.path.isdir(model_dir):  # Verifica se è una directory
            # Carico i valori di base (pre fine-tuning) per ogni modello
            scores_dict, responses_dict = load_base_files(models_dir)
            logger.debug(f"Dati di base caricati per {model_name}: {scores_dict.keys()}, {responses_dict.keys()}")

            # Creo una sottocartella con il nome della cartella letta in Result (output_base_dir)
            model_output_dir = os.path.join(output_base_dir, model_name)            
            if not os.path.exists(model_output_dir):
                os.makedirs(model_output_dir)

            #-------------------------------------------------------------------------------
            # Cerco i file che contengono "scores" e "responses" nella sottocartella del modello
            scores_files = [f for f in os.listdir(model_dir) if "scores" in f and f.endswith('.xlsx')]
            responses_files = [f for f in os.listdir(model_dir) if "responses" in f and f.endswith('.xlsx')]

            process_model_files(model_dir, scores_dict, responses_dict, scores_files, responses_files)
            logger.debug(f"Processamento dei file del modello {model_name} completato")

            creazione_file(scores_dict, responses_dict, model_output_dir)    
    
            # Dopo la creazione dei file, rimuovo le chiavi dal dizionario che non appartengono al modello corrente
            keys_to_remove = [key for key in scores_dict if key != "Base" and key not in map(lambda x: x.split('_')[-1], scores_files)]
            for key in keys_to_remove:
                del scores_dict[key]

            keys_to_remove_responses = [key for key in responses_dict if key != "Base" and key not in map(lambda x: x.split('_')[-1], responses_files)]
            for key in keys_to_remove_responses:
                del responses_dict[key]
    
    #-------------------------------------------------------------------------------
    # Stampo i risultati per verifica
    # print("Scores Dictionary:")
    # for key, value in scores_dict.items():
    #     print(f"Epoche: {key}, Valori: {value}")
    
    # print("\nResponses Dictionary:")
    # for key, value in responses_dict.items():
    #     print(f"Epoche: {key}, Domande: {value['Questions'][:3]}, Risposte: {value['Responses'][:3]}")  # Mostra solo le prime 3 domande e risposte per brevità
