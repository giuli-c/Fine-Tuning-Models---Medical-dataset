import openai
import openai.error
import time
import pandas as pd
import os
import csv
from decouple import config

#self, mi permette di definirli come metodi di istanza.
class APIService():
    def __init__(self):
        openai.api_key = config("OPENAI_API_KEY")

    def generate_questions(self, question, n=10):
        #lo uso anche per tenere traccia di domande e risposte
        dataset = []
        questions =set()
        questions.add(question)
        answers = set()

        print("Generazione della risposta, alla domanda: ", question)
        new_answer = self.generate_response(question)
        dataset.append({"DOMANDE": question, "RISPOSTE": new_answer})
        answers.add(new_answer)
        print(dataset)

        # creo una lista vuota (registro di chat)
        #+ aggiungo un prompt al chatlog
        

        while len(questions) < n + 1:
            chat_log = [{"role": "system",
                         "content": "Potresti riformulare le frasi che ti passo, in modo che siano di senso compiuto, veritiere e non uguali a quelle precedentemente generate? \
                                     Segui l' esempio qua sotto per capire come la domanda deve essere riformulata: \
                                     DOMANDA: È buon segno che la frequenza cardiaca sia più alta del solito? \
                                     DOMANDE RIFORMULATA: È normale che la mia frequenza cardiaca sia superiore al solito?"},
                        {"role": "user",
                         "content": f"Mi potresti riformulare la seguente domanda in modo che non sia uguale alle riformulazioni precedenti? {question}"}
                       ]
            response = openai.ChatCompletion.create(
                model="gpt-4o",  
                messages = chat_log,  
                max_tokens=40,
                n=1,
                stop=None,
                temperature=0.8,
            )


            print("Generazione della domanda: ", len(questions))

            new_questions = response.choices[0].message.content.strip()
            
            if new_questions not in questions:
                questions.add(new_questions)

                new_answer = self.generate_response(new_questions)
                #dataset.append({"DOMANDE": new_questions, "RISPOSTE": answer})
                # Verifica se la nuova risposta è un duplicato
                if new_answer not in answers:
                    dataset.append({"DOMANDE": new_questions, "RISPOSTE": new_answer})
                    answers.add(new_answer)
                    # Aggiorna il chat_log con la nuova domanda e risposta per mantenere il contesto
                    chat_log.append({'role': 'assistant', 'content': new_questions})
                    chat_log.append({'role': 'assistant', 'content': new_answer})

        # Filtra l'output per includere solo le domande e risposte pertinenti
        filtered_dataset = [{"DOMANDE": entry["DOMANDE"], "RISPOSTE": entry["RISPOSTE"]} for entry in dataset if "Mi potresti riformulare" not in entry["DOMANDE"]]

        return filtered_dataset

    def generate_response(self, new_questions):
        try:
            response = openai.ChatCompletion.create(
                    model="gpt-4o",  
                    messages=[
                            {"role": "system", "content": "Sei un assistente virtuale."},                
                            {"role": "user", "content": f"In qualità di esperto di ipertensione e cardiologia, dovresti rispondere alle richieste dei pazienti per fornire diagnosi o consigli empatici. \
                                                        Le risposte devono essere empatiche, di senso compiuto e LE FRASI DEVONO TERMINARE CON UN PUNTO. \
                                                        Segui l'esempio di come è stata data la risposta alla seguente domanda: \
                                                        DOMANDA: Come posso migliorare il monitoraggio dei dati della mia frequenza cardiaca? \
                                                        RISPOSTA: Assicurati di calibrare regolarmente i tuoi dispositivi e di verificare la loro precisione confrontandoli con metodi di misurazione tradizionali, come l'uso di un cronometro e la palpazione del polso. \
                                                        {new_questions}"}
                    ],    
                    max_tokens=60,
                    n=1,
                    stop=None,
                    temperature=0.8,
                )

            answer = response.choices[0].message.content.strip()

            #Codice per controllare che la frase termini con un punto e sia di senso compiuto. In caso contrario continuo la risposta.
            #retries = 0
            while not self.is_sentence_complete(answer):  # Add a retry limit
                # Se la frase non è completa, chiedi al modello di continuare la generazione
                answer += self.continue_answer(answer)
                #retries += 1

            if not self.is_sentence_complete(answer):
                answer = ""
                self.generate_response(new_questions)

            return answer
        except openai.error.RateLimitError as e:
            print(f"Rate limit error: {e}. Retrying in 1 second...")
            time.sleep(1)  # Aspetta 1 secondo prima di riprovare
            return self.generate_response(new_questions)

    def is_sentence_complete(self, sentence):
        # Controllo se la frase termina con un segno di punteggiatura
        return sentence[-1] in '.!?'
    
    def continue_answer(self, sentence):
        completion_prompt = f"Continua la frase fino ad un punto per terminare la frase: {sentence}"
        continuation = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei un assistente virtuale, attento ai segni di punteggiatura."},
                {"role": "user", "content": completion_prompt}
            ],
            max_tokens=10,
            temperature=0.9
        )
        return continuation.choices[0].message['content'].strip()
    
    def write_file(self, outputfile, data):
        #controllo se il file di output esiste
        file_ok = os.path.isfile(outputfile)

        with open(outputfile, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ["DOMANDE", "RISPOSTE"]
            writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

            # Se il file non esiste, scrivi l'intestazione
            if not file_ok:
                writer.writeheader()

            #scrivo la nuova riga
            for row in data:
                writer.writerow(row)


        

