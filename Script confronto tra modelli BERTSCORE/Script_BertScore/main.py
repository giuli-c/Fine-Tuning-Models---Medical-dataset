import argparse
from . import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generazione di tabelle per confronto di BertScore')
    parser.add_argument('--models-dir', type=str, required=True, help='Directory dei modelli contenente i file JSON.')
    parser.add_argument('--output-dir', type=str, required=True, help='Directory di output per i grafici.')

    args = parser.parse_args()
    print(">>>> CARTELLA DI BASE " + args.models_dir + " CARTELLA OUTPUT" +  args.output_dir)

    main(args.models_dir, args.output_dir)

#python main.py --models-dir /path/to/models --output-dir /path/to/output