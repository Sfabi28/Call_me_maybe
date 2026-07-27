import src


def main() -> None:
    try:
        src.parsing_definition()
        src.parsing_calling()
    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    main()
