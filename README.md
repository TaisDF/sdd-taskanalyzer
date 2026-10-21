# sdd-taskanalyzer

[![CI - TaskAnalyzer](https://github.com/TaisDF/sdd-taskanalyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/TaisDF/sdd-taskanalyzer/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![Docker](https://img.shields.io/badge/docker-python%3A3.12--slim-2496ED)
![Fase](https://img.shields.io/badge/fase-3%20de%203-brightgreen)

Módulo Python de análise de tarefas e produtividade desenvolvido com **Spec-Driven Development (SDD)**: o código-fonte foi gerado por assistente de IA a partir de um contrato executável, homologado por revisão humana e validado continuamente por um pipeline de CI/CD com testes automatizados, análise de segurança e containerização Docker.

Projeto da disciplina **Bootcamp III — CEUB**.

## Sobre o projeto

O **TaskAnalyzer** recebe uma lista de tarefas e calcula indicadores objetivos de desempenho:

- **Totais gerais:** tarefas processadas, concluídas, pendentes e atrasadas.
- **Tempo médio de conclusão** (em horas), considerando apenas tarefas concluídas.
- **Taxa de atraso** (percentual de tarefas concluídas após o prazo).
- **Indicadores por prioridade** (`baixa`, `media`, `alta`), calculados de forma isolada.

O contrato completo (entradas, saídas, validações e regras de negócio) está em [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md), que é a **fonte da verdade** do projeto.

## Arquitetura de confiança

| Pilar | Artefato | Função |
|---|---|---|
| Motor CI/CD | `.github/workflows/ci.yml` | Executa testes, análise de segurança e build Docker a cada push e Pull Request |
| Empacotamento | `Dockerfile` | Imagem isolada e reproduzível (`python:3.12-slim`, usuário sem privilégios) |
| Orquestração | `docker-compose.yml` | Suíte de testes inteira com um único comando |
| Governança | `CONTEXT_RULES.md` + `specs/` | Regras para a IA e contrato de negócio (SDD) |
| Qualidade | `tests/` | Test Harness com os cenários de aceite |
| Código | `src/task_analyzer.py` | Implementação gerada por IA e homologada |

## Pipeline de CI/CD (GitHub Actions)

Gatilhos: **push** e **Pull Request** nas branches `main` e `develop` (e execução manual).

```
push / pull request
        │
        ├──► testes (Python 3.11) ──┐
        ├──► testes (Python 3.12) ──┼──► docker (build + testes no contêiner)
        └──► segurança (Bandit) ────┘
```

| Job | O que faz |
|---|---|
| **Test Harness** | Sobe um runner `ubuntu-latest`, instala as dependências do `requirements.txt` e executa `pytest tests/test_harness.py -v` em Python 3.11 e 3.12, em paralelo |
| **Análise de segurança** | Executa o Bandit (análise estática de segurança) sobre `src/` |
| **Docker** | Só roda se os anteriores passarem: constrói a imagem e executa a suíte dentro do contêiner, via `docker run` e `docker compose run` |

Se qualquer teste falhar, a esteira é interrompida, o build fica vermelho e o Pull Request não pode ser integrado.

## Estrutura do repositório

```
sdd-taskanalyzer/
├── .github/
│   └── workflows/
│       └── ci.yml            # Pipeline de CI/CD (GitHub Actions)
├── Dockerfile                # Empacotamento da aplicação e dos testes
├── docker-compose.yml        # Orquestração local
├── .dockerignore             # Arquivos excluídos da imagem
├── pytest.ini                # Configuração do pytest
├── README.md                 # Este arquivo
├── CONTEXT_RULES.md          # Regras de governança para agentes de IA
├── .gitignore                # Arquivos e pastas ignorados pelo Git
├── requirements.txt          # Dependências (pytest)
├── specs/
│   └── task_analyzer_spec.md # Especificação SDD (contrato)
├── tests/
│   ├── conftest.py           # Fixtures compartilhadas
│   └── test_harness.py       # Test Harness (cenários de aceite)
└── src/
    └── task_analyzer.py      # Código gerado por IA e homologado por humano
```

## Como executar

### Opção 1: Docker (recomendado)

Requer apenas o [Docker](https://docs.docker.com/get-docker/) instalado. Nenhuma instalação de Python é necessária.

```bash
git clone https://github.com/TaisDF/sdd-taskanalyzer.git
cd sdd-taskanalyzer
docker compose run --rm tests
```

Ou, construindo e executando a imagem manualmente:

```bash
docker build -t sdd-taskanalyzer .
docker run --rm sdd-taskanalyzer
```

Resultado esperado: `16 passed`.

### Opção 2: Python local

Requer Python **3.11 ou superior** (o projeto adota 3.12+ como padrão).

**Windows (PowerShell):**

```powershell
git clone https://github.com/TaisDF/sdd-taskanalyzer.git
cd sdd-taskanalyzer
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest tests/test_harness.py -v
```

> Se a ativação do ambiente for bloqueada, execute uma vez:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Linux / macOS:**

```bash
git clone https://github.com/TaisDF/sdd-taskanalyzer.git
cd sdd-taskanalyzer
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
pytest tests/test_harness.py -v
```

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
# resultado["total_tarefas"] == 2
# resultado["tempo_medio_conclusao_horas"] == 30.0
# resultado["taxa_atraso_percentual"] == 100.0
```

Entradas inválidas (por exemplo, `data_conclusao` anterior a `data_criacao`) disparam `TaskValidationError`, com mensagem indicando o campo e o `id_tarefa`.

## Cenários de aceite cobertos

| Cenário | Descrição | Testes |
|---|---|---|
| 1 — Sucesso | Totais, tempo médio e taxa de atraso (geral e por prioridade) | 5 |
| 2 — Erro | Datas inconsistentes, enums inválidos, campos ausentes | 8 |
| 3 — Borda | Lista vazia e somente pendentes retornam `0.0` sem exceção | 2 |
| 4 — Prioridade | Indicadores calculados de forma isolada por prioridade | 1 |

## Governança de IA (Critical-in-the-Loop)

1. **Geração:** o agente de IA implementa a lógica a partir do contrato SDD e do `CONTEXT_RULES.md`.
2. **Barreira SDD:** o código precisa respeitar o contrato executável e as regras de contexto (somente biblioteca padrão, assinatura fixa, sem regras inventadas).
3. **Validação humana:** revisão crítica linha a linha, checklist de conformidade e correções em commits separados.
4. **Integração segura:** o código só entra em `develop` e `main` por Pull Request com o pipeline verde.

## Fluxo de versionamento

- `main`: versões entregues (tags `v2.0-fase2`, `v3.0-fase3`).
- `develop`: integração das funcionalidades.
- `feature/*`: uma branch por entrega.
- Integração sempre via **Pull Request** com o pipeline de CI aprovado e commits semânticos (`feat:`, `fix:`, `test:`, `docs:`, `ci:`, `build:`).

## Roadmap

- [x] **Fase 1:** especificação SDD, cenários de aceite e CONTEXT_RULES
- [x] **Fase 2:** código gerado por IA, Test Harness, versionamento e Pull Requests
- [x] **Fase 3:** CI/CD com GitHub Actions, containerização Docker e governança ética de IA

## Autora

**Taís Döring Freire da Silva**, Ciência da Computação, CEUB.
