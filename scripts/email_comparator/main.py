# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pandas",
#     "openpyxl",
#     "tabulate",
# ]
# ///

"""Compara duas planilhas e retorna as linhas com emails em comum."""

import sys
import typing
from pathlib import Path

import pandas as pd

EMAIL_COLUMN = "email"


def load_spreadsheet(path: Path) -> pd.DataFrame:
    """Carrega uma planilha (csv, xlsx, xls) e valida a presença da coluna de email."""
    suffix = path.suffix.lower()
    readers: dict[str, typing.Callable] = {
        ".csv": pd.read_csv,
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
    }

    reader = readers.get(suffix)
    if reader is None:
        raise ValueError(f"Formato não suportado: {suffix}. Use .csv, .xlsx ou .xls")

    df = reader(path)
    df.columns = df.columns.str.strip().str.lower()

    if EMAIL_COLUMN not in df.columns:
        available = list(df.columns)
        raise ValueError(f"Coluna '{EMAIL_COLUMN}' não encontrada em '{path.name}'. Colunas disponíveis: {available}")

    df[EMAIL_COLUMN] = df[EMAIL_COLUMN].astype(str).str.strip().str.lower()
    return df


def compare_emails(df_base: pd.DataFrame, df_compare: pd.DataFrame, name_base: str, name_compare: str) -> pd.DataFrame:
    """Left merge ordenado: emails com match primeiro, sem match por último."""
    result = df_base.merge(
        df_compare, on=EMAIL_COLUMN, how="left", suffixes=(f"_{name_base}", f"_{name_compare}"), indicator=True
    )
    result = result.sort_values("_merge", key=lambda col: col != "both").drop(columns=["_merge"])
    return result.reset_index(drop=True)


def find_spreadsheets() -> list[Path]:
    """Busca planilhas via argumentos ou na pasta data/."""
    if len(sys.argv) == 3:
        paths = [Path(sys.argv[1]), Path(sys.argv[2])]
        for p in paths:
            if not p.exists():
                print(f"Erro: arquivo '{p}' não encontrado.")
                sys.exit(1)
        return paths

    if len(sys.argv) > 3:
        print(f"Erro: esperado 2 planilhas, recebido {len(sys.argv) - 1}.")
        print(f"Uso: uv run {sys.argv[0]} <planilha1> <planilha2>")
        sys.exit(1)

    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"

    if not data_dir.exists():
        print("Erro: nenhuma planilha informada e pasta 'data/' não encontrada.")
        print(f"Uso: uv run {sys.argv[0]} <planilha1> <planilha2>")
        print(f"  ou coloque 2 planilhas em: {data_dir}")
        sys.exit(1)

    spreadsheets = sorted(p for p in data_dir.iterdir() if p.suffix.lower() in {".csv", ".xlsx", ".xls"})

    if len(spreadsheets) != 2:
        print(f"Erro: esperado 2 planilhas em 'data/', encontrado {len(spreadsheets)}.")
        for s in spreadsheets:
            print(f"  - {s.name}")
        sys.exit(1)

    return spreadsheets


def choose_base(paths: list[Path]) -> tuple[Path, Path]:
    """Permite ao usuário escolher qual planilha será a base."""
    print("\nPlanilhas encontradas:")
    for i, p in enumerate(paths, 1):
        print(f"  [{i}] {p.name}")

    while True:
        choice = input("\nQual será a planilha BASE? [1/2]: ").strip()
        if choice == "1":
            return paths[0], paths[1]
        if choice == "2":
            return paths[1], paths[0]
        print("Opção inválida. Digite 1 ou 2.")


def main() -> None:
    """Ponto de entrada: busca planilhas e pergunta qual é a base."""
    paths = find_spreadsheets()
    path_base, path_compare = choose_base(paths)

    try:
        df_base = load_spreadsheet(path_base)
        df_compare = load_spreadsheet(path_compare)
    except ValueError as exc:
        print(f"Erro: {exc}")
        sys.exit(1)

    result = compare_emails(df_base, df_compare, path_base.stem, path_compare.stem)

    common = result[EMAIL_COLUMN].isin(set(df_base[EMAIL_COLUMN]) & set(df_compare[EMAIL_COLUMN]))
    print(f"\n  {path_base.name} (base): {len(df_base)} email(s)")
    print(f"  {path_compare.name}: {len(df_compare)} email(s)")
    print(f"  Em comum: {common.sum()} email(s)\n")

    if result.empty:
        print("Nenhum email em comum encontrado.")
        sys.exit(0)

    # print(result.to_markdown(index=False, tablefmt="rounded_grid"))

    output = path_base.parent / "emails_em_comum.csv"
    result.to_csv(output, index=False)
    print(f"\nResultado salvo em: {output}")


if __name__ == "__main__":
    main()
