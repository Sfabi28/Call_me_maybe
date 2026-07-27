from typing import Any, Dict
import json


def dict_construct(id, x, y, z):
    new_dic = {id: {'properties': {}}}
    values = [{'x': x}, {'y': y}, {'z': z}]
    for val in values:
        new_dic[id]['properties'].update(val)
    return new_dic


def functions_definition_dict(fun_def: Dict, name: str, desc: str,
                              param: Dict[str: Any]) -> Dict:
    fun_def['name'] = name
    fun_def['description'] = desc
    fun_def['parameters'] = param

    return fun_def


def function_calling_tests_dict(fun_call: Dict, prompt: str) -> Dict:
    fun_call['prompt'] = prompt

    return fun_call


def main() -> None:

    data = {
        "name": "John",
        "age": 30,
        "city": "New York"
    }

    json_string = json.dumps(data, indent=4, ensure_ascii=False)

    with open('output.json', 'w', encoding='utf-8') as file:
        file.write(json_string)

    json_array = {}
    json_array['i'] = {}
    json_array['i']

    # with open('function_calling_tests.json', 'w') as f:
    #     f.write()

    return_values = [('a', '9', '3', '17'), ('b', '3', '2', '1')]
    a_dict = {'name': {}}
    for xx in return_values:
        add_dict = dict_construct(*xx)
        a_dict['id'].update(add_dict)

    with open('functions_definition.json', 'w') as outfile:
        json.dump(a_dict, outfile)

    print(a_dict)


if __name__ == "__main__":
    main()
