import torch
import src
import llm_sdk
import json
import numpy as np


MESSAGE = (
    "You are an automated function-calling assistant. Your only task is to "
    "read a user request and produce a JSON object describing which function "
    "to call and with which parameters. You do not answer the user's question "
    "and you do not explain your reasoning.\n"
    "\n"
    "Rules:\n"
    "1. Choose exactly one function from the list below that best matches the "
    "user's request.\n"
    "2. Use the EXACT parameter names defined for that function — do not "
    "rename, translate, or omit them.\n"
    "3. Extract every parameter value EXACTLY as it appears in the user "
    "request. Never invent, guess, or substitute a placeholder such as "
    "'user' or 'name' — always copy the specific word, phrase, or number "
    "the user actually provided.\n"
    "4. If a value in the user request is wrapped in single quotes, copy "
    "only the text inside the quotes, without the quotes themselves.\n"
    "5. Values for parameters of type 'number' must always be written as "
    "floats (e.g. 10 -> 10.0). Values for parameters of type 'integer' must "
    "be written as plain integers (e.g. 10, not 10.0).\n"
    "6. Output nothing except the JSON object — no explanations, no extra "
    "text before or after it.\n"
    "\n"
    "Here is the list of functions available to you, with their parameters "
    "and expected data types:\n"
)

EXAMPLES = (
    '\nExample 1:\nUser request: Greet Mary\nResult:\n{\n"prompt": "Greet Mary'
    '",\n"name": "fn_greet",\n"parameters": {"name": "Mary"}\n}\n\n'
    'Example 2:\nUser request: What is the sum of 10 and 20?\nResult:\n{\n"prompt": '
    '"What is the sum of 10 and 20?",\n"name": "fn_add_numbers",\n'
    '"parameters": {"a": 10.0, "b": 20.0}\n}\n\n'
    "Example 3:\nUser request: Look up the record with id 'ABC-123'\nResult:\n"
    '{\n"prompt": "Look up the record with id \'ABC-123\'",\n'
    '"name": "fn_lookup_record",\n"parameters": {"id": "ABC-123"}\n}\n'
)

REQUEST = "\nNow do the same for this new request.\nUser request: "

END = (
    "\nRemember: output ONLY a single valid JSON object with exactly the "
    'keys "name" and "parameters", matching the format shown in the '
    "examples above. No explanations, no markdown, no extra text.\nResult:\n\n"
)


def main() -> None:
    try:
        functs = src.parsing_definition()
        functs_data = json.loads(functs)
        prompts = src.parsing_calling()
        model = llm_sdk.Small_LLM_Model()
        state = src.jsonState
        vocab_path = model.get_path_to_vocab_file()
        with open(vocab_path, 'r', encoding='utf-8') as file:
            vocab = json.load(file)
        vocab_size = len(model.get_logits_from_input_ids(model.encode("x").tolist()[0]))
        id_to_token = {tid: model.decode(tid) for tid in range(vocab_size)}

        for i in prompts:
            curr_prompt: str = f'"{i.prompt}",\n'
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
                best_tokenId = src.constrained_decoding(func_name, id_to_token, functs_data, current_state,
                                                        param_name, inputIDs, model, state_output, i.prompt, used_params)
                token_str = model.decode(best_tokenId)
                output += token_str
                state_output += token_str

                if current_state == state.AWAITING_NAME:
                    func_name = func_name + token_str
                    func_name = func_name.replace(',', '').replace('"', '').replace('\n', '').strip()

                if current_state == state.AWAITING_PARAMETERS_NAME:
                    param_name = param_name + token_str
                    param_name = param_name.replace(',', '').replace('"', '').replace('\n', '').replace(':', '').strip()

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
