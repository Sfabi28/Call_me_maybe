from pydantic import BaseModel, ValidationError, TypeAdapter, ConfigDict
from enum import Enum


class jsonState(Enum):
    '''
        macchina a stati per sapere sempre dove siamo nel codice
    '''
    AWAITING_BRACKET = 0 # '{\n'
    AWAITING_NAME_KEY = 1 # '"name": '
    AWAITING_NAME = 2 # '"fn_add_numbers",\n'
    AWAITING_PARAMETERS_KEY = 3 # '"parameters": '
    AWAITING_PARAMETERS_BRACKET = 4 # '{ '
    AWAITING_PARAMETERS_NAME = 5 #'"a": '
    AWAITING_PARAMETERS_VALUE = 6 # ', ' OR '}\n'
    AWAITING_CLOSING_BRACKET = 7 # '}'
    

def update_state(current_state: jsonState, current_text: str) -> jsonState:

    '''
        funzione per passare da uno stato all'altro della macchina a stati
    '''


    match current_state:
        case jsonState.AWAITING_BRACKET:
            if current_text == "{\n":
                return jsonState.AWAITING_NAME_KEY
                
        case jsonState.AWAITING_NAME_KEY:
            if current_text.endswith('"name": '):
                return jsonState.AWAITING_NAME
                
        case jsonState.AWAITING_NAME:
            if current_text.endswith('",\n'):
                return jsonState.AWAITING_PARAMETERS_KEY
                
        case jsonState.AWAITING_PARAMETERS_KEY:
            if current_text.endswith('"parameters": '):
                return jsonState.AWAITING_PARAMETERS_BRACKET
                
        case jsonState.AWAITING_PARAMETERS_BRACKET:
            if current_text.endswith('{ '):
                return jsonState.AWAITING_PARAMETERS_NAME
            
        case jsonState.AWAITING_PARAMETERS_NAME:
            if current_text.endswith('": '):
                return jsonState.AWAITING_PARAMETERS_VALUE

        case jsonState.AWAITING_PARAMETERS_VALUE:
             if current_text.endswith(', '):
                 return jsonState.AWAITING_PARAMETERS_NAME
             elif current_text.endswith('}\n'):
                 return jsonState.AWAITING_CLOSING_BRACKET
                 
        case jsonState.AWAITING_CLOSING_BRACKET:
             if current_text.endswith('}'):
                 return current_state
                
    return current_state


def get_valid_targets(current_state: jsonState, available_functions: list, chosen_function_name: str = None, current_param_name: str = None) -> list[str]:
    '''
        funzione che restituisce una lista di quello che l'AI puo' generare, servira' per gestire i logits con constrained decoding
    '''
    match current_state:
        case jsonState.AWAITING_BRACKET:
            return ["{\n"]
                
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
            return ['{ ']
            
        case jsonState.AWAITING_PARAMETERS_NAME:    ##############################
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
                targets.append(f'"{param_name}": ')
            return targets

        case jsonState.AWAITING_PARAMETERS_VALUE:  ###############################
            targets = []
            targets.append(', ')
            targets.append('}\n')
            
            if not chosen_function_name or not current_param_name:
                return targets
                
            chosen_func_data = None
            for func in available_functions:
                if func["name"] == chosen_function_name:
                    chosen_func_data = func
                    break
            
            if chosen_func_data and "parameters" in chosen_func_data:
                param_info = chosen_func_data["parameters"].get(current_param_name)
                if param_info:
                    param_type = param_info.get("type")
                    if param_type == "number":
                        targets.append("<NUMBER_PATTERN>") 
                    elif param_type == "string":
                        targets.append("<STRING_PATTERN>")
                        
            return targets
                 
        case jsonState.AWAITING_CLOSING_BRACKET:
            return ["}"]

    return []