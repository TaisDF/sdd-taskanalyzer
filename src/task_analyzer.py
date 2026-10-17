"""Módulo de análise de tarefas e produtividade (TaskAnalyzer).

Implementa o contrato definido em ``specs/task_analyzer_spec.md`` (v1.1):
recebe uma lista de tarefas, valida cada uma delas e calcula indicadores
objetivos de desempenho (totais, tempo médio de conclusão, taxa de atraso e
indicadores por prioridade).

Exemplo:
    >>> analyze_tasks([])["total_tarefas"]
    0
"""

import logging
from collections.abc import Collection
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final

logger: Final[logging.Logger] = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

PRIORIDADES: Final[tuple[str, ...]] = ("baixa", "media", "alta")
STATUS_VALIDOS: Final[tuple[str, ...]] = ("concluida", "pendente", "cancelada")
STATUS_CONCLUIDA: Final[str] = "concluida"
STATUS_PENDENTE: Final[str] = "pendente"
CAMPOS_OBRIGATORIOS: Final[tuple[str, ...]] = (
    "id_tarefa",
    "titulo",
    "prioridade",
    "status",
    "data_criacao",
    "prazo",
)
SEGUNDOS_POR_HORA: Final[float] = 3600.0
PERCENTUAL: Final[float] = 100.0
CASAS_DECIMAIS: Final[int] = 2


class TaskValidationError(Exception):
    """Erro lançado quando uma tarefa viola as regras de validação.

    A mensagem sempre indica o campo e o ``id_tarefa`` que causaram o
    problema (Seção 1.2.1 da especificação).
    """


@dataclass(frozen=True, slots=True)
class _TarefaValidada:
    """Representação interna, imutável e já validada de uma tarefa.

    Attributes:
        id_tarefa: Identificador único da tarefa.
        prioridade: Prioridade da tarefa (``baixa``, ``media`` ou ``alta``).
        status: Status da tarefa (``concluida``, ``pendente`` ou ``cancelada``).
        data_criacao: Data/hora de criação, normalizada para UTC.
        prazo: Data/hora limite, normalizada para UTC.
        data_conclusao: Data/hora de conclusão em UTC, ou ``None``.
    """

    id_tarefa: int
    prioridade: str
    status: str
    data_criacao: datetime
    prazo: datetime
    data_conclusao: datetime | None


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------


def analyze_tasks(tarefas: list[dict[str, Any]]) -> dict[str, Any]:
    """Valida as tarefas e calcula os indicadores de produtividade.

    Args:
        tarefas: Lista de tarefas, cada uma um dicionário com os campos da
            Seção 1.2.2 da especificação.

    Returns:
        Dicionário de métricas com as chaves da Seção 1.2.3 da especificação.

    Raises:
        TaskValidationError: Na primeira tarefa que violar qualquer regra de
            validação. A análise é interrompida e nenhuma tarefa é ignorada.
    """
    logger.debug("Iniciando análise de tarefas.")
    validadas = _validar_tarefas(tarefas)
    resultado = _montar_resultado(validadas)
    logger.debug(
        "Análise concluída: %d tarefas processadas, %d concluídas.",
        resultado["total_tarefas"],
        resultado["total_concluidas"],
    )
    return resultado


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------


def _criar_erro(campo: str, id_tarefa: object, motivo: str) -> TaskValidationError:
    """Cria uma ``TaskValidationError`` com mensagem padronizada e a registra no log.

    Args:
        campo: Nome do campo que causou o problema.
        id_tarefa: Identificador da tarefa (ou ``None`` se não puder ser obtido).
        motivo: Descrição legível da violação.

    Returns:
        A exceção pronta para ser lançada.
    """
    mensagem = f"Tarefa id_tarefa={id_tarefa!r}: campo '{campo}' inválido ({motivo})."
    logger.warning(mensagem)
    return TaskValidationError(mensagem)


def _validar_tarefas(tarefas: object) -> list[_TarefaValidada]:
    """Valida a lista completa de tarefas, na ordem em que foram recebidas.

    Args:
        tarefas: Objeto recebido como entrada de ``analyze_tasks``.

    Returns:
        Lista de tarefas validadas e normalizadas.

    Raises:
        TaskValidationError: Se a entrada não for uma lista, se alguma tarefa
            for inválida ou se houver ``id_tarefa`` duplicado.
    """
    if not isinstance(tarefas, list):
        raise _criar_erro("tarefas", None, "a entrada deve ser uma lista de tarefas")
    validadas: list[_TarefaValidada] = []
    ids_vistos: set[int] = set()
    for posicao, tarefa in enumerate(tarefas):
        validada = _validar_tarefa(tarefa, posicao)
        _verificar_id_unico(validada.id_tarefa, ids_vistos)
        validadas.append(validada)
    return validadas


