from enum import Enum
import math
import string


class jsonState(Enum):
    '''
        macchina a stati per sapere sempre dove siamo nel codice
    '''
    AWAITING_NAME_KEY = 1 # '"name": '
    AWAITING_NAME = 2 # '"fn_add_numbers",\n'
    AWAITING_PARAMETERS_KEY = 3 # '"parameters": '
    AWAITING_PARAMETERS_BRACKET = 4 # '{ '
    AWAITING_PARAMETERS_NAME = 5 #'"a": '
    AWAITING_PARAMETERS_VALUE = 6 # ', ' OR '}\n'
    AWAITING_CLOSING_BRACKET = 7 # '}'


def _count_unescaped_quotes(text: str) -> int:
    count = 0
    escaped = False
    for ch in text:
        if escaped:
            escaped = False
            continue
        if ch == '\\':
            escaped = True
            continue
        if ch == '"':
            count += 1
    return count


def _normalize_for_match(text: str) -> str:
    return (
        text
        .replace('\\"', '"')
        .replace("\\'", "'")
        .replace('\\\\', '\\')
    )


def constrained_decoding(chosen_function, id_to_token, functions, curnt_state,
                         current_par_name, inputIDs, model, output, prompt,
                         used_params=None):
    '''
    funzione che restituisce il logit corretto in base al constrained decoding
    '''
    logits = model.get_logits_from_input_ids(inputIDs)
    valid_targets = get_valid_targets(curnt_state, functions, chosen_function,
                                      current_par_name, used_params)
    has_value_text = bool(output.strip())
    # valid_prompt = [w.strip(string.punctuation) for w in prompt.split()]

    for token_id in range(len(logits)):
        token_text = id_to_token[token_id]
        simulated_text = output + token_text
        is_valid = False

        for target in valid_targets:
            is_closing_target = (target in [', ', '}\n']
                                 or target.startswith('}'))
            if curnt_state == (jsonState.AWAITING_PARAMETERS_VALUE
                               and not has_value_text and is_closing_target):
                continue

            if target == "<NUMBER_PATTERN>":
                if ',' not in output and '}' not in output:
                    if token_text.strip().isdigit() or (token_text.strip()
                                                        in ['-', '.']):
                        is_valid = True
                        break

            elif target == "<STRING_PATTERN>":
                quote_count = _count_unescaped_quotes(output)

                if '\n' in token_text:
                    continue

                tentative = output + token_text
                tentative_quote_count = _count_unescaped_quotes(tentative)

                if tentative_quote_count > 2:
                    continue

                if quote_count == 0:
                    if not token_text.startswith('"'):
                        continue

                normalized_prompt = _normalize_for_match(prompt)
                normalized_tentative = _normalize_for_match(tentative)

                first_quote = normalized_tentative.find('"')
                if first_quote == -1:
                    continue

                if tentative_quote_count == 1:
                    candidate = normalized_tentative[first_quote + 1:]
                    if candidate == "" or candidate in normalized_prompt:
                        is_valid = True
                        break

                elif tentative_quote_count == 2:
                    last_quote = normalized_tentative.rfind('"')
                    if last_quote > first_quote:
                        candidate = normalized_tentative[
                            first_quote + 1:last_quote]
                        if candidate in normalized_prompt:
                            is_valid = True
                            break

            else:
                if curnt_state == jsonState.AWAITING_PARAMETERS_VALUE:
                    quote_count = _count_unescaped_quotes(output)
                    if quote_count % 2 == 1:
                        continue
                    if target.startswith(token_text):
                        is_valid = True
                        break
                    elif any(simulated_text.endswith(target[:i])
                             for i in range(1, len(target) + 1)):
                        is_valid = True
                        break
                else:
                    if target.startswith(simulated_text):
                        is_valid = True
                        break

        if not is_valid:
            logits[token_id] = -math.inf

    winning_token_id = logits.index(max(logits))

    return winning_token_id


