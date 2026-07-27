from pydantic import BaseModel, ValidationError, TypeAdapter, ConfigDict
import sys


class ParseDef(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    description: str
    parameters: dict[str, dict[str, str | int]]
    returns: dict[str, str | int]


class ParseCall(BaseModel):
    model_config = ConfigDict(extra='forbid')
    prompt: str


def parsing_definition() -> str | None:
    adapter = TypeAdapter(list[ParseDef])
    try:
        with open("data/input/functions_definition.json",
                  encoding="utf-8") as file:
            f = file.read()
            res_def = adapter.validate_json(f)
        print("json valido")
        return f
    except FileNotFoundError:
        print("Errore: file non trovato")
        sys.exit(1)
    except ValidationError as e:
        print("Errore: il file JSON non rispetta il formato atteso")
        print(e.errors(include_url=False, include_input=False))
        sys.exit(1)


def parsing_calling() -> list | None:
    adapter = TypeAdapter(list[ParseCall])

    try:
        with open("data/input/function_calling_tests.json",
                  encoding="utf-8") as file:
            res_call = adapter.validate_json(file.read())
        print("json valido")
        return res_call
    except FileNotFoundError:
        print("Errore: file non trovato")
        sys.exit(1)
    except ValidationError as e:
        print("Errore: il file JSON non rispetta il formato atteso")
        print(e.errors(include_url=False, include_input=False))
        sys.exit(1)
