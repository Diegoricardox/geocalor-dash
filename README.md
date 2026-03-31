# GeoCalor Dash (Python)

Este repositório contém a reescrita do painel **GeoCalor** utilizando **Python (Dash/Plotly)**. O objetivo é espelhar as funcionalidades do painel original em R/Shiny, oferecendo uma alternativa de stack para a equipe de desenvolvimento.

## Estrutura do Projeto

```text
geocalor-dash/
├── app/                    # Código fonte da aplicação Dash
│   ├── components/         # Componentes reutilizáveis (gráficos, cards)
│   ├── pages/              # Layouts específicos de cada aba
│   ├── utils/              # Funções auxiliares (ETL, formatação)
│   ├── callbacks.py        # Lógica de interatividade
│   └── layout.py           # Layout principal (Sidebar + Content)
├── assets/                 # Arquivos estáticos (CSS, imagens, logos)
├── data/                   # Dados do projeto (ignorados no git)
├── scripts/                # Scripts de processamento de dados
├── tests/                  # Testes unitários
├── app.py                  # Entry point da aplicação
├── requirements.txt        # Dependências do projeto
└── README.md               # Este arquivo
```

## Como executar localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/Diegoricardox/geocalor-dash.git
   cd geocalor-dash
   ```

2. **Crie um ambiente virtual e instale as dependências:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. **Adicione os dados:**
   Coloque os arquivos de dados (ex: `temp.csv.gz`, `geocalor.duckdb`) na pasta `data/`.

4. **Execute a aplicação:**
   ```bash
   python app.py
   ```
   Acesse `http://localhost:8050` no seu navegador.

## Autoria e Desenvolvimento

**Desenvolvimento do Painel:** Diego Ricardo Xavier | OCS/ICICT/Fiocruz

Projeto original desenvolvido pelo Laboratório de Geografia, Ambiente e Saúde (LAGAS) da Universidade de Brasília (UnB), vinculado ao Observatório de Clima e Saúde (OCS).