def _verificar_id_unico(id_tarefa: int, ids_vistos: set[int]) -> None:
    """Garante que o ``id_tarefa`` ainda não apareceu na entrada.

    Args:
        id_tarefa: Identificador da tarefa atual.
        ids_vistos: Identificadores já processados (é atualizado in-place).

    Raises:
        TaskValidationError: Se o identificador estiver duplicado.
    """
    if id_tarefa in ids_vistos:
        raise _criar_erro("id_tarefa", id_tarefa, "identificador duplicado")
    ids_vistos.add(id_tarefa)


def _validar_tarefa(tarefa: object, posicao: int) -> _TarefaValidada:
    """Valida uma única tarefa e a converte para a representação interna.

    Args:
        tarefa: Elemento da lista de entrada.
        posicao: Posição do elemento na lista (usada apenas em mensagens).

    Returns:
        A tarefa validada, com datas normalizadas para UTC.

    Raises:
        TaskValidationError: Na primeira regra de validação violada.
    """
    if not isinstance(tarefa, dict):
        raise _criar_erro("tarefa", None, f"elemento na posição {posicao} não é um dicionário")
    _verificar_campos_obrigatorios(tarefa)
    id_tarefa = _validar_id(tarefa["id_tarefa"])
    _validar_titulo(tarefa["titulo"], id_tarefa)
    prioridade = _validar_enum(tarefa["prioridade"], "prioridade", PRIORIDADES, id_tarefa)
    status = _validar_enum(tarefa["status"], "status", STATUS_VALIDOS, id_tarefa)
    data_criacao = _validar_datetime(tarefa["data_criacao"], "data_criacao", id_tarefa)
    prazo = _validar_datetime(tarefa["prazo"], "prazo", id_tarefa)
    data_conclusao = _validar_data_conclusao(tarefa.get("data_conclusao"), status, id_tarefa)
    _validar_prazo(data_criacao, prazo, id_tarefa)
    _validar_ordem_conclusao(data_criacao, data_conclusao, id_tarefa)
    return _TarefaValidada(
        id_tarefa=id_tarefa,
        prioridade=prioridade,
        status=status,
        data_criacao=data_criacao,
        prazo=prazo,
        data_conclusao=data_conclusao,
    )


def _verificar_campos_obrigatorios(tarefa: dict[str, Any]) -> None:
    """Verifica a presença de todos os campos obrigatórios.

    Args:
        tarefa: Dicionário da tarefa.

    Raises:
        TaskValidationError: Se algum campo obrigatório estiver ausente.
    """
    id_tarefa = tarefa.get("id_tarefa")
    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in tarefa:
            raise _criar_erro(campo, id_tarefa, "campo obrigatório ausente")


def _validar_id(valor: object) -> int:
    """Valida o campo ``id_tarefa`` (inteiro maior que zero).

    Args:
        valor: Valor recebido em ``id_tarefa``.

    Returns:
        O identificador validado.

    Raises:
        TaskValidationError: Se não for ``int`` (``bool`` é rejeitado) ou se
            não for maior que zero.
    """
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise _criar_erro("id_tarefa", valor, "deve ser do tipo int")
    if valor <= 0:
        raise _criar_erro("id_tarefa", valor, "deve ser maior que zero")
    return valor


def _validar_titulo(valor: object, id_tarefa: int) -> None:
    """Valida o campo ``titulo`` (string não vazia).

    Args:
        valor: Valor recebido em ``titulo``.
        id_tarefa: Identificador da tarefa, para a mensagem de erro.

    Raises:
        TaskValidationError: Se não for ``str`` ou se for vazio/só espaços.
    """
    if not isinstance(valor, str):
        raise _criar_erro("titulo", id_tarefa, "deve ser do tipo str")
    if not valor.strip():
        raise _criar_erro("titulo", id_tarefa, "não pode ser vazio")


def _validar_enum(
    valor: object, campo: str, aceitos: Collection[str], id_tarefa: int
) -> str:
    """Valida um campo enumerado (comparação exata, sensível a maiúsculas).

    Args:
        valor: Valor recebido no campo.
        campo: Nome do campo (``prioridade`` ou ``status``).
        aceitos: Valores permitidos para o campo.
        id_tarefa: Identificador da tarefa, para a mensagem de erro.

    Returns:
        O valor validado.

    Raises:
        TaskValidationError: Se o valor não for ``str`` ou não estiver em ``aceitos``.
    """
    if not isinstance(valor, str) or valor not in aceitos:
        raise _criar_erro(campo, id_tarefa, f"valor {valor!r} fora de {list(aceitos)}")
    return valor


