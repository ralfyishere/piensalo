# fable-think — offline-first developer tasks.

.PHONY: test lint benchmark build

test:
	@if command -v uv >/dev/null 2>&1; then \
		uv run pytest -q; \
	else \
		python3 -m pytest -q; \
	fi

lint:
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check src tests; \
	else \
		echo "ruff not found — falling back to py_compile"; \
		python3 -c "import pathlib, py_compile, sys; \
files = sorted(str(p) for p in pathlib.Path('src').rglob('*.py')) + sorted(str(p) for p in pathlib.Path('tests').rglob('*.py')); \
[py_compile.compile(f, doraise=True) for f in files]; \
print(f'py_compile ok: {len(files)} files')"; \
	fi

benchmark:
	@if [ -f evals/Makefile ]; then \
		$(MAKE) -C evals benchmark; \
	else \
		echo "TODO: no evals harness present (expected evals/run.sh)"; \
	fi

build:
	@if command -v uv >/dev/null 2>&1; then \
		uv build; \
	else \
		python3 -m build; \
	fi
