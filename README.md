# GeoCalor Dashboard — Python (Dash/Plotly)

[![Deploy no Render](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render)](https://geocalor-dash.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-2.14-blue?logo=plotly)](https://dash.plotly.com)
[![GitHub](https://img.shields.io/badge/GitHub-Diegoricardox-black?logo=github)](https://github.com/Diegoricardox/geocalor-dash)

> **Painel web interativo** para monitoramento de ondas de calor nas Regiões Metropolitanas brasileiras.  
> Reescrita em Python (Dash/Plotly) do painel original R/Shiny do LAGAS/UnB.

---

## 🌐 Acesso Online

**→ [https://geocalor-dash.onrender.com](https://geocalor-dash.onrender.com)**

> _Nota: O plano gratuito do Render pode ter latência de ~30s na primeira requisição (cold start). Aguarde o carregamento._

---

## 📊 Sobre o Projeto

O **GeoCalor** é um projeto do [Laboratório de Geoprocessamento Aplicado à Saúde (LAGAS)](https://lagas.sites.homologa.unb.br/) da Universidade de Brasília (UnB), vinculado ao **Observatório de Clima e Saúde (OCS/ICICT/Fiocruz)**.

**Dados:** 234.795 registros climáticos diários | 15 Regiões Metropolitanas | 1981–2023  
**Metodologia:** Excess Heat Factor (EHF) — identificação e classificação de ondas de calor  
**Referência:** [Porto et al. (2024) — PLOS ONE e0295766](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295766)

---

## 🗂️ Abas do Painel

| Aba | Conteúdo |
|-----|----------|
| 🏠 Início | KPIs globais, mapa de bolhas, parceiros |
| ℹ️ Sobre o Projeto | Equipe, metodologia EHF, artigo de referência |
| 🌡️ Temperaturas Diárias | Série temporal, EHF diário, Ridge Plot, Calendário EHF |
| 🌊 Ondas de Calor | Polar, heatmap histórico, ranking, tendência, anomalia, Bubble Chart, Radar |
| ⚠️ Eventos Extremos | Mapa interativo, tabela filtrável, distribuição de intensidade |
| 🔔 Sistemas de Alertas | Sazonalidade decadal, streamgraph de intensidade |
| 🧠 Saúde Mental (SIA) | Evidências, CIDs, mortalidade em excesso (Porto et al., 2024) |
| 🏥 Internações (SIH) | O/E ratio por causa e grupo de risco |
| 🪁 SRAG (Vigilância) | Metodologia SIVEP-Gripe, integração planejada |
| 🔄 Atualização de Dados | Upload CSV, validação, status dos dados |

---

## 🚀 Execução Local

### Pré-requisitos
- Python 3.9+
- [GitHub CLI (gh)](https://cli.github.com/) — para autenticação e download dos dados

### Instalação

```bash
# 1. Clonar o repositório
gh repo clone Diegoricardox/geocalor-dash
cd geocalor-dash

# 2. Configurar e iniciar (setup automático)
bash run.sh
```

O `run.sh` irá:
1. Configurar autenticação `gh` para repositório privado
2. Criar ambiente virtual Python
3. Instalar dependências
4. Baixar dados climáticos da Release v1.0 (~7.5 MB)
5. Iniciar o app em `http://localhost:8050`

### Atualização

```bash
cd geocalor-dash
bash update.sh
```

---

## 🏗️ Deploy no Render (gratuito)

1. Acesse [render.com](https://render.com) e crie uma conta
2. Clique em **New → Web Service**
3. Conecte o repositório `Diegoricardox/geocalor-dash`
4. Configure:
   - **Build Command:** `bash build.sh`
   - **Start Command:** `gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - **Python Version:** `3.11.0`
5. Clique em **Create Web Service**

O Render fará deploy automático a cada push no `main`.

---

## 📁 Estrutura do Repositório

```
geocalor-dash/
├── app.py                    # Aplicação principal (layout + callbacks)
├── app/
│   └── utils/
│       ├── data_loader.py    # Carregamento e queries dos dados
│       └── charts.py         # Funções de visualização (21 gráficos)
├── assets/
│   ├── custom.css            # Estilos do painel
│   └── *.png / *.jpg         # Logos institucionais
├── data/
│   └── .gitkeep              # Pasta de dados (ignorada pelo git)
├── build.sh                  # Script de build para deploy (Render)
├── run.sh                    # Script de execução local
├── update.sh                 # Script de atualização via gh CLI
├── Procfile                  # Configuração Gunicorn
├── render.yaml               # Configuração do Render
└── requirements.txt          # Dependências Python
```

---

## 📦 Dados

Os dados climáticos (`temp.csv.gz`, ~7.5 MB) estão disponíveis na **[Release v1.0](https://github.com/Diegoricardox/geocalor-dash/releases/tag/v1.0)** do repositório.

- **Fonte:** INMET / ICEA
- **Período:** 1981–2023
- **Cidades:** 15 Regiões Metropolitanas brasileiras
- **Colunas:** `date`, `cidade`, `tempMax`, `tempMed`, `tempMin`, `Mean_HW_Humidity`, `EHF`, `isHW`, `HW_duration`, `HW_Intensity`

---

## 👥 Equipe

**Painel Python (GeoCalor Dash):** Diego Ricardo Xavier | OCS/ICICT/Fiocruz — 2026

**Projeto GeoCalor (LAGAS/UnB):** Helen Gurgel, Eliane Lima e Silva, Eucilene Santana, Amarilis Bezerra, Bruno Porto, Marina Miranda, Peter Zeilhofer, Caio Leal, Hendesson Alves, Isabella de Sá, Livia Feitosa

**Painel R/Shiny original:** Bruno Porto e Hendesson Alves | [github.com/Diegoricardox/geocalor_shiny](https://github.com/Diegoricardox/geocalor_shiny)

**Financiamento:** CNPq — Processo 444938/2023-0 | IRD — Institut de Recherche pour le Développement

---

## 📄 Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.