def update_state(curnt_state: jsonState, current_text: str) -> jsonState:

    '''
        funzione per passare da uno stato all'altro della macchina a stati
    '''
    normalized_text = current_text

    match curnt_state:
        case jsonState.AWAITING_NAME_KEY:
            if '"name": ' in normalized_text:
                return jsonState.AWAITING_NAME

        case jsonState.AWAITING_NAME:
            if '",\n' in normalized_text:
                return jsonState.AWAITING_PARAMETERS_KEY

        case jsonState.AWAITING_PARAMETERS_KEY:
            if '"parameters": ' in normalized_text:
                return jsonState.AWAITING_PARAMETERS_BRACKET

        case jsonState.AWAITING_PARAMETERS_BRACKET:
            if '{' in normalized_text:
                return jsonState.AWAITING_PARAMETERS_NAME

        case jsonState.AWAITING_PARAMETERS_NAME:
            if '": ' in normalized_text:
                return jsonState.AWAITING_PARAMETERS_VALUE

        case jsonState.AWAITING_PARAMETERS_VALUE:
            quote_count = _count_unescaped_quotes(normalized_text)
            if quote_count % 2 == 1:
                return curnt_state

            if ', ' in normalized_text:
                return jsonState.AWAITING_PARAMETERS_NAME
            elif '}' in normalized_text:
                return jsonState.AWAITING_CLOSING_BRACKET

        case jsonState.AWAITING_CLOSING_BRACKET:
            if '}' in normalized_text:
                return curnt_state

    return curnt_state


def get_valid_targets(curnt_state: jsonState, available_functions: list[dict],
                      chosen_function_name: str = None,
                      current_param_name: str = None,
                      used_params: str = None) -> list[str]:
    '''
        funzione che restituisce una lista di quello che l'AI puo' generare,
        servira' per gestire i logits con constrained decoding
    '''
    match curnt_state:

        case jsonState.AWAITING_NAME_KEY:
            return ['"name": ']

        case jsonState.AWAITING_NAME:
            targets = []
            for func in available_functions:
                targets.append(f'"{func["name"]}",\n')
            return targets

        case jsonState.AWAITING_PARAMETERS_KEY:
            return ['"parameters": ']

        case jsonState.AWAITING_PARAMETERS_BRACKET:
            return ['{']

        case jsonState.AWAITING_PARAMETERS_NAME:
            if not chosen_function_name:
                return []

            chosen_func_data = None
            for func in available_functions:
                if func["name"] == chosen_function_name:
                    chosen_func_data = func
                    break

            if not chosen_func_data or "parameters" not in chosen_func_data:
                return []

            targets = []
            for param_name in chosen_func_data["parameters"].keys():
                if used_params and param_name in used_params:
                    continue
                targets.append(f'"{param_name}": ')
            return targets

        case jsonState.AWAITING_PARAMETERS_VALUE:
            targets = []

            if not chosen_function_name or not current_param_name:
                return targets

            chosen_func_data = None
            for func in available_functions:
                if func["name"] == chosen_function_name:
                    chosen_func_data = func
                    break

            if chosen_func_data and "parameters" in chosen_func_data:
                param_names = list(chosen_func_data["parameters"].keys())
                already_used = set(used_params or [])
                remaining = [p for p in param_names
                             if p != current_param_name
                             and p not in already_used]
                is_last_param = len(remaining) == 0

                targets.append(', ')
                if is_last_param:
                    targets.append('}\n}')

                param_info = chosen_func_data["parameters"].get(
                    current_param_name)
                if param_info:
                    param_type = param_info.get("type")
                    if param_type in ("number", "integer", "boolean"):
                        targets.append("<NUMBER_PATTERN>")
                    elif param_type == "string":
                        targets.append("<STRING_PATTERN>")

            return targets

        case jsonState.AWAITING_CLOSING_BRACKET:
            return ["}"]

    return []
