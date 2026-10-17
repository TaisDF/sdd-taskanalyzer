# Especificação SDD — TaskAnalyzer

**Versão:** 1.1
**Disciplina:** Bootcamp III — CEUB
**Autora:** Taís Döring Freire da Silva — Ciência da Computação — Asa Norte, Turma A
**Vídeo da Fase 1:** https://youtu.be/xCN6W3L6dgo

> Esta especificação é a **fonte da verdade** do projeto. Qualquer alteração de nome, tipo ou comportamento aqui definido é tratada como quebra de contrato e deve gerar nova versão deste documento.

## Histórico de Alterações

| Versão | Data | Descrição |
|---|---|---|
| 1.0 | 12/09/2026 | Versão inicial (Fase 1). |
| 1.1 | 17/10/2026 | Alinhamento ao enunciado da Fase 2 (detalhes abaixo). |

**Alterações da versão 1.1:**

1. Exceção padronizada como `TaskValidationError` (na v1.0 citada como exemplo: `TarefaInvalidaError`), conforme exigido no enunciado da Fase 2.
2. Campos de saída renomeados conforme o enunciado da Fase 2: `quantidade_tarefas` → `total_tarefas`; `tempo_medio_conclusao` → `tempo_medio_conclusao_horas`.
3. `indicadores_por_prioridade` passa a incluir `tempo_medio_conclusao_horas` por prioridade (lacuna da v1.0, exigida pelo enunciado da Fase 2) e tem suas chaves internas definidas.
4. Definida a assinatura da função pública `analyze_tasks`.
5. Explicitado que campo obrigatório ausente ou com tipo inválido também dispara `TaskValidationError`.
6. Esclarecido o Cenário 2: a análise é interrompida na primeira tarefa inválida com `TaskValidationError`; nenhuma tarefa inválida é ignorada silenciosamente.
7. Nome do repositório definido como `sdd-taskanalyzer` (nome exigido pelo enunciado da Fase 2).

---

## 1. Visão Geral e Contrato de Negócio

### 1.1 Propósito do Módulo

O TaskAnalyzer é um módulo de análise de tarefas e produtividade que recebe uma lista de tarefas de um usuário ou equipe e calcula indicadores objetivos de desempenho. O objetivo é permitir que gestores e colaboradores identifiquem gargalos, meçam a eficiência da entrega e priorizem ações corretivas com base em dados, e não em percepção subjetiva.

Escopo funcional:

- Cálculo do tempo médio de conclusão das tarefas concluídas.
- Cálculo da taxa de atraso (percentual de tarefas concluídas após o prazo).
- Geração de indicadores por prioridade (baixa, media, alta).
- Consolidação de totais gerais (tarefas processadas, concluídas, pendentes e atrasadas).

### 1.2 Contrato Executável de Interface

#### 1.2.1 Função Pública e Exceção

```python
class TaskValidationError(Exception): ...

def analyze_tasks(tarefas: list[dict[str, Any]]) -> dict[str, Any]: ...
```

- Módulo: `src/task_analyzer.py`.
- `analyze_tasks` recebe uma lista de tarefas e retorna o dicionário de métricas (Seção 1.2.3).
- `TaskValidationError` é lançada quando qualquer tarefa viola as regras de validação (Seção 1.2.2), com mensagem indicando o **campo** e o **id_tarefa** que causou o problema.

#### 1.2.2 Entradas

Cada tarefa é um dicionário com os campos:

| Campo | Tipo | Obrigatório | Descrição / Restrições |
|---|---|---|---|
| `id_tarefa` | `int` | Sim | Identificador único da tarefa (> 0) |
| `titulo` | `str` | Sim | Nome/descrição curta da tarefa (não vazio) |
| `prioridade` | `str` (enum) | Sim | Um dos valores: `"baixa"`, `"media"`, `"alta"` |
| `status` | `str` (enum) | Sim | Um dos valores: `"concluida"`, `"pendente"`, `"cancelada"` |
| `data_criacao` | `datetime` | Sim | Data/hora de criação da tarefa (UTC) |
| `prazo` | `datetime` | Sim | Data/hora limite para conclusão (UTC) |
| `data_conclusao` | `datetime` ou `None` | Não | Obrigatório quando `status == "concluida"`; deve ser `None` caso contrário |

Regras de validação (qualquer violação dispara `TaskValidationError`):

- Todos os campos obrigatórios devem estar presentes e com o tipo correto.
- `data_conclusao`, quando presente, não pode ser anterior a `data_criacao`.
- `prazo` deve ser posterior a `data_criacao`.
- `status` e `prioridade` devem pertencer aos valores aceitos.
- `data_conclusao` é obrigatória quando `status == "concluida"` e deve ser `None` nos demais casos.
- Fuso horário: todas as datas são tratadas em UTC; entradas "naive" (sem timezone) são consideradas UTC na fronteira do módulo.

#### 1.2.3 Saídas

