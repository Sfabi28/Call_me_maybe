NAME = call_me_maybe.py
PYTHON = python3
VENV = /sgoinfre/sfabi/.venv
BIN = $(VENV)/bin
UV_CACHE_DIR = /sgoinfre/sfabi/uv-cache
TMPDIR = /sgoinfre/sfabi/tmp
HF_HOME = /sgoinfre/sfabi/hf
HF_HUB_CACHE = $(HF_HOME)/hub

dirs:
	mkdir -p $(VENV) $(UV_CACHE_DIR) $(TMPDIR) $(HF_HOME) $(HF_HUB_CACHE)

install: dirs
	UV_PROJECT_ENVIRONMENT=$(VENV) UV_CACHE_DIR=$(UV_CACHE_DIR) TMPDIR=$(TMPDIR) uv sync --no-cache

run:
	CUDA_VISIBLE_DEVICES= HF_HOME=$(HF_HOME) HF_HUB_CACHE=$(HF_HUB_CACHE) TMPDIR=$(TMPDIR) $(BIN)/$(PYTHON) $(NAME) # config.txt

debug:
	CUDA_VISIBLE_DEVICES= HF_HOME=$(HF_HOME) HF_HUB_CACHE=$(HF_HUB_CACHE) TMPDIR=$(TMPDIR) $(BIN)/$(PYTHON) -m pdb $(NAME) # config.txt

test:
        $(foreach num, $(NUMBERS), CUDA_VISIBLE_DEVICES= HF_HOME=$(HF_HOME) HF_HUB_CACHE=$(HF_HUB_CACHE) TMPDIR=$(TMPDIR) $(BIN)/$(PYTHON) $(NAME) configs/config$(num).txt;)
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

build:
	HF_HOME=$(HF_HOME) HF_HUB_CACHE=$(HF_HUB_CACHE) TMPDIR=$(TMPDIR) $(BIN)/pip install build
	HF_HOME=$(HF_HOME) HF_HUB_CACHE=$(HF_HUB_CACHE) TMPDIR=$(TMPDIR) $(BIN)/$(PYTHON) -m build --wheel

.PHONY: install run debug clean lint lint-strict build