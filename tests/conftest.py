"""Fixtures compartilhadas do Test Harness do TaskAnalyzer.

As fixtures representam os conjuntos de dados definidos na Seção 2.2 de
specs/task_analyzer_spec.md: listas de tarefas válidas, fábrica para
montar tarefas com erros propositais e listas vazias.
"""

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

DATA_BASE: datetime = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)

FabricaTarefa = Callable[..., dict[str, Any]]


@pytest.fixture
def data_base() -> datetime:
    """Data/hora de referência (UTC) usada para montar as tarefas de teste."""
    return DATA_BASE


@pytest.fixture
def criar_tarefa() -> FabricaTarefa:
    """Fábrica que monta uma tarefa válida, com datas relativas à DATA_BASE.

    Returns:
        Função que recebe os dados principais da tarefa e campos extras
        (sobrescritas) para forçar valores inválidos nos testes de erro.
    """

    def _criar(
        id_tarefa: int = 1,
        prioridade: str = "media",
        status: str = "concluida",
        horas_ate_prazo: float = 24,
        horas_ate_conclusao: float | None = 10,
        **sobrescritas: Any,
    ) -> dict[str, Any]:
        data_conclusao = (
            DATA_BASE + timedelta(hours=horas_ate_conclusao)
            if status == "concluida" and horas_ate_conclusao is not None
            else None
        )
        tarefa: dict[str, Any] = {
            "id_tarefa": id_tarefa,
            "titulo": f"Tarefa {id_tarefa}",
            "prioridade": prioridade,
            "status": status,
            "data_criacao": DATA_BASE,
            "prazo": DATA_BASE + timedelta(hours=horas_ate_prazo),
            "data_conclusao": data_conclusao,
        }
        tarefa.update(sobrescritas)
        return tarefa

    return _criar


@pytest.fixture
def tarefas_validas(criar_tarefa: FabricaTarefa) -> list[dict[str, Any]]:
    """Cenário 1: tarefas válidas com prioridades, prazos e status variados.

    Valores esperados (calculados à mão):
        Concluídas: 1 (10h), 2 (24h, atrasada), 3 (20h), 4 (8h, atrasada).
        Tempo médio geral: (10 + 24 + 20 + 8) / 4 = 15.5 horas.
        Taxa de atraso geral: 2 / 4 = 50.0%.
    """
    return [
        criar_tarefa(1, "alta", "concluida", horas_ate_prazo=24, horas_ate_conclusao=10),
        criar_tarefa(2, "alta", "concluida", horas_ate_prazo=12, horas_ate_conclusao=24),
        criar_tarefa(3, "media", "concluida", horas_ate_prazo=48, horas_ate_conclusao=20),
        criar_tarefa(4, "baixa", "concluida", horas_ate_prazo=6, horas_ate_conclusao=8),
        criar_tarefa(5, "media", "pendente", horas_ate_prazo=96),
        criar_tarefa(6, "baixa", "cancelada", horas_ate_prazo=96),
        criar_tarefa(7, "alta", "pendente", horas_ate_prazo=96),
    ]


@pytest.fixture
def tarefas_concluidas_por_prioridade(
    criar_tarefa: FabricaTarefa,
) -> list[dict[str, Any]]:
    """Cenário 4: apenas tarefas concluídas, distribuídas nas três prioridades.

    alta: 2 concluídas, ambas atrasadas -> taxa 100.0%.
    media: 1 concluída no prazo -> taxa 0.0%.
    baixa: 2 concluídas, 1 atrasada -> taxa 50.0%.
    """
    return [
        criar_tarefa(10, "alta", "concluida", horas_ate_prazo=5, horas_ate_conclusao=6),
        criar_tarefa(11, "alta", "concluida", horas_ate_prazo=5, horas_ate_conclusao=12),
        criar_tarefa(12, "media", "concluida", horas_ate_prazo=24, horas_ate_conclusao=4),
        criar_tarefa(13, "baixa", "concluida", horas_ate_prazo=24, horas_ate_conclusao=30),
        criar_tarefa(14, "baixa", "concluida", horas_ate_prazo=24, horas_ate_conclusao=2),
    ]


@pytest.fixture
def tarefas_somente_pendentes(criar_tarefa: FabricaTarefa) -> list[dict[str, Any]]:
    """Caso de borda: nenhuma tarefa concluída (só pendentes)."""
    return [
        criar_tarefa(20, "alta", "pendente"),
        criar_tarefa(21, "baixa", "pendente"),
    ]


@pytest.fixture
def metricas_zeradas() -> dict[str, Any]:
    """Estrutura de saída esperada para lista vazia (Seção 1.2.3 da spec)."""
    indicador_zerado: dict[str, Any] = {
        "quantidade_tarefas": 0,
        "quantidade_concluidas": 0,
        "tempo_medio_conclusao_horas": 0.0,
        "taxa_atraso_percentual": 0.0,
    }
    return {
        "total_tarefas": 0,
        "total_concluidas": 0,
        "total_pendentes": 0,
        "total_atrasadas": 0,
        "tempo_medio_conclusao_horas": 0.0,
        "taxa_atraso_percentual": 0.0,
        "indicadores_por_prioridade": {
            "baixa": dict(indicador_zerado),
            "media": dict(indicador_zerado),
            "alta": dict(indicador_zerado),
        },
    }