def _validar_datetime(valor: object, campo: str, id_tarefa: int) -> datetime:
    """Valida que o valor é ``datetime`` e o normaliza para UTC.

    Args:
        valor: Valor recebido no campo de data.
        campo: Nome do campo de data.
        id_tarefa: Identificador da tarefa, para a mensagem de erro.

    Returns:
        A data/hora em UTC.

    Raises:
        TaskValidationError: Se o valor não for ``datetime``.
    """
    if not isinstance(valor, datetime):
        raise _criar_erro(campo, id_tarefa, "deve ser do tipo datetime")
    return _normalizar_utc(valor)


def _normalizar_utc(valor: datetime) -> datetime:
    """Converte uma data/hora para UTC sem alterar o objeto original.

    Datas "naive" (sem fuso) são consideradas UTC; datas com fuso são
    convertidas para UTC.

    Args:
        valor: Data/hora a normalizar.

    Returns:
        Nova instância de ``datetime`` com ``tzinfo`` UTC.
    """
    if valor.tzinfo is None or valor.utcoffset() is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def _validar_data_conclusao(
    valor: object, status: str, id_tarefa: int
) -> datetime | None:
    """Valida ``data_conclusao`` de acordo com o ``status`` da tarefa.

    Uma chave ausente é tratada como ``None``.

    Args:
        valor: Valor recebido em ``data_conclusao`` (ou ``None``).
        status: Status já validado da tarefa.
        id_tarefa: Identificador da tarefa, para a mensagem de erro.

    Returns:
        A data de conclusão em UTC para tarefas concluídas; ``None`` nos demais casos.

    Raises:
        TaskValidationError: Se faltar para tarefa concluída, se estiver
            preenchida para outro status ou se tiver tipo inválido.
    """
    if status != STATUS_CONCLUIDA:
        if valor is not None:
            raise _criar_erro("data_conclusao", id_tarefa, f"deve ser None quando status é '{status}'")
        return None
    if valor is None:
        raise _criar_erro("data_conclusao", id_tarefa, "obrigatória quando status é 'concluida'")
    return _validar_datetime(valor, "data_conclusao", id_tarefa)


def _validar_prazo(data_criacao: datetime, prazo: datetime, id_tarefa: int) -> None:
    """Garante que o prazo seja estritamente posterior à data de criação.

    Args:
        data_criacao: Data de criação em UTC.
        prazo: Prazo em UTC.
        id_tarefa: Identificador da tarefa, para a mensagem de erro.

    Raises:
        TaskValidationError: Se ``prazo <= data_criacao``.
    """
    if prazo <= data_criacao:
        raise _criar_erro("prazo", id_tarefa, "deve ser posterior a data_criacao")


def _validar_ordem_conclusao(
    data_criacao: datetime, data_conclusao: datetime | None, id_tarefa: int
) -> None:
    """Garante que a conclusão não seja anterior à criação.

    Args:
        data_criacao: Data de criação em UTC.
        data_conclusao: Data de conclusão em UTC, ou ``None``.
        id_tarefa: Identificador da tarefa, para a mensagem de erro.

    Raises:
        TaskValidationError: Se ``data_conclusao < data_criacao``.
    """
    if data_conclusao is not None and data_conclusao < data_criacao:
        raise _criar_erro("data_conclusao", id_tarefa, "não pode ser anterior a data_criacao")


# ---------------------------------------------------------------------------
# Cálculo de métricas
# ---------------------------------------------------------------------------


def _dividir_com_seguranca(numerador: float, denominador: float) -> float:
    """Divide dois números, retornando ``0.0`` quando o denominador é zero.

    Args:
        numerador: Dividendo.
        denominador: Divisor.

    Returns:
        O quociente, ou ``0.0`` se ``denominador == 0``.
    """
    if denominador == 0:
        return 0.0
    return numerador / denominador


def _arredondar(valor: float) -> float:
    """Arredonda um valor para o número de casas decimais da saída.

    Args:
        valor: Valor a arredondar.

    Returns:
        O valor arredondado para ``CASAS_DECIMAIS`` casas.
    """
    return round(valor, CASAS_DECIMAIS)


def _filtrar_por_status(tarefas: list[_TarefaValidada], status: str) -> list[_TarefaValidada]:
    """Retorna as tarefas com o status informado.

    Args:
        tarefas: Tarefas validadas.
        status: Status desejado.

    Returns:
        Subconjunto das tarefas com esse status.
    """
    return [tarefa for tarefa in tarefas if tarefa.status == status]


def _filtrar_por_prioridade(
    tarefas: list[_TarefaValidada], prioridade: str
) -> list[_TarefaValidada]:
    """Retorna as tarefas com a prioridade informada.

    Args:
        tarefas: Tarefas validadas.
        prioridade: Prioridade desejada.

    Returns:
        Subconjunto das tarefas com essa prioridade.
    """
    return [tarefa for tarefa in tarefas if tarefa.prioridade == prioridade]


