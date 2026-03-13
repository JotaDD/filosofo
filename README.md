# filosofo

Repositório de scripts Python independentes.

## Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

## Rodar um script

Cada script declara suas próprias dependências via [inline script metadata (PEP 723)](https://peps.python.org/pep-0723/). Para rodar:

```bash
uv run scripts/email_comparator/main.py
uv run scripts/irmas_checker/main.py
```

O `uv` resolve e instala as dependências de cada script automaticamente.

## Scripts disponíveis

| Script | Descrição | Dependências |
|---|---|---|
| `scripts/email_comparator/` | Compara emails entre duas planilhas | `pandas`, `openpyxl` |
| `scripts/irmas_checker/` | Valida se faculdades do Teste possuem relação (irmãs) com as do Qbank Personalizado | `pandas`, `openpyxl` |

## Criar um novo script

1. Crie uma pasta dentro de `scripts/`:

```bash
mkdir scripts/meu_script
```

2. Crie o arquivo `main.py` com inline metadata no topo:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
# ]
# ///

def main():
    pass

if __name__ == "__main__":
    main()
```

3. Rode com `uv run scripts/meu_script/main.py`.

## Linting

```bash
uv run ruff check scripts/
uv run ruff format scripts/
```
