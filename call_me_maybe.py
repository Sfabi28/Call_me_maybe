import src


MESSAGE = ("Sei un assistente automatico progettato per estrarre informazioni "
           "e chiamare funzioni. Non devi rispondere alle domande dell'utente,"
           " ma devi solo selezionare la funzione corretta e i parametri "
           "necessari.\nEcco la lista delle funzioni a tua disposizione, "
           "con i rispettivi parametri e tipi di dato:\n")

REQUEST = "\nRichiesta dell'utente: "

END = ("\nGenera SOLO un oggetto JSON valido contenente le chiavi 'name' e "
       "'parameters'. Nessun altro testo.\nRisultato:\n\n{")


def main() -> None:
    try:
        functs = src.parsing_definition()
        prompts = src.parsing_calling()
        for i in prompts:
            prompt = MESSAGE + functs + REQUEST + i.prompt + END
            ''' for di generazione risposta'''
    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    main()
