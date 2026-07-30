import src
import llm_sdk


MESSAGE = ("You are an automated assistant designed to extract information "
           "and call functions. You do not need to answer the user's questions,"
           " but only select the correct function and the necessary parameters."
           "\nHere is the list of functions available to you, with their respective "
           "parameters and data types:\n")

REQUEST = "\nUser request: "

END = ("\nGenerate ONLY a valid JSON object containing the keys 'name' and "
       "'parameters'. No other text.\nResult:\n\n{")


def main() -> None:
    try:
        functs = src.parsing_definition()
        prompts = src.parsing_calling()
        model = llm_sdk.Small_LLM_Model()

        for i in prompts:
            prompt = MESSAGE + functs + REQUEST + i.prompt + END
            inputIDs = model.encode(prompt)
            # print(inputIDs)
            ''' while di generazione risposta finche non viene generata una }'''
    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    main()
