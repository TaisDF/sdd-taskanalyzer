"""Test Harness do TaskAnalyzer (pytest).

Traduz os cenários de aceite da Seção 2 de specs/task_analyzer_spec.md
em testes automatizados:
    Cenário 1 - Sucesso (cálculo correto de métricas).
    Cenário 2 - Exceção/Erro (entradas inválidas).
    Cenário 3 - Divisão por zero / conjunto vazio (casos de borda).
    Cenário 4 - Indicadores por prioridade.
"""

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

import pytest

from src.task_analyzer import TaskValidationError, analyze_tasks

FabricaTarefa = Callable[..., dict[str, Any]]


# ---------------------------------------------------------------------------
# Cenário 1 - Sucesso
# ---------------------------------------------------------------------------


def test_calculo_metricas_sucesso(tarefas_validas: list[dict[str, Any]]) -> None:
    """Cenário 1: totais, tempo médio e taxa de atraso gerais corretos."""
    resultado = analyze_tasks(tarefas_validas)

    assert resultado["total_tarefas"] == 7
    assert resultado["total_concluidas"] == 4
    assert resultado["total_pendentes"] == 2
    assert resultado["total_atrasadas"] == 2
    assert resultado["tempo_medio_conclusao_horas"] == 15.5
    assert resultado["taxa_atraso_percentual"] == 50.0


def test_calculo_metricas_por_prioridade_sucesso(
    tarefas_validas: list[dict[str, Any]],
) -> None:
    """Cenário 1: tempo médio e taxa de atraso por prioridade corretos."""
    indicadores = analyze_tasks(tarefas_validas)["indicadores_por_prioridade"]

    assert indicadores["alta"] == {
        "quantidade_tarefas": 3,
        "quantidade_concluidas": 2,
        "tempo_medio_conclusao_horas": 17.0,
        "taxa_atraso_percentual": 50.0,
    }
    assert indicadores["media"] == {
        "quantidade_tarefas": 2,
        "quantidade_concluidas": 1,
        "tempo_medio_conclusao_horas": 20.0,
        "taxa_atraso_percentual": 0.0,
    }
    assert indicadores["baixa"] == {
        "quantidade_tarefas": 2,
        "quantidade_concluidas": 1,
        "tempo_medio_conclusao_horas": 8.0,
        "taxa_atraso_percentual": 100.0,
    }


def test_arredondamento_duas_casas(criar_tarefa: FabricaTarefa) -> None:
    """Médias e percentuais são arredondados para 2 casas decimais."""
    tarefas = [
        criar_tarefa(1, horas_ate_prazo=24, horas_ate_conclusao=1),
        criar_tarefa(2, horas_ate_prazo=24, horas_ate_conclusao=1),
        criar_tarefa(3, horas_ate_prazo=1, horas_ate_conclusao=2),
    ]

    resultado = analyze_tasks(tarefas)

    assert resultado["tempo_medio_conclusao_horas"] == 1.33
    assert resultado["taxa_atraso_percentual"] == 33.33


def test_conclusao_exatamente_no_prazo_nao_e_atraso(
    criar_tarefa: FabricaTarefa,
) -> None:
    """Atraso exige data_conclusao > prazo; concluir no prazo exato não atrasa."""
    tarefas = [criar_tarefa(1, horas_ate_prazo=10, horas_ate_conclusao=10)]

    resultado = analyze_tasks(tarefas)

    assert resultado["total_atrasadas"] == 0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_datas_naive_tratadas_como_utc(criar_tarefa: FabricaTarefa) -> None:
    """Datas sem fuso horário são consideradas UTC na fronteira do módulo."""
    tarefa = criar_tarefa(1, horas_ate_prazo=24, horas_ate_conclusao=10)
    tarefa["data_criacao"] = tarefa["data_criacao"].replace(tzinfo=None)

    resultado = analyze_tasks([tarefa])

    assert resultado["tempo_medio_conclusao_horas"] == 10.0


# ---------------------------------------------------------------------------
# Cenário 2 - Exceção/Erro
# ---------------------------------------------------------------------------


def test_excecao_data_invalida(criar_tarefa: FabricaTarefa) -> None:
    """Cenário 2: data_conclusao anterior a data_criacao dispara a exceção."""
    tarefa = criar_tarefa(42)
    tarefa["data_conclusao"] = tarefa["data_criacao"] - timedelta(hours=1)

    with pytest.raises(TaskValidationError) as erro:
        analyze_tasks([tarefa])

    mensagem = str(erro.value)
    assert "data_conclusao" in mensagem
    assert "42" in mensagem