| Campo | Tipo | Descrição |
|---|---|---|
| `total_tarefas` | `int` | Total de tarefas processadas na entrada |
| `total_concluidas` | `int` | Total de tarefas com status `concluida` |
| `total_pendentes` | `int` | Total de tarefas com status `pendente` |
| `total_atrasadas` | `int` | Total de tarefas concluídas com `data_conclusao > prazo` |
| `tempo_medio_conclusao_horas` | `float` | Média, em horas, do tempo entre `data_criacao` e `data_conclusao`, apenas das tarefas concluídas |
| `taxa_atraso_percentual` | `float` (0–100) | `total_atrasadas / total_concluidas * 100` |
| `indicadores_por_prioridade` | `dict` | Uma entrada para cada prioridade (`baixa`, `media`, `alta`), sempre presentes |

Cada entrada de `indicadores_por_prioridade` contém:

| Chave | Tipo | Descrição |
|---|---|---|
| `quantidade_tarefas` | `int` | Total de tarefas da prioridade |
| `quantidade_concluidas` | `int` | Tarefas concluídas da prioridade |
| `tempo_medio_conclusao_horas` | `float` | Tempo médio de conclusão, em horas, das concluídas da prioridade |
| `taxa_atraso_percentual` | `float` (0–100) | Atrasadas da prioridade / concluídas da prioridade * 100 |

Exemplo de saída para lista vazia:

```python
{
    "total_tarefas": 0,
    "total_concluidas": 0,
    "total_pendentes": 0,
    "total_atrasadas": 0,
    "tempo_medio_conclusao_horas": 0.0,
    "taxa_atraso_percentual": 0.0,
    "indicadores_por_prioridade": {
        "baixa": {"quantidade_tarefas": 0, "quantidade_concluidas": 0,
                  "tempo_medio_conclusao_horas": 0.0, "taxa_atraso_percentual": 0.0},
        "media": {"quantidade_tarefas": 0, "quantidade_concluidas": 0,
                  "tempo_medio_conclusao_horas": 0.0, "taxa_atraso_percentual": 0.0},
        "alta":  {"quantidade_tarefas": 0, "quantidade_concluidas": 0,
                  "tempo_medio_conclusao_horas": 0.0, "taxa_atraso_percentual": 0.0},
    },
}
```

#### 1.2.4 Regras de Negócio e Restrições

- Tempo médio e taxa de atraso consideram **apenas** tarefas com status `concluida`. Tarefas `pendente` e `cancelada` entram apenas nas contagens de totais.
- Uma tarefa é atrasada quando está concluída e `data_conclusao > prazo`.
- Evitar divisão por zero: sem tarefas concluídas (no geral ou em uma prioridade), tempo médio e taxa de atraso retornam `0.0`, sem exceção (condição de negócio válida, não erro).
- Lista de tarefas vazia é entrada válida e retorna a estrutura de métricas zerada.
- Arredondamento: médias e percentuais arredondados para 2 casas decimais na saída final.

---

## 2. Cenários de Aceite e Test Harness

### 2.1 Cenários de Aceite (Dado–Quando–Então)

**Cenário 1 – Sucesso (cálculo correto de métricas)**
- **Dado** um conjunto de tarefas válidas, com diferentes prioridades, prazos e status (concluídas e pendentes);
- **Quando** o analisador for executado;
- **Então** ele deve retornar as métricas corretas: totais gerais, tempo médio de conclusão (geral e por prioridade) e taxa de atraso (geral e por prioridade) — calculados exclusivamente a partir das tarefas concluídas, exceto os totais gerais.

**Cenário 2 – Exceção/Erro (entradas inválidas)**
- **Dado** uma entrada com datas inválidas (ex.: `data_conclusao` anterior a `data_criacao`) ou um valor de status/prioridade fora do enum permitido;
- **Quando** o analisador for executado;
- **Então** deve disparar `TaskValidationError`, com mensagem clara indicando o campo e a tarefa (`id_tarefa`) que causou o problema, sem ignorar silenciosamente a tarefa inválida.

**Cenário 3 – Divisão por zero / conjunto vazio**
- **Dado** uma lista de tarefas vazia ou um conjunto onde nenhuma tarefa está concluída;
- **Quando** o analisador for executado;
- **Então** deve retornar `tempo_medio_conclusao_horas = 0.0` e `taxa_atraso_percentual = 0.0`, sem lançar exceção.

**Cenário 4 – Indicadores por prioridade**
- **Dado** um conjunto de tarefas concluídas distribuídas entre as três prioridades;
- **Quando** o analisador for executado;
- **Então** `indicadores_por_prioridade` deve conter, para cada prioridade, contagens, tempo médio e taxa de atraso calculados de forma isolada (a taxa de `alta` não pode ser influenciada pelas tarefas de `baixa`/`media`).

### 2.2 Planejamento do Test Harness

1. **Fixtures** em `tests/conftest.py`: listas de tarefas válidas, listas com erros propositais e listas vazias.
2. **Casos de teste** em `tests/test_harness.py`, ao menos um por cenário: `test_calculo_metricas_sucesso`, `test_excecao_data_invalida`, `test_lista_vazia_sem_erro`, `test_indicadores_por_prioridade`, além de casos de borda (ex.: somente tarefas pendentes).
3. **Execução**: `python -m pytest -v`, cobrindo o caminho feliz e os casos de borda.
4. **Critério de aceite da Fase 2**: o código gerado pela IA só é homologado se 100% dos testes passarem sem alteração do contrato da Seção 1.2.