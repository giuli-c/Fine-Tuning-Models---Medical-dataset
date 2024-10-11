import re

def convert_scientific_to_decimal(number_str):
    """
    Converte un numero in notazione scientifica a una stringa con notazione decimale standard.
    Se il numero non è in notazione scientifica, restituisce il numero originale.
    """
    try:
        # Converte la stringa in un numero float e poi di nuovo in stringa
        return '{:.5f}'.format(float(number_str))
    except ValueError:
        # Se il valore non è un numero valido, restituisce la stringa originale
        return number_str

def extract_epochs_from_filename(filename):
    pattern = r'\d+'    # il pattern di riferimento (struttura del nome del file) è \d (qualsiasi cifra da 0 a 9), + (una o più cifre) > in sintesi una o più cifre consecutive.
    epochs = [int(e) for e in re.findall(pattern, filename)] #scansiono il filename alla ricerca di tutte le sequenze di cifre che corrispondono al pattern \d+.
    return epochs