def _esta_atrasada(tarefa: _TarefaValidada) -> bool:
    """Indica se a tarefa foi concluída após o prazo.

    Args:
        tarefa: Tarefa validada.

    Returns:
        ``True`` se estiver concluída e ``data_conclusao > prazo``.
    """
    return tarefa.data_conclusao is not None and tarefa.data_conclusao > tarefa.prazo


def _horas_para_conclusao(tarefa: _TarefaValidada) -> float:
    """Calcula as horas entre a criação e a conclusão da tarefa.

    Args:
        tarefa: Tarefa validada.

    Returns:
        Horas decorridas, ou ``0.0`` se a tarefa não tiver data de conclusão.
    """
    if tarefa.data_conclusao is None:
        return 0.0
    segundos = (tarefa.data_conclusao - tarefa.data_criacao).total_seconds()
    return _dividir_com_seguranca(segundos, SEGUNDOS_POR_HORA)


def _contar_atrasadas(concluidas: list[_TarefaValidada]) -> int:
    """Conta as tarefas concluídas após o prazo.

    Args:
        concluidas: Tarefas com status ``concluida``.

    Returns:
        Quantidade de tarefas atrasadas.
    """
    return sum(1 for tarefa in concluidas if _esta_atrasada(tarefa))


def _tempo_medio_horas(concluidas: list[_TarefaValidada]) -> float:
    """Calcula o tempo médio de conclusão, em horas, sem arredondar.

    Args:
        concluidas: Tarefas com status ``concluida``.

    Returns:
        Média das horas de conclusão, ou ``0.0`` se a lista for vazia.
    """
    total_horas = sum(_horas_para_conclusao(tarefa) for tarefa in concluidas)
    return _dividir_com_seguranca(total_horas, len(concluidas))


def _taxa_atraso_percentual(concluidas: list[_TarefaValidada]) -> float:
    """Calcula o percentual de tarefas concluídas com atraso, sem arredondar.

    Args:
        concluidas: Tarefas com status ``concluida``.

    Returns:
        Percentual (0–100) de atrasadas, ou ``0.0`` se a lista for vazia.
    """
    return _dividir_com_seguranca(_contar_atrasadas(concluidas), len(concluidas)) * PERCENTUAL


def _indicadores_da_prioridade(tarefas_da_prioridade: list[_TarefaValidada]) -> dict[str, Any]:
    """Calcula os indicadores isolados de uma prioridade.

    Args:
        tarefas_da_prioridade: Todas as tarefas de uma única prioridade.

    Returns:
        Dicionário com ``quantidade_tarefas``, ``quantidade_concluidas``,
        ``tempo_medio_conclusao_horas`` e ``taxa_atraso_percentual``.
    """
    concluidas = _filtrar_por_status(tarefas_da_prioridade, STATUS_CONCLUIDA)
    return {
        "quantidade_tarefas": len(tarefas_da_prioridade),
        "quantidade_concluidas": len(concluidas),
        "tempo_medio_conclusao_horas": _arredondar(_tempo_medio_horas(concluidas)),
        "taxa_atraso_percentual": _arredondar(_taxa_atraso_percentual(concluidas)),
    }


def _indicadores_por_prioridade(tarefas: list[_TarefaValidada]) -> dict[str, dict[str, Any]]:
    """Monta os indicadores para todas as prioridades, sempre presentes.

    Args:
        tarefas: Tarefas validadas.

    Returns:
        Dicionário com as chaves ``baixa``, ``media`` e ``alta``.
    """
    return {
        prioridade: _indicadores_da_prioridade(_filtrar_por_prioridade(tarefas, prioridade))
        for prioridade in PRIORIDADES
    }


def _montar_resultado(tarefas: list[_TarefaValidada]) -> dict[str, Any]:
    """Consolida todas as métricas no formato de saída da especificação.

    Args:
        tarefas: Tarefas validadas.

    Returns:
        Dicionário de métricas conforme a Seção 1.2.3 da especificação.
    """
    concluidas = _filtrar_por_status(tarefas, STATUS_CONCLUIDA)
    return {
        "total_tarefas": len(tarefas),
        "total_concluidas": len(concluidas),
        "total_pendentes": len(_filtrar_por_status(tarefas, STATUS_PENDENTE)),
        "total_atrasadas": _contar_atrasadas(concluidas),
        "tempo_medio_conclusao_horas": _arredondar(_tempo_medio_horas(concluidas)),
        "taxa_atraso_percentual": _arredondar(_taxa_atraso_percentual(concluidas)),
        "indicadores_por_prioridade": _indicadores_por_prioridade(tarefas),
    }