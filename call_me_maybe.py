import src
import llm_sdk
import json


MESSAGE = (
    "You are an automated assistant designed to extract information "
    "and call functions. You do not need to answer the user's questions,"
    " but only select the correct function and the necessary parameters."
    " You have to keep the same parameters names."
    " IMPORTANT: parameter values must be extracted EXACTLY as they appear"
    " in the user request below. Never use placeholder values like 'user'"
    " or 'name' — always copy the specific word or number the user provided."
    "\nHere is the list of functions available to you, with their respec"
    " tive parameters and data types, REMEMBER that number is a float so it"
    " needs a .:\n")

EXAMPLES = (
    '\nExample 1:\nUser request: Greet Mary\nResult:\n{\n"prompt": "Greet Mary'
    '",\n"name": "fn_greet",\n"parameters": {"name": "Mary"}\n}\n\nExample 2:'
    '\nUser request: What is the sum of 10 and 20?\nResult:\n{\n"prompt": '
    '"What is the sum of 10 and 20?",\n"name": "fn_add_numbers",\n'
    '"parameters": {"a": 10.0, "b": 20.0}\n}\n')

REQUEST = "\nUser request: "

END = ('\nGenerate ONLY a valid JSON object containing the keys "name" and '
       '"parameters". No other text.\nResult:\n\n')


def main() -> None:
    try:
        functs = src.parsing_definition()
        functs_data = json.loads(functs)
        prompts = src.parsing_calling()
        model = llm_sdk.Small_LLM_Model()
        state = src.jsonState
        vocab_path = model.get_path_to_vocab_file()
        with open(vocab_path, 'r', encoding='utf-8') as file:
            json.load(file)
        vocab_size = len(model.get_logits_from_input_ids(model.encode(
                         "x").tolist()[0]))
        id_to_token = {tid: model.decode(tid) for tid in range(vocab_size)}

        for i in prompts:
            curr_prompt: str = f'{json.dumps(i.prompt)},\n'
            output: str = '{\n"prompt": ' + curr_prompt
            state_output: str = ''
            prompt: str = (MESSAGE + functs + EXAMPLES + REQUEST + i.prompt +
                           END + output)
            inputIDs = model.encode(prompt).tolist()[0]

            current_state: src.jsonState = state.AWAITING_NAME_KEY
            func_name = ""
            param_name = ""
            used_params: list[str] = []

            while True:
                best_tokenId = src.constrained_decoding(
                    func_name, id_to_token, functs_data, current_state,
                    param_name, inputIDs, model, state_output, i.prompt,
                    used_params)
                token_str = model.decode(best_tokenId)
                output += token_str
                state_output += token_str

                if current_state == state.AWAITING_NAME:
                    func_name = func_name + token_str
                    func_name = func_name.replace(',', '').replace(
                        '"', '').replace('\n', '').strip()

                if current_state == state.AWAITING_PARAMETERS_NAME:
                    param_name = param_name + token_str
                    param_name = param_name.replace(',', '').replace(
                        '"', '').replace('\n', '').replace(':', '').strip()

                if current_state == state.AWAITING_CLOSING_BRACKET:
                    break

                inputIDs = inputIDs + [best_tokenId]
                new_state = src.update_state(current_state, state_output)
                if new_state != current_state:
                    if current_state == state.AWAITING_PARAMETERS_NAME:
                        used_params.append(param_name)
                    state_output = ''
                    if new_state == state.AWAITING_PARAMETERS_NAME:
                        param_name = ''
                current_state = new_state
                # print(output)
            print(output)

    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    main()
