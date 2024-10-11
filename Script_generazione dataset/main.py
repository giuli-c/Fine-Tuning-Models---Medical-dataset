from script_dataset import APIService
import os
import pandas as pd
from tqdm import tqdm

if __name__ == "__main__":
    service = APIService()
    outputfile = "Output.csv"
    inputfile = os.path.join("data", "Domande.xlsx")
    
    #Leggi riga per riga del file xlsx di input e genera 10 domande ognuno con una risposta
    if os.path.exists(inputfile):
        df_input = pd.read_excel(inputfile)
    else:
        print("Il file non esiste")
        exit

    # Genera domande e risposte per ciascuna riga
    dataset = []
    for index, row in tqdm(df_input.iterrows(), total=df_input.shape[0]):
        question = row.iloc[0].strip()
        print("Lettura della domanda...")
        if question:
            new_questions = service.generate_questions(question, n=10)
            dataset.extend(new_questions)

    service.write_file(outputfile, dataset)
    print(f'Dati scritti con successo su {outputfile}')