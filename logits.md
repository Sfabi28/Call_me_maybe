# logits

i logits sono float che rappresentano punti, i punti sono quanto la rete neurale spinge su quella risposta, piu alti sono piu l'AI e' convinta sia giusto

la dimensione dell'array e' tanto lunga quanto il numero di token che il linguaggio conosce (se l'AI ha un vocabolario di 150000 token allora l'array sara' lungo 150000)

esempio:
	Il prompt chiede quale e' la capitale d'Italia

	passiamo il prompt (convertito in input IDs) all'AI

	riceviamo in risposta il logits (array di float)

	se andiamo all'ID dell'array che rappresenta la parola "Roma" allora avremo un valore alto (come per esempio 19.5) mentre se guardassimo la parola "Elefante" avremmo un valore molto basso (com ead esempio -10.2)