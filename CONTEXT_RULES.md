# CONTEXT_RULES — Governança de IA do TaskAnalyzer

Este arquivo define as regras obrigatórias que qualquer assistente de IA deve seguir
ao gerar ou modificar código neste projeto. O contrato de negócio está em
`specs/task_analyzer_spec.md`.

## 1. Linguagem e ambiente
- Python 3.11 ou superior.
- Usar apenas a biblioteca padrão do Python no código-fonte (ex.: `datetime`, `typing`).
- Dependências externas são permitidas somente para testes e devem constar em `requirements.txt` (pytest).

## 2. Tipagem
- Type hints obrigatórios em 100% das funções, parâmetros e retornos.

## 3. Tratamento de erros
- Usar a exceção customizada `TaskValidationError` para dados inválidos.
- Proibido usar `except Exception` genérico ou silenciar erros.
- Datas inconsistentes (`data_conclusao` < `data_criacao`) devem lançar `TaskValidationError`.

## 4. Cálculos
- Proibido dividir por zero: médias e percentuais sem dados retornam `0.0`.
- Tempos em horas, arredondados para 2 casas decimais.

## 5. Aderência à especificação
- A IA não pode inventar campos, regras ou chaves de saída que não estejam na especificação.
- Nomes de funções, campos e chaves devem ser idênticos aos da especificação.
- Em caso de ambiguidade, a IA deve perguntar em vez de supor.

## 6. Qualidade de código
- Funções com docstrings.
- Código legível, sem lógica duplicada.

## 7. Homologação humana
- Todo código gerado por IA deve passar pelo Test Harness (`tests/test_harness.py`)
  e por revisão humana antes do merge na branch `main`.