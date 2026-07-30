import torch
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
            flag: int = 0
            while True:    #USARE CONSTRAINED DECODING
                logits = model.get_logits_from_input_ids(inputIDs[0].tolist())
                next_token_id = int(torch.argmax(torch.tensor(logits, device=inputIDs.device)))
                inputIDs = torch.cat([inputIDs, torch.tensor([[next_token_id]], device=inputIDs.device,
                                     dtype=inputIDs.dtype)], dim=1)
                output = model.decode([next_token_id])
                if '}' in output:
                    if flag == 0:
                        flag = 1
                    else:
                        break

            print(model.decode(inputIDs[0].tolist()))

    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    main()