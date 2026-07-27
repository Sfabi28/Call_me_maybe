NAME = src/call_me_maybe.py
PYTHON = python3
VENV = .venv
BIN = $(VENV)/bin

install:
	uv sync

run:
	$(BIN)/$(PYTHON) $(NAME) # config.txt

debug:
	$(BIN)/$(PYTHON) -m pdb $(NAME) # config.txt

clean:
	rm -rf $(VENV)
	rm -rf __pycache__

lint:
	$(BIN)/flake8 $(NAME) mazegen
	$(BIN)/mypy $(NAME) mazegen --warn-return-any --warn-unused-ignores \
								   --ignore-missing-imports --disallow-untyped-defs \
								   --check-untyped-defs

lint-strict:
	flake8 $(NAME) mazegen
	mypy $(NAME) mazegen --strict

NUMBERS=0 1 2 3 4 5 6 7 8 9
test:
		$(foreach num, $(NUMBERS), $(BIN)/$(PYTHON) $(NAME) configs/config$(num).txt;)


build:
	$(BIN)/pip install build
	$(BIN)/$(PYTHON) -m build --wheel

.PHONY: install run debug clean lint lint-strict build