@pytest.mark.parametrize(
    ("campo", "valor_invalido"),
    [
        ("status", "em_andamento"),
        ("prioridade", "urgente"),
    ],
)
def test_excecao_enum_invalido(
    criar_tarefa: FabricaTarefa, campo: str, valor_invalido: str
) -> None:
    """Cenário 2: status ou prioridade fora do enum dispara a exceção."""
    tarefa = criar_tarefa(7, **{campo: valor_invalido})

    with pytest.raises(TaskValidationError) as erro:
        analyze_tasks([tarefa])

    mensagem = str(erro.value)
    assert campo in mensagem
    assert "7" in mensagem


def test_excecao_prazo_anterior_a_criacao(criar_tarefa: FabricaTarefa) -> None:
    """Validação de entrada: prazo deve ser posterior a data_criacao."""
    tarefa = criar_tarefa(8, horas_ate_prazo=-1)

    with pytest.raises(TaskValidationError, match="prazo"):
        analyze_tasks([tarefa])


def test_excecao_concluida_sem_data_conclusao(criar_tarefa: FabricaTarefa) -> None:
    """Validação de entrada: tarefa concluída exige data_conclusao."""
    tarefa = criar_tarefa(9, data_conclusao=None)

    with pytest.raises(TaskValidationError, match="data_conclusao"):
        analyze_tasks([tarefa])


def test_excecao_pendente_com_data_conclusao(
    criar_tarefa: FabricaTarefa, data_base: datetime
) -> None:
    """Validação de entrada: tarefa não concluída deve ter data_conclusao None."""
    tarefa = criar_tarefa(10, status="pendente", data_conclusao=data_base)

    with pytest.raises(TaskValidationError, match="data_conclusao"):
        analyze_tasks([tarefa])


def test_excecao_campo_obrigatorio_ausente(criar_tarefa: FabricaTarefa) -> None:
    """Validação de entrada: campo obrigatório ausente dispara a exceção."""
    tarefa = criar_tarefa(11)
    del tarefa["titulo"]

    with pytest.raises(TaskValidationError, match="titulo"):
        analyze_tasks([tarefa])


def test_tarefa_invalida_nao_e_ignorada(
    tarefas_validas: list[dict[str, Any]], criar_tarefa: FabricaTarefa
) -> None:
    """Cenário 2: uma tarefa inválida no meio de válidas não é ignorada."""
    tarefa_invalida = criar_tarefa(99, status="desconhecido")

    with pytest.raises(TaskValidationError):
        analyze_tasks([*tarefas_validas, tarefa_invalida])


# ---------------------------------------------------------------------------
# Cenário 3 - Divisão por zero / conjunto vazio (casos de borda)
# ---------------------------------------------------------------------------


def test_lista_vazia_sem_erro(metricas_zeradas: dict[str, Any]) -> None:
    """Cenário 3: lista vazia retorna a estrutura de métricas zerada."""
    assert analyze_tasks([]) == metricas_zeradas


def test_somente_pendentes_sem_erro(
    tarefas_somente_pendentes: list[dict[str, Any]],
) -> None:
    """Cenário 3: sem tarefas concluídas, médias retornam 0.0 sem exceção."""
    resultado = analyze_tasks(tarefas_somente_pendentes)

    assert resultado["total_tarefas"] == 2
    assert resultado["total_pendentes"] == 2
    assert resultado["total_concluidas"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0
    for indicador in resultado["indicadores_por_prioridade"].values():
        assert indicador["tempo_medio_conclusao_horas"] == 0.0
        assert indicador["taxa_atraso_percentual"] == 0.0


# ---------------------------------------------------------------------------
# Cenário 4 - Indicadores por prioridade
# ---------------------------------------------------------------------------


def test_indicadores_por_prioridade(
    tarefas_concluidas_por_prioridade: list[dict[str, Any]],
) -> None:
    """Cenário 4: cada prioridade é calculada de forma isolada."""
    resultado = analyze_tasks(tarefas_concluidas_por_prioridade)
    indicadores = resultado["indicadores_por_prioridade"]

    assert indicadores["alta"]["taxa_atraso_percentual"] == 100.0
    assert indicadores["media"]["taxa_atraso_percentual"] == 0.0
    assert indicadores["baixa"]["taxa_atraso_percentual"] == 50.0

    assert indicadores["alta"]["tempo_medio_conclusao_horas"] == 9.0
    assert indicadores["media"]["tempo_medio_conclusao_horas"] == 4.0
    assert indicadores["baixa"]["tempo_medio_conclusao_horas"] == 16.0

    assert resultado["taxa_atraso_percentual"] == 60.0
    assert resultado["tempo_medio_conclusao_horas"] == 10.8
