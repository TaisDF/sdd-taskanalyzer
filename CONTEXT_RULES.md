# CONTEXT_RULES — TaskAnalyzer

Regras de governança de contexto para agentes de IA. Este arquivo deve ser fornecido ao agente de IA, junto com `specs/task_analyzer_spec.md`, em **toda** interação de geração de código.

> Origem: Seções 3 e 4 da Especificação SDD — TaskAnalyzer (Fase 1), alinhadas à versão 1.1 da especificação.

## 1. Diretrizes Arquiteturais (Obrigatórias)

- Utilizar Python 3.12 ou superior.
- Utilizar type hints (anotações de tipo) em todas as funções, métodos e parâmetros.
- Seguir o princípio Single Responsibility (SRP) e as boas práticas de Clean Code / PEP 8.
- Documentar todo o código no padrão Google Style Docstrings (módulos, classes, funções e parâmetros).
- Funções devem ser pequenas, coesas e com um único propósito.
- Tratamento de exceções específico, com mensagens claras e acionáveis (nunca `except: pass`).
- Logs estruturados utilizando o módulo padrão `logging` (sem `print()` para depuração).
- Código legível, de fácil manutenção, com nomes de variáveis e funções descritivos (evitar abreviações ambíguas).

## 2. Proibições Explícitas (Regras Restritivas)

- Não utilizar bibliotecas externas não autorizadas: o código em `src/` usa somente a biblioteca padrão do Python. O `pytest` é autorizado exclusivamente para os testes (listado em `requirements.txt`).
- Não alterar, remover ou adaptar os cenários de teste definidos na Seção 2 de `specs/task_analyzer_spec.md`.
- Não modificar a estrutura de pastas definida na Seção 4 deste arquivo.
- Não persistir dados em arquivos ou bancos de dados nesta fase.
- Não alterar a assinatura (nome, parâmetros e tipos) das funções públicas definidas no contrato sem autorização.
- Não gerar código sem os testes automatizados correspondentes para novas funcionalidades.
- Não inserir código duplicado ou desnecessário (evitar redundância).
- Não assumir comportamentos não especificados no contrato de negócio — em caso de ambiguidade, a IA deve sinalizar a lacuna em vez de "inventar" uma regra.

## 3. Regras de Interação com a IA

- Sempre fornecer o contexto completo (`specs/task_analyzer_spec.md` + `CONTEXT_RULES.md`) antes de solicitar geração de código.
- Validar se a IA compreendeu o contrato de negócio antes de aceitar o código gerado.
- Solicitar explicações quando houver dúvida sobre a solução proposta pela IA.
- Revisar criticamente todo código gerado antes de aceitar (homologação humana — ver Seção 5).
- Rejeitar respostas que violem qualquer proibição listada na Seção 2.

## 4. Estrutura de Pastas do Repositório (fixa)

```
sdd-taskanalyzer/
├── README.md                 # Visão geral do projeto no GitHub
├── CONTEXT_RULES.md          # Regras persistentes para os agentes de IA
├── .gitignore                # Arquivos e pastas ignorados pelo Git
├── requirements.txt          # Dependências do projeto (pytest)
├── specs/
│   └── task_analyzer_spec.md # Especificação SDD (contrato)
├── tests/
│   ├── conftest.py           # Fixtures compartilhadas dos testes
│   └── test_harness.py       # Testes automatizados (pytest) dos cenários de aceite
└── src/
    └── task_analyzer.py      # Código-fonte gerado por IA e homologado por humano
```

Qualquer necessidade de alteração deve ser justificada e registrada como nova versão da especificação.

## 5. Plano de Homologação Humana

Todo código gerado pela IA é submetido a revisão crítica humana antes de ser aceito e versionado:

1. Execução completa dos testes automatizados (pytest) para validação funcional de todos os cenários.
2. Revisão de conformidade com o contrato de negócio (`specs/task_analyzer_spec.md`) e com estas regras de contexto.
3. Análise de qualidade do código: legibilidade, tratamento de erros, aderência ao PEP 8 e aos padrões definidos.
4. Testes manuais complementares em casos de borda não cobertos automaticamente.
5. Aprovação e commit: somente após a aprovação nos quatro passos anteriores o código é comitado no repositório.

A IA é uma ferramenta produtiva no desenvolvimento, mas a decisão final e a responsabilidade técnica permanecem sempre humanas.