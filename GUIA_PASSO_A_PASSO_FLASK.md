# Organiza — gestão de tarefas

Aplicação de gestão de tarefas criada com Flask, SQLAlchemy e SQLite. Permite
criar, consultar, pesquisar, filtrar, editar e eliminar tarefas.

## Requisitos

- Python 3.10 ou superior
- pip

## Instalação e execução

Na pasta do projeto, abre um terminal e executa:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Abre depois <http://127.0.0.1:5000> no navegador. A base de dados
`instance/tarefas.db` e as tabelas são criadas automaticamente na primeira
execução.

## Utilização

1. Seleciona **Adicionar uma tarefa** e preenche a descrição, data de fim,
   tempo previsto em minutos, categoria e prioridade.
2. Usa o seletor na lista para atualizar rapidamente o estado: **Não iniciada**,
   **Em progresso** ou **Realizada**.
3. Usa **Pesquisar tarefas** e o filtro de estado para encontrar tarefas.
4. Seleciona o ícone de edição para alterar os detalhes ou o ícone `×` para
   eliminar uma tarefa.

As tarefas com data de fim ultrapassada são assinaladas na lista. O resumo
apresenta o total, as tarefas em progresso, as concluídas e as atrasadas.

## Estrutura

```text
trab_recup/
├── run.py
├── requirements.txt
├── .gitignore
├── GUIA_PASSO_A_PASSO_FLASK.md
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── base.html
│       ├── index.html
│       └── editar.html
└── tests/
    └── test_app.py
```

## Testes

Com as dependências instaladas, executa:

```powershell
python -m unittest discover -s tests
```
