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