# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pandas",
#     "openpyxl",
# ]
# ///

"""Valida se as faculdades do Teste possuem relação (irmãs) com as do Qbank Personalizado."""

import re
import unicodedata
from pathlib import Path

import pandas as pd

SPREADSHEET_PATH = Path(__file__).parent / "data" / "irmas.xlsx"

BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def normalize(text: str) -> str:
    """Remove acentos, espaços extras, hífens e converte para uppercase."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[\s\-_]+", "", text).upper()
    return text


def parse_input(raw: str) -> list[str]:
    """Separa o input por vírgula e retorna lista de nomes trimados."""
    return [item.strip() for item in raw.split(",") if item.strip()]


def load_institution_map(df: pd.DataFrame) -> dict[str, dict]:
    """
    Constrói um mapa normalizado: nome_normalizado -> {nome_original, irmas_nomes}.
    As irmãs são armazenadas tanto com o nome original quanto normalizado.
    """
    institution_map: dict[str, dict] = {}

    for _, row in df.iterrows():
        nome_original = str(row["nome"]).strip()
        nome_norm = normalize(nome_original)

        irmas_nomes_raw = row.get("instituicoes_irmas_nomes", "")
        irmas: list[str] = []
        if pd.notna(irmas_nomes_raw) and "Não contém cadastro" not in str(irmas_nomes_raw):
            irmas = [s.strip() for s in str(irmas_nomes_raw).split(",") if s.strip()]

        institution_map[nome_norm] = {
            "nome_original": nome_original,
            "irmas_originais": irmas,
            "irmas_normalizadas": {normalize(i) for i in irmas},
        }

    return institution_map


def find_best_match(name: str, institution_map: dict[str, dict]) -> str | None:
    """Tenta encontrar a melhor correspondência para um nome no mapa, usando match exato normalizado."""
    norm = normalize(name)
    if norm in institution_map:
        return norm

    for key in institution_map:
        if norm in key or key in norm:
            return key

    return None


def main() -> None:
    """Executa a validação das instituições irmãs entre Qbank e Teste."""
    df = pd.read_excel(SPREADSHEET_PATH)
    institution_map = load_institution_map(df)

    print(f"\n{BOLD}=== Checker de Instituições Irmãs ==={RESET}\n")

    qbank_raw = input(f"{CYAN}Qbank Personalizado (separado por vírgula):{RESET} ")
    test_raw = input(f"{CYAN}Faculdades do Teste (separado por vírgula):{RESET} ")

    qbank_items = parse_input(qbank_raw)
    test_items = parse_input(test_raw)

    test_normalized: dict[str, str] = {}
    for t in test_items:
        match = find_best_match(t, institution_map)
        if match:
            test_normalized[match] = institution_map[match]["nome_original"]
        else:
            test_normalized[normalize(t)] = t

    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}Resultado da Análise{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}\n")

    matched_test_keys: set[str] = set()

    for qbank_name in qbank_items:
        matched_key = find_best_match(qbank_name, institution_map)

        if not matched_key:
            print(f"{YELLOW}⚠  '{qbank_name}' não encontrada na planilha.{RESET}\n")
            continue

        entry = institution_map[matched_key]
        nome_oficial = entry["nome_original"]
        irmas_norm = entry["irmas_normalizadas"]
        irmas_orig = entry["irmas_originais"]

        print(f"{BOLD}📋 {nome_oficial}{RESET}")
        if irmas_orig:
            print(f"   Irmãs: {', '.join(irmas_orig)}")
        else:
            print(f"   {YELLOW}Sem irmãs cadastradas{RESET}")

        found_direct = matched_key in test_normalized
        found_irmas = irmas_norm & set(test_normalized.keys())

        if found_direct:
            matched_test_keys.add(matched_key)
            print(f"   {GREEN}✔ Encontrada diretamente no Teste: {test_normalized[matched_key]}{RESET}")

        if found_irmas:
            matched_test_keys.update(found_irmas)
            for irma_key in found_irmas:
                irma_display = test_normalized.get(irma_key, irma_key)
                print(f"   {GREEN}✔ Irmã encontrada no Teste: {irma_display}{RESET}")

        if not found_direct and not found_irmas:
            print(f"   {RED}✘ Nenhuma correspondência encontrada no Teste{RESET}")

        print()

    unmatched_keys = set(test_normalized.keys()) - matched_test_keys
    if unmatched_keys:
        print(f"{BOLD}{'=' * 60}{RESET}")
        print(f"{BOLD}Faculdades do Teste sem relação com o Qbank{RESET}")
        print(f"{BOLD}{'=' * 60}{RESET}\n")
        for key in unmatched_keys:
            print(f"   {RED}✘ {test_normalized[key]}{RESET}")
        print()


if __name__ == "__main__":
    main()
