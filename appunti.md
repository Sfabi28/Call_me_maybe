# step 1

parsare  e validare i due file 'functions_definition.json' 'function_calling_tests.json' utilizzando pydantic

# step 2

creare un mega prompt in cui viene spiegato cosa deve fare e gli argomenti da usare, ci deve essere un unico prompt per domanda, quindi mettere tutto in un ciclo.

1) far capire all'AI il suo obiettivo, per esempio: "Sei un assistente automatico progettato per estrarre informazioni e chiamare funzioni. Non devi rispondere alle domande dell'utente, ma devi solo selezionare la funzione corretta e i parametri necessari."

2) pasargli le funzioni che lui ha a disposizione, per esempio: "Ecco la lista delle funzioni a tua disposizione, con i rispettivi parametri e tipi di dato:", seguito dal testo presente nel JSON

3) aggiungere la richiesta dell'utente, per esempio: "Richiesta dell'utente: 'Qual è la somma di 2 e 3?'"

4) dirgli cosa generare, per esempio: "Genera SOLO un oggetto JSON valido contenente le chiavi 'name' e 'parameters'. Nessun altro testo. \n Risultato:\n{"

il risultato finale dovrebbe essere qualcosa tipo:

```text
Sei un assistente automatico progettato per estrarre informazioni e chiamare funzioni. Non devi rispondere alle domande dell'utente, ma devi solo selezionare la funzione corretta e i parametri necessari.

Ecco la lista delle funzioni a tua disposizione, con i rispettivi parametri e tipi di dato:

[
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
      "a": {
        "type": "number"
      },
      "b": {
        "type": "number"
      }
    }
  },
  {
    "name": "fn_greet",
    "description": "Generate a greeting message for a person by name.",
    "parameters": {
      "name": {
        "type": "string"
      }
    }
  }
]

Richiesta dell'utente: Ciao, potresti salutare john per me?

Genera SOLO un oggetto JSON valido contenente le chiavi 'name' e 'parameters'. Nessun altro testo.
Risultato:
{
```

# step 3

tradurre il prompt utilizzando la funzione encode del pacchetto llm_sdk, la funzione encode prende la stringa e la converte in una lista di numeri interi chiamati "input IDs" per esempio: [345, 89, 90, 3403, ...] (i numeri sono l'indice del vocabolario dell'AI, spiegato meglio in logits.md)

salvare il dizionario dell'AI in una variabile utilizzando get_path_to_vocab_file() per trovare il path nel pc e poi aprire il file.


# step 4

creare un ciclo while in cui viene generata la risposta, scegliere una fine del ciclo in base a quando l'AI finisce di generare, per esempio quando genera una } di chiusura JSON

all'interno del ciclo e' necessario chiamare la funzione 'get_logits_from_input_ids()', questa funzione prende in input la lista degli IDs e rende in output un array di floats, questo array di float si chiama Logits (guardare logits.md per spiegazione)

## constrained decoding

```text
Poiché siamo al primissimo giro di ciclo, il prompt è appena terminato con il carattere { quindi dopo ci possiamo aspettare '"' oppure '"name"' oppure '"na'

per sapere a quali ID corrispondono queste stringhe scorriamo il dizionario dell'AI (la variabile che abbiamo salvato fuori dal ciclo nello step 3).

Cerchiamo nel dizionario tutte le chiavi di testo che corrispondono a '"', '"name"' e '"na'.
Il dizionario ci dirà, ad esempio, che '"na' corrisponde all'ID 450.


Ora che sappiamo che i nostri ID validi sono (ad esempio) il 450 e il 505, andiamo a modificare l'array dei Logits.

Impostiamo a -inf tutti gli indici dell'array, TRANNE quelli validi che abbiamo appena trovato.

finito di ciclare l'array basta prendere il valore rimasto piu alto, siamo sicuri che vada bene a prescindere dato che quelli sbagliati sono stati messi a -inf.

Una volta preso l'ID lo copiamo e lo aggiungiamo alla fine del nostro "input IDs", quindi per esempio se l'ID 450 era '"na' allora passeremo da [..., 100, 1234, 543, 300] a [..., 100, 1234, 543, 300, 450]

quindi il prompt passerebbe da:

---------------------

Genera SOLO un oggetto JSON valido contenente le chiavi 'name' e 'parameters'. Nessun altro testo.
Risultato:
{

---------------------

Genera SOLO un oggetto JSON valido contenente le chiavi 'name' e 'parameters'. Nessun altro testo.
Risultato:
{
	"na

---------------------


dato che l'AI non ha generato una '}' dobbiamo continuare il ciclo, quindi richiameremo 'get_logits_from_input_ids()' passandogli il nuovo "input IDs"
```

# step 5

adesso abbiamo il prompt iniziale modificato in modo che anche la parte del risultato e' completa, cio che dobbiamo fare adesso e' riconvertire "input IDs" in una stringa usando funzione "decode(token_ids: List[int]) -> str" 

riconvertito in stringa dobbiamo prendere solo la parte finale del risultato, validarla con pydantic e poi aggiungere il risultato in una lista di output in questo modo:

prompt: La stringa originale della domanda dell'utente (quella letta dal file di test).
name: Il nome della funzione che l'AI ha scelto. 
parameters: L'oggetto con i parametri estratti. 


# step 6

se ci sono altri input dell'utente all'interno del file "function_calling_tests.json" allora dobbiamo ricominciare tutto da capo, creare un nuovo prompt da zero, pulire "input IDs" e ricominciare il while ("step 2")

se le domande sono finite allora va presa la lista generale di output e creare "data/output/function_calling_results.json"
