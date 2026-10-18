# sdd-taskanalyzer

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Testes](https://img.shields.io/badge/pytest-16%20passed-brightgreen)
![Fase](https://img.shields.io/badge/fase-2%20de%203-orange)

Módulo Python de análise de tarefas e produtividade desenvolvido com **Spec-Driven Development (SDD)**: o código-fonte foi gerado por assistente de IA a partir de um contrato executável e homologado por revisão humana e testes automatizados.

Projeto da disciplina **Bootcamp III — CEUB**.

## Sobre o projeto

O **TaskAnalyzer** recebe uma lista de tarefas e calcula indicadores objetivos de desempenho:

- **Totais gerais:** tarefas processadas, concluídas, pendentes e atrasadas.
- **Tempo médio de conclusão** (em horas), considerando apenas tarefas concluídas.
- **Taxa de atraso** (percentual de tarefas concluídas após o prazo).
- **Indicadores por prioridade** (`baixa`, `media`, `alta`), calculados de forma isolada.

O contrato completo (entradas, saídas, validações e regras de negócio) está em [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md), que é a **fonte da verdade** do projeto.

## Status do build

| Item | Status |
|---|---|
| Testes automatizados | ✅ 16/16 aprovados (`python -m pytest -v`) |
| Ambiente validado | Windows · PowerShell · Python 3.15.0 |
| Homologação humana | ✅ Concluída (ver Pull Request da implementação) |
| Integração contínua | ⏳ Prevista para a Fase 3 (GitHub Actions) |

## Estrutura do repositório

```
sdd-taskanalyzer/
├── README.md                 # Este arquivo
├── CONTEXT_RULES.md          # Regras de governança para agentes de IA
├── .gitignore                # Arquivos e pastas ignorados pelo Git
├── requirements.txt          # Dependências (pytest)
├── specs/
│   └── task_analyzer_spec.md # Especificação SDD v1.1 (contrato)
├── tests/
│   ├── conftest.py           # Fixtures compartilhadas
│   └── test_harness.py       # Test Harness (cenários de aceite)
└── src/
    └── task_analyzer.py      # Código gerado por IA e homologado por humano
```

## Requisitos

- Python **3.12 ou superior**
- `pytest >= 8.0` (apenas para os testes)

O módulo `src/task_analyzer.py` usa **somente a biblioteca padrão** do Python.

## Como executar

### Windows (PowerShell)

```powershell
git clone https://github.com/TaisDF/sdd-taskanalyzer.git
cd sdd-taskanalyzer
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -v
```

> Se a ativação do ambiente for bloqueada, execute uma vez:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Linux / macOS

```bash
git clone https://github.com/TaisDF/sdd-taskanalyzer.git
cd sdd-taskanalyzer
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
```

Resultado esperado: `16 passed`.

## Exemplo de uso

```python
from datetime import datetime, timezone
from src.task_analyzer import analyze_tasks

tarefas = [
    {
        "id_tarefa": 1,
        "titulo": "Preparar relatório",
        "prioridade": "alta",
        "status": "concluida",
        "data_criacao": datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),
        "prazo": datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc),
        "data_conclusao": datetime(2026, 10, 2, 15, 0, tzinfo=timezone.utc),
    },
    {
        "id_tarefa": 2,
        "titulo": "Revisar código",
        "prioridade": "media",
        "status": "pendente",
        "data_criacao": datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),
        "prazo": datetime(2026, 10, 5, 18, 0, tzinfo=timezone.utc),
        "data_conclusao": None,
    },
]

resultado = analyze_tasks(tarefas)
```

Saída:

```python
{
    "total_tarefas": 2,
    "total_concluidas": 1,
    "total_pendentes": 1,
    "total_atrasadas": 1,
    "tempo_medio_conclusao_horas": 30.0,
    "taxa_atraso_percentual": 100.0,
    "indicadores_por_prioridade": {
        "baixa": {"quantidade_tarefas": 0, "quantidade_concluidas": 0,
                  "tempo_medio_conclusao_horas": 0.0, "taxa_atraso_percentual": 0.0},
        "media": {"quantidade_tarefas": 1, "quantidade_concluidas": 0,
                  "tempo_medio_conclusao_horas": 0.0, "taxa_atraso_percentual": 0.0},
        "alta":  {"quantidade_tarefas": 1, "quantidade_concluidas": 1,
                  "tempo_medio_conclusao_horas": 30.0, "taxa_atraso_percentual": 100.0},
    },
}
```

Entradas inválidas (por exemplo, `data_conclusao` anterior a `data_criacao`) disparam `TaskValidationError`, com mensagem indicando o campo e o `id_tarefa`.

## Cenários de aceite cobertos

| Cenário | Descrição | Testes |
|---|---|---|
| 1 — Sucesso | Totais, tempo médio e taxa de atraso (geral e por prioridade) | 5 |
| 2 — Erro | Datas inconsistentes, enums inválidos, campos ausentes | 8 |
| 3 — Borda | Lista vazia e somente pendentes retornam `0.0` sem exceção | 2 |
| 4 — Prioridade | Indicadores calculados de forma isolada por prioridade | 1 |

## Metodologia: SDD com IA

1. **Especificação** do contrato (Fase 1), versionada em `specs/`.
2. **Regras de contexto** (`CONTEXT_RULES.md`) fornecidas à IA em toda interação.
3. **Testes escritos antes do código**, sem serem enviados à IA.
4. **Geração em dois prompts:** validação da compreensão do contrato e, depois, geração do código.
5. **Homologação humana:** checklist de conformidade, registro de ocorrências e commits de correção separados.

## Fluxo de versionamento

- `main`: versões entregues.
- `develop`: integração das funcionalidades.
- `feature/*`: uma branch por entrega (`sdd-specification`, `test-harness`, `task-analyzer-impl`, `readme`).
- Integração sempre via **Pull Request**, com commits semânticos (`feat:`, `fix:`, `test:`, `docs:`).

## Roadmap

- [x] **Fase 1:** especificação SDD, cenários de aceite e CONTEXT_RULES
- [x] **Fase 2:** repositório, código gerado por IA, Test Harness e Pull Requests
- [ ] **Fase 3:** CI/CD com GitHub Actions, Docker e relatório de governança

## Autora

**Taís Döring Freire da Silva**, Ciência da Computação, CEUB.