"""
GeoCalor Dashboard — Versão Python (Dash/Plotly)
Espelho fiel do painel R/Shiny: https://shiny.icict.fiocruz.br/geocalor/
+ Visualizações originais adicionais

Desenvolvimento: Diego Ricardo Xavier | OCS/ICICT/Fiocruz — 2026
"""

import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc

from app.utils.data_loader import (
    load_data, get_cidades, get_anos, filter_df,
    kpi_global, kpi_cidade_ano, heatmap_cidade_ano,
    polar_mensal, ranking_cidades, tendencia_anual,
    anomalia_termica, distribuicao_intensidade,
    sazonalidade_decadal, eventos_extremos_tabela, mapa_dados,
)
from app.utils.charts import (
    fig_temperatura_diaria, fig_umidade, fig_ehf,
    fig_polar_mensal, fig_heatmap_historico, fig_ranking_barras,
    fig_tendencia_anual, fig_anomalia_termica,
    fig_distribuicao_intensidade, fig_sazonalidade_decadal,
    fig_mapa_bolhas, fig_ridge_mensal, fig_heatmap_calendario,
    fig_bubble_cidades, fig_streamgraph_intensidade, fig_radar_cidade,
    TEAL, ORANGE, GREEN, RED, DARK,
)

# ── Inicializar app ────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title='Dashboard GeoCalor | OCS',
    update_title=None,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
)
server = app.server

# Pré-carregar dados
df_all  = load_data()
CIDADES = get_cidades()
ANOS    = get_anos()
KPI     = kpi_global()

# ── Helpers de UI ──────────────────────────────────────────────────────────

def kpi_box(valor, label, icon, classe='kpi-teal'):
    return html.Div(className=f'kpi-card {classe}', children=[
        html.Div(icon, className='kpi-icon'),
        html.Div([
            html.Div(str(valor), className='kpi-value'),
            html.Div(label, className='kpi-label'),
        ])
    ])


def chart_card(titulo, children, cor='teal'):
    return html.Div(className='chart-card', children=[
        html.Div(titulo, className=f'chart-card-header {cor}'),
        html.Div(children, className='chart-card-body'),
    ])


def dd(id_, options, value, label=None, multi=False):
    items = []
    if label:
        items.append(html.Label(label, style={'fontSize':'12px','fontWeight':'600','color':'#555','marginBottom':'4px'}))
    items.append(dcc.Dropdown(
        id=id_, options=options, value=value, clearable=False, multi=multi,
        style={'fontSize':'13px', 'minWidth':'160px'},
    ))
    return html.Div(items, style={'flex':'1','minWidth':'160px'})


def info_card_saude(titulo, icon, descricao, variaveis, metodologia, status='desenvolvimento'):
    cor_status = {'desenvolvimento': '#e07b39', 'disponivel': '#2a9d8f', 'planejado': '#7b2d8b'}
    label_status = {'desenvolvimento': '🔧 Em desenvolvimento', 'disponivel': '✅ Disponível', 'planejado': '📋 Planejado'}
    return html.Div(className='info-card', children=[
        html.Div(style={'display':'flex','justifyContent':'space-between','alignItems':'flex-start','marginBottom':'12px'}, children=[
            html.H5([html.Span(icon, style={'marginRight':'8px'}), titulo]),
            html.Span(label_status.get(status, status),
                      style={'background': cor_status.get(status,'#999'), 'color':'#fff',
                             'padding':'3px 10px','borderRadius':'12px','fontSize':'11px','fontWeight':'600'}),
        ]),
        html.P(descricao, style={'color':'#555','fontSize':'13px','marginBottom':'12px'}),
        html.Div(style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'12px'}, children=[
            html.Div(style={'background':'#f8f9fa','borderRadius':'6px','padding':'12px'}, children=[
                html.Strong('Variáveis analisadas:', style={'color':TEAL,'fontSize':'12px'}),
                html.Ul([html.Li(v, style={'fontSize':'12px','color':'#555'}) for v in variaveis],
                        style={'margin':'6px 0 0','paddingLeft':'16px'}),
            ]),
            html.Div(style={'background':'#f8f9fa','borderRadius':'6px','padding':'12px'}, children=[
                html.Strong('Metodologia:', style={'color':TEAL,'fontSize':'12px'}),
                html.P(metodologia, style={'fontSize':'12px','color':'#555','margin':'6px 0 0'}),
            ]),
        ]),
    ])


# ── SIDEBAR ────────────────────────────────────────────────────────────────

ABAS = [
    ('inicio',       '🏠', 'Início'),
    ('sobre',        'ℹ️', 'Sobre o Projeto'),
    ('temperaturas', '🌡️', 'Temperaturas Diárias'),
    ('ondas',        '🌊', 'Ondas de Calor'),
    ('extremos',     '⚠️', 'Eventos Extremos'),
    ('alertas',      '🔔', 'Sistemas de Alertas'),
    ('saude_mental', '🧠', 'Saúde Mental (SIA)'),
    ('internacoes',  '🏥', 'Internações (SIH)'),
    ('srag',         '🫁', 'SRAG (Vigilância)'),
    ('originais',    '✨', 'Visualizações Originais'),
]

sidebar = html.Div(id='sidebar', children=[
    html.Div(id='sidebar-brand', children=[
        html.Img(src='/assets/header_geocalor.png', style={'maxWidth':'90px','marginBottom':'6px'}),
        html.Br(),
        html.Img(src='/assets/header_ocs.png', style={'maxWidth':'110px','marginTop':'6px','background':'white','borderRadius':'4px','padding':'3px'}),
        html.P('Monitoramento de ondas de calor e impactos na saúde', style={'marginTop':'8px'}),
    ]),
    html.Nav([
        html.A(
            [html.Span(icon, style={'fontSize':'14px'}), ' ', nome],
            id=f'nav-{aba}', href='#', className='nav-link',
        )
        for aba, icon, nome in ABAS
    ]),
    html.Div(id='sidebar-footer', children=[html.Div('LAGAS/UnB © 2025')]),
])

header = html.Div(id='top-navbar', children=[
    html.Div([
        html.P('Dashboard GeoCalor | OCS', className='brand-title'),
        html.P('Monitoramento de ondas de calor e seus impactos na saúde das populações das Regiões Metropolitanas brasileiras.', className='brand-sub'),
    ]),
    html.Img(src='/assets/header_ocs.png', style={'height':'36px','background':'white','borderRadius':'6px','padding':'3px'}),
])

footer = html.Div(id='footer', children=[
    html.Div(style={'display':'flex','justifyContent':'center','alignItems':'center','gap':'16px','marginBottom':'10px'}, children=[
        html.Img(src='/assets/logo_pcdas.png', style={'height':'28px','background':'white','borderRadius':'4px','padding':'2px 6px'}),
        html.Img(src='/assets/header_ocs.png', style={'height':'28px','background':'white','borderRadius':'4px','padding':'2px 6px'}),
        html.Img(src='/assets/fiocruz.jpg', style={'height':'28px','borderRadius':'4px'}),
    ]),
    html.Div([html.Strong('Desenvolvimento do painel: '), 'Diego Ricardo Xavier | OCS/ICICT/Fiocruz — 2026']),
    html.Div('GeoCalor Dashboard Python | Dados: INMET/ICEA | Metodologia: EHF (Excess Heat Factor)'),
])

# ══════════════════════════════════════════════════════════════════════════
# CONTEÚDO DAS ABAS
# ══════════════════════════════════════════════════════════════════════════

tab_inicio = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', children=[
        html.Img(src='/assets/header_geocalor.png', style={'height':'80px','background':'white','borderRadius':'10px','padding':'6px','boxShadow':'0 2px 8px rgba(0,0,0,0.2)'}),
        html.H1('Dashboard GeoCalor | OCS'),
        html.P('Monitoramento de ondas de calor e seus impactos na saúde das populações das Regiões Metropolitanas brasileiras.'),
    ]),
    dbc.Row([
        dbc.Col(kpi_box(KPI['n_cidades'], 'Regiões Metropolitanas', '🗺️', 'kpi-teal'), md=3),
        dbc.Col(kpi_box(f"{KPI['ano_min']}–{KPI['ano_max']}", f"{KPI['n_anos']} anos de dados", '📅', 'kpi-orange'), md=3),
        dbc.Col(kpi_box(f"{KPI['n_registros']:,}".replace(',','.'), 'Registros climáticos diários', '📊', 'kpi-green'), md=3),
        dbc.Col(kpi_box(f"{KPI['dias_hw']:,}".replace(',','.'), 'Dias de onda de calor (total)', '🔥', 'kpi-brown'), md=3),
    ], className='mb-3'),
    dbc.Row([
        dbc.Col(html.Div(className='info-card', children=[
            html.H5('Sobre o GeoCalor'),
            html.P(['O ', html.Strong('GeoCalor'), ' é um projeto de pesquisa do ', html.Strong('Laboratório de Geoprocessamento Aplicado à Saúde (LAGAS)'), ' da Universidade de Brasília (UnB), vinculado ao Observatório de Clima e Saúde. O projeto monitora e analisa ', html.Strong('ondas de calor'), ' nas principais ', html.Strong('Regiões Metropolitanas brasileiras'), ' e seus impactos na saúde humana, com foco em internações hospitalares, atendimentos ambulatoriais e casos de SRAG.']),
            html.P(['Os dados climáticos são provenientes do ', html.Strong('INMET'), ' e processados utilizando o índice ', html.Strong('Excess Heat Factor (EHF)'), ' para identificação e classificação das ondas de calor em: ', html.Span('Low-Intensity', style={'color':TEAL,'fontWeight':'600'}), ', ', html.Span('Severe', style={'color':ORANGE,'fontWeight':'600'}), ' e ', html.Span('Extreme', style={'color':RED,'fontWeight':'600'}), '.']),
            html.P(['O período de análise abrange de ', html.Strong('1981 a 2023'), ', cobrindo 15 regiões metropolitanas distribuídas por todas as macrorregiões do Brasil.']),
            html.P([html.Strong('Financiamento: '), 'CNPq — Conselho Nacional de Desenvolvimento Científico e Tecnológico. Projeto aprovado no edital PIBIC/UnB 2023–2024.']),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', children=[
            html.H5('Regiões Metropolitanas Monitoradas'),
            html.Ul([html.Li([html.Span('📍', style={'marginRight':'6px'}), c]) for c in CIDADES],
                    style={'columns':'2','listStyle':'none','padding':'0','fontSize':'13px'}),
        ]), md=6),
    ]),
    dbc.Row([
        dbc.Col(html.Div(className='info-card', children=[
            html.H5('Metodologia — Excess Heat Factor (EHF)'),
            html.P('O EHF é calculado como o produto de dois componentes:'),
            html.Ul([
                html.Li([html.Strong('EHI_sig'), ': excesso de calor em relação ao percentil 95 da temperatura de 3 dias']),
                html.Li([html.Strong('EHI_accl'), ': aclimatação — diferença entre a temperatura atual e a média dos 30 dias anteriores']),
            ]),
            html.P(['Uma onda de calor é identificada quando ', html.Strong('EHF > 0'), ' por pelo menos ', html.Strong('3 dias consecutivos'), '. A intensidade é classificada com base no percentil 85 do EHF positivo:']),
            html.Ul([
                html.Li([html.Span('Low-Intensity', style={'color':TEAL,'fontWeight':'600'}), ': EHF entre 0 e p85']),
                html.Li([html.Span('Severe', style={'color':ORANGE,'fontWeight':'600'}), ': EHF entre p85 e 3×p85']),
                html.Li([html.Span('Extreme', style={'color':RED,'fontWeight':'600'}), ': EHF > 3×p85']),
            ]),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', children=[
            html.H5('Limiares de Temperatura Extrema'),
            html.P('Limiares de temperatura extrema utilizados na análise por região metropolitana:'),
            html.Img(src='/assets/limiares_temp.png', style={'width':'100%','borderRadius':'6px'}),
        ]), md=6),
    ]),
    chart_card('Mapa — Total de Dias de Onda de Calor por Região Metropolitana (1981–2023)', [
        dcc.Graph(id='mapa-bolhas-inicio', figure=fig_mapa_bolhas(mapa_dados()), config={'displayModeBar': False}),
    ], 'teal'),
    html.Div(className='parceiros-bar', children=[
        html.H6('Parceiros e Financiadores'),
        html.Div(style={'display':'flex','flexWrap':'wrap','justifyContent':'center','alignItems':'center','gap':'8px'}, children=[
            html.Img(src='/assets/unb.png', style={'height':'45px'}),
            html.Img(src='/assets/cnpq.png', style={'height':'45px'}),
            html.Img(src='/assets/fiocruz.jpg', style={'height':'45px'}),
            html.Img(src='/assets/inmet.png', style={'height':'45px'}),
            html.Img(src='/assets/icea.png', style={'height':'45px'}),
            html.Img(src='/assets/header_ocs.png', style={'height':'45px','background':'#f0f0f0','borderRadius':'4px','padding':'3px'}),
            html.Img(src='/assets/logo_pcdas.png', style={'height':'45px'}),
        ]),
        html.P([html.Strong('Desenvolvimento do painel: '), 'Diego Ricardo Xavier | OCS/ICICT/Fiocruz — 2026'],
               style={'marginTop':'12px','fontSize':'12px','color':'#777'}),
    ]),
])

tab_sobre = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', style={'padding':'30px'}, children=[
        html.H1('Painel de Dados Climáticos — Projeto GeoCalor'),
        html.P('Laboratório de Geografia, Ambiente e Saúde (LAGAS) | Universidade de Brasília (UnB)'),
    ]),
    html.Div(className='info-card', children=[
        html.P(['Este painel é um produto do projeto ', html.Strong("'Indicadores socioespaciais e sistema de alertas de ondas de calor nas regiões metropolitanas brasileiras'"), ', ou GeoCalor para facilitar!']),
        html.Br(),
        html.P([html.Strong('Financiamento do Projeto:')]),
        html.P('CNPq - Conselho Nacional de Desenvolvimento Científico e Tecnológico (Chamada Nº 18/2023 - Processo 444938/2023-0)'),
        html.P('IRD - Institut de Recherche pour le Développement (Instituto Francês de Pesquisa para o Desenvolvimento).'),
        html.Br(),
        html.P([html.Strong('Projeto desenvolvido pelo Laboratório de Geografia, Ambiente e Saúde (LAGAS) da Universidade de Brasília (UnB)')]),
        html.Br(),
        html.P([html.Strong('Equipe do Projeto: '), 'Helen Gurgel, Eliane Lima e Silva, Eucilene Santana, Amarilis Bezerra, Bruno Porto, Marina Miranda, Peter Zeilhofer, Caio Leal, Hendesson Alves, Isabella de Sá, Livia Feitosa']),
        html.P([html.Strong('Construção do Painel (versão R/Shiny): '), 'Bruno Porto e Hendesson Alves']),
        html.P([html.Strong('Desenvolvimento do Painel (versão Python — GeoCalor Dash): '), html.Span('Diego Ricardo Xavier | OCS/ICICT/Fiocruz', style={'color':TEAL,'fontWeight':'600'})]),
        html.P([html.Strong('Fontes dos dados: '), 'Instituto Nacional de Meteorologia (INMET) e Instituto de Controle do Espaço Aéreo (ICEA).']),
        html.Br(),
        html.P([html.Strong('Como Citar:')]),
        html.P('NBR 6023: PORTO, B. et al. Comportamento das ondas de calor em capitais brasileiras através do fator de excesso de calor. Zenodo, 2025.'),
        html.P([html.A('https://doi.org/10.5281/zenodo.15102791', href='https://doi.org/10.5281/zenodo.15102791', target='_blank', style={'color':TEAL})]),
        html.P([html.Strong('Fevereiro de 2025')]),
    ]),
])

tab_temperaturas = html.Div(className='page-wrapper', children=[
    html.Div(className='filter-bar', children=[
        dd('temp-cidade', [{'label': c, 'value': c} for c in CIDADES], 'Belém', 'Região Metropolitana:'),
        dd('temp-ano', [{'label': str(a), 'value': a} for a in ANOS], 2020, 'Ano:'),
        html.Div([
            html.Label('Variáveis:', style={'fontSize':'12px','fontWeight':'600','color':'#555','marginBottom':'4px'}),
            dcc.Checklist(
                id='temp-vars',
                options=[
                    {'label': ' Temperatura Máxima', 'value': 'max'},
                    {'label': ' Temperatura Média',  'value': 'med'},
                    {'label': ' Temperatura Mínima', 'value': 'min'},
                ],
                value=['max', 'med', 'min'],
                inline=True,
                style={'fontSize':'13px'},
                inputStyle={'marginRight':'4px'},
            ),
        ]),
    ]),
    dbc.Row(id='kpi-temp-row', className='mb-3'),
    chart_card('Temperatura Diária com Ondas de Calor', [
        dcc.Graph(id='graf-temp', config={'displayModeBar': False}),
    ], 'teal'),
    dbc.Row([
        dbc.Col(chart_card('Umidade Relativa Diária', [
            dcc.Graph(id='graf-umidade', config={'displayModeBar': False}),
        ], 'teal'), md=6),
        dbc.Col(chart_card('Excess Heat Factor (EHF) Diário', [
            dcc.Graph(id='graf-ehf', config={'displayModeBar': False}),
        ], 'orange'), md=6),
    ]),
    chart_card('✨ Calendário EHF — Visualização por Semana do Ano', [
        html.P('Cada célula representa um dia do ano. Azul = EHF negativo (fresco), vermelho = EHF positivo (calor). Dias de onda de calor se destacam em tons quentes.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-calendario', config={'displayModeBar': False}),
    ], 'purple'),
    chart_card('✨ Distribuição Mensal de Temperatura Máxima (Ridge Plot)', [
        html.P('Distribuição estatística da temperatura máxima por mês. Permite identificar meses com maior variabilidade e valores extremos.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-ridge', config={'displayModeBar': False}),
    ], 'dark'),
])

tab_ondas = html.Div(className='page-wrapper', children=[
    html.Div(className='filter-bar', children=[
        dd('hw-cidade', [{'label': c, 'value': c} for c in CIDADES], 'Belém', 'Região Metropolitana:'),
        dd('hw-ano', [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(a), 'value': a} for a in ANOS], 'Todos', 'Ano (gráficos individuais):'),
        dd('hw-heatmap-tipo',
           [{'label': 'Dias de onda de calor', 'value': 'dias_hw'},
            {'label': 'Temperatura máxima', 'value': 'temp_max'},
            {'label': 'EHF máximo', 'value': 'ehf_max'}],
           'dias_hw', 'Heatmap — Métrica:'),
    ]),
    dbc.Row([
        dbc.Col(chart_card('Frequência Mensal de Ondas de Calor (Gráfico Polar)', [
            dcc.Graph(id='graf-polar', config={'displayModeBar': False}),
        ], 'teal'), md=6),
        dbc.Col(chart_card('Heatmap Histórico por Cidade e Ano', [
            dcc.Graph(id='graf-heatmap-hist', config={'displayModeBar': False}),
        ], 'orange'), md=6),
    ]),
    html.Div(className='chart-card', children=[
        html.Div('Características Médias das Ondas de Calor (Severe + Extreme)', className='chart-card-header brown'),
        html.Div(className='chart-card-body', children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id='graf-rank-temp', config={'displayModeBar': False}), md=6),
                dbc.Col(dcc.Graph(id='graf-rank-dur',  config={'displayModeBar': False}), md=6),
            ]),
        ]),
    ]),
    chart_card('Tendência Anual de Dias de Onda de Calor', [
        dcc.Graph(id='graf-tendencia', config={'displayModeBar': False}),
    ], 'green'),
    chart_card('Anomalia de Temperatura Média Anual (estilo IPCC)', [
        html.P('Barras vermelhas = anos mais quentes que a média histórica; barras azuis = anos mais frios. Evidencia o aquecimento progressivo.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-anomalia', config={'displayModeBar': False}),
    ], 'orange'),
])

tab_extremos = html.Div(className='page-wrapper', children=[
    chart_card('Mapa Interativo de Eventos Extremos nas Regiões Metropolitanas', [
        html.P('Tamanho da bolha = total de dias de onda de calor (1981–2023). Cor = intensidade acumulada. Passe o mouse para detalhes.',
               style={'padding':'8px 12px','fontSize':'13px','color':'#555'}),
        dcc.Graph(id='mapa-extremos', figure=fig_mapa_bolhas(mapa_dados()), config={'displayModeBar': False}),
    ], 'teal'),
    html.Div(className='filter-bar', children=[
        dd('ext-cidade', [{'label': 'Todas', 'value': 'Todas'}] + [{'label': c, 'value': c} for c in CIDADES], 'Todas', 'Região Metropolitana:'),
        html.Div([
            html.Label('Período:', style={'fontSize':'12px','fontWeight':'600','color':'#555','marginBottom':'4px'}),
            dcc.RangeSlider(id='ext-anos', min=1981, max=2023, step=1,
                            value=[1981, 2023],
                            marks={y: str(y) for y in range(1981, 2024, 7)},
                            tooltip={'placement':'bottom','always_visible':False}),
        ], style={'flex':'2','minWidth':'300px'}),
        dd('ext-intensidade',
           [{'label': 'Todas', 'value': 'Todas'},
            {'label': 'Low Intensity', 'value': 'Low Intensity'},
            {'label': 'Severe', 'value': 'Severe'},
            {'label': 'Extreme', 'value': 'Extreme'}],
           'Todas', 'Intensidade:'),
    ]),
    dbc.Row([
        dbc.Col(chart_card('Frequência Mensal de OC — Gráfico Polar', [
            dcc.Graph(id='ext-polar', config={'displayModeBar': False}),
        ], 'orange'), md=5),
        dbc.Col(html.Div(className='chart-card', children=[
            html.Div('Tabela de Eventos Extremos', className='chart-card-header teal'),
            html.Div(className='chart-card-body', style={'padding':'12px'}, children=[
                html.P('Resumo estatístico das ondas de calor por cidade. Filtre por período e intensidade. Clique nas colunas para ordenar.',
                       style={'fontSize':'12px','color':'#666','marginBottom':'8px'}),
                html.Div(id='tabela-extremos'),
            ]),
        ]), md=7),
    ]),
    chart_card('Distribuição de Intensidade das Ondas de Calor por Cidade', [
        html.P('Proporção de dias de onda de calor por intensidade (Low / Severe / Extreme) em cada Região Metropolitana.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-dist-intens', figure=fig_distribuicao_intensidade(distribuicao_intensidade()), config={'displayModeBar': False}),
    ], 'brown'),
])

tab_alertas = html.Div(className='page-wrapper', children=[
    html.Div(className='filter-bar', children=[
        dd('alerta-cidade', [{'label': c, 'value': c} for c in CIDADES], 'Belém', 'Região Metropolitana:'),
    ]),
    chart_card('Sazonalidade das Ondas de Calor por Década', [
        html.P('Frequência mensal de dias de onda de calor agrupada por década. Permite identificar mudanças na sazonalidade ao longo do tempo.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-sazonalidade', config={'displayModeBar': False}),
    ], 'teal'),
    chart_card('✨ Evolução Anual dos Dias de OC por Intensidade — Todas as RMs', [
        html.P('Área empilhada mostrando a evolução temporal da composição de intensidade das ondas de calor em todas as regiões metropolitanas.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-stream', figure=fig_streamgraph_intensidade(df_all), config={'displayModeBar': False}),
    ], 'orange'),
])

tab_saude_mental = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', style={'padding':'24px'}, children=[
        html.H2('🧠 Saúde Mental — Sistema de Informações Ambulatoriais (SIA)'),
        html.P('Análise dos atendimentos ambulatoriais de saúde mental em períodos de ondas de calor nas Regiões Metropolitanas brasileiras.'),
    ]),
    info_card_saude(
        titulo='Saúde Mental e Ondas de Calor',
        icon='🧠',
        descricao='O calor extremo está associado ao aumento de transtornos mentais, agitação, agressividade e piora de condições psiquiátricas preexistentes. Esta seção analisará os atendimentos do SIA/DATASUS em períodos de ondas de calor identificadas pelo índice EHF.',
        variaveis=[
            'Atendimentos ambulatoriais por CID-10 (F00–F99)',
            'Internações por transtornos mentais',
            'Uso de psicotrópicos em períodos de calor',
            'Correlação EHF × demanda por serviços de saúde mental',
        ],
        metodologia='Linkage entre dados climáticos (EHF) e registros do SIA/DATASUS. Análise de séries temporais com modelos de regressão de Poisson e análise de interrupção de séries temporais (ITS).',
        status='desenvolvimento',
    ),
    dbc.Row([
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {TEAL}'}, children=[
            html.H6('Evidências científicas', style={'color':TEAL}),
            html.P('Estudos mostram aumento de 8–12% nas internações psiquiátricas durante ondas de calor severas (EHF > p85). O risco é maior para idosos, pessoas em situação de rua e pacientes com esquizofrenia.', style={'fontSize':'13px','color':'#555'}),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {ORANGE}'}, children=[
            html.H6('Dados utilizados', style={'color':ORANGE}),
            html.P('SIA/DATASUS — Produção Ambulatorial do SUS. CID-10: F00–F99 (Transtornos mentais e comportamentais). Período: 2000–2023. Granularidade: mensal por município.', style={'fontSize':'13px','color':'#555'}),
        ]), md=6),
    ]),
])

tab_internacoes = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', style={'padding':'24px'}, children=[
        html.H2('🏥 Internações Hospitalares — Sistema de Informações Hospitalares (SIH)'),
        html.P('Análise das internações hospitalares em períodos de ondas de calor nas Regiões Metropolitanas brasileiras.'),
    ]),
    info_card_saude(
        titulo='Internações e Ondas de Calor',
        icon='🏥',
        descricao='Ondas de calor aumentam significativamente as internações por doenças cardiovasculares, respiratórias e renais. Esta seção analisará os dados do SIH/DATASUS para quantificar o impacto das ondas de calor nas hospitalizações.',
        variaveis=[
            'Internações por doenças cardiovasculares (CID I00–I99)',
            'Internações por doenças respiratórias (CID J00–J99)',
            'Internações por insuficiência renal (CID N17–N19)',
            'Mortalidade hospitalar em períodos de OC',
            'Tempo de permanência hospitalar',
        ],
        metodologia='Linkage entre dados climáticos (EHF) e AIH do SIH/DATASUS. Modelos de regressão de Poisson com defasagem temporal (lag 0–7 dias). Análise estratificada por faixa etária e sexo.',
        status='desenvolvimento',
    ),
    dbc.Row([
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {TEAL}'}, children=[
            html.H6('Grupos de risco prioritários', style={'color':TEAL}),
            html.Ul([
                html.Li('Idosos (≥ 65 anos): risco 3× maior'),
                html.Li('Crianças (< 5 anos): vulnerabilidade termorregulação'),
                html.Li('Pacientes com doenças crônicas'),
                html.Li('Trabalhadores ao ar livre'),
            ], style={'fontSize':'13px','color':'#555'}),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {ORANGE}'}, children=[
            html.H6('Dados utilizados', style={'color':ORANGE}),
            html.P('SIH/DATASUS — Autorizações de Internação Hospitalar (AIH). Período: 2000–2023. Granularidade: mensal por município de residência. Variáveis: diagnóstico principal, idade, sexo, desfecho.', style={'fontSize':'13px','color':'#555'}),
        ]), md=6),
    ]),
])

tab_srag = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', style={'padding':'24px'}, children=[
        html.H2('🫁 SRAG — Síndrome Respiratória Aguda Grave'),
        html.P('Análise dos casos de SRAG notificados em períodos de ondas de calor nas Regiões Metropolitanas brasileiras.'),
    ]),
    info_card_saude(
        titulo='SRAG e Ondas de Calor',
        icon='🫁',
        descricao='O calor extremo agrava condições respiratórias e aumenta a susceptibilidade a infecções. Esta seção analisará os dados do SIVEP-Gripe para investigar a associação entre ondas de calor e casos de SRAG.',
        variaveis=[
            'Casos notificados de SRAG (SIVEP-Gripe)',
            'Hospitalizações por SRAG',
            'Óbitos por SRAG em períodos de OC',
            'Agentes etiológicos (Influenza, VSR, COVID-19)',
            'Correlação EHF × incidência de SRAG',
        ],
        metodologia='Análise de séries temporais com modelos DLNM (Distributed Lag Non-linear Models) para capturar efeitos defasados e não-lineares do calor sobre a incidência de SRAG. Dados: SIVEP-Gripe/SVS/MS.',
        status='planejado',
    ),
    dbc.Row([
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {TEAL}'}, children=[
            html.H6('Mecanismos biológicos', style={'color':TEAL}),
            html.P('O calor extremo reduz a função mucociliar, aumenta a permeabilidade das mucosas e compromete a resposta imune inata, favorecendo infecções respiratórias. Além disso, o aumento do uso de ar-condicionado pode concentrar patógenos em ambientes fechados.', style={'fontSize':'13px','color':'#555'}),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {ORANGE}'}, children=[
            html.H6('Dados utilizados', style={'color':ORANGE}),
            html.P('SIVEP-Gripe — Sistema de Informação de Vigilância Epidemiológica da Gripe. Período: 2012–2023. Granularidade: semanal por município. Variáveis: diagnóstico, hospitalização, óbito, agente etiológico.', style={'fontSize':'13px','color':'#555'}),
        ]), md=6),
    ]),
])

tab_originais = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', style={'padding':'24px'}, children=[
        html.H2('✨ Visualizações Originais'),
        html.P('Análises inéditas desenvolvidas para a versão Python do GeoCalor, complementando o painel original com novas perspectivas analíticas.'),
    ]),
    chart_card('✨ Temperatura × Duração × Total de Dias OC (Bubble Chart)', [
        html.P('Cada bolha representa uma Região Metropolitana. O tamanho indica o total de dias de onda de calor (1981–2023). A cor identifica a macrorregião do Brasil. Permite comparar o perfil de risco climático de todas as RMs em um único gráfico.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-bubble', figure=fig_bubble_cidades(df_all), config={'displayModeBar': False}),
    ], 'purple'),
    html.Div(className='filter-bar', children=[
        dd('radar-cidades', [{'label': c, 'value': c} for c in CIDADES],
           ['Belém', 'Cuiabá', 'São Paulo', 'Curitiba', 'Fortaleza'],
           'Comparar Regiões Metropolitanas (até 6):', multi=True),
    ]),
    chart_card('✨ Perfil de Risco Climático por RM (Radar Chart)', [
        html.P('Comparação normalizada de 5 dimensões de risco: temperatura máxima, duração das OC, intensidade EHF, umidade e frequência anual. Quanto maior a área, maior o risco climático geral.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-radar', config={'displayModeBar': False}),
    ], 'dark'),
    chart_card('✨ Evolução da Composição de Intensidade ao Longo das Décadas', [
        html.P('Área empilhada mostrando como a proporção de dias de OC por intensidade (Low / Severe / Extreme) evoluiu de 1981 a 2023 em todas as RMs. O crescimento da área vermelha (Extreme) evidencia a intensificação das ondas de calor.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-stream2', figure=fig_streamgraph_intensidade(df_all), config={'displayModeBar': False}),
    ], 'orange'),
])

# ── LAYOUT PRINCIPAL ──────────────────────────────────────────────────────

app.layout = html.Div([
    dcc.Store(id='aba-ativa', data='inicio'),
    sidebar,
    html.Div(id='main-content', children=[
        header,
        html.Div(id='conteudo-aba'),
        footer,
    ]),
])

# ══════════════════════════════════════════════════════════════════════════
# CALLBACKS
# ══════════════════════════════════════════════════════════════════════════

@app.callback(
    Output('conteudo-aba', 'children'),
    Output('aba-ativa', 'data'),
    [Input(f'nav-{aba}', 'n_clicks') for aba, _, _ in ABAS],
    State('aba-ativa', 'data'),
    prevent_initial_call=False,
)
def trocar_aba(*args):
    from dash import ctx
    state = args[-1]
    trigger_id = ctx.triggered_id or f'nav-{state or "inicio"}'
    aba = state or 'inicio'
    if trigger_id and trigger_id.startswith('nav-'):
        aba = trigger_id.replace('nav-', '')

    tabs = {
        'inicio': tab_inicio, 'sobre': tab_sobre,
        'temperaturas': tab_temperaturas, 'ondas': tab_ondas,
        'extremos': tab_extremos, 'alertas': tab_alertas,
        'saude_mental': tab_saude_mental, 'internacoes': tab_internacoes,
        'srag': tab_srag, 'originais': tab_originais,
    }
    return tabs.get(aba, tab_inicio), aba


@app.callback(
    Output('graf-temp', 'figure'),
    Output('graf-umidade', 'figure'),
    Output('graf-ehf', 'figure'),
    Output('kpi-temp-row', 'children'),
    Output('graf-calendario', 'figure'),
    Output('graf-ridge', 'figure'),
    Input('temp-cidade', 'value'),
    Input('temp-ano', 'value'),
    Input('temp-vars', 'value'),
)
def update_temperaturas(cidade, ano, vars_sel):
    df = filter_df(cidade=cidade, ano=str(ano))
    show_max = 'max' in (vars_sel or [])
    show_med = 'med' in (vars_sel or [])
    show_min = 'min' in (vars_sel or [])

    f_temp  = fig_temperatura_diaria(df, cidade, ano, show_max, show_med, show_min)
    f_umid  = fig_umidade(df, cidade, ano)
    f_ehf   = fig_ehf(df, cidade, ano)
    f_cal   = fig_heatmap_calendario(df, cidade, ano)
    f_ridge = fig_ridge_mensal(filter_df(cidade=cidade), cidade)

    # KPIs dinâmicos
    kpi = kpi_cidade_ano(cidade, ano)
    kpi_row = [
        dbc.Col(kpi_box(kpi['dias_hw'], f'Dias de OC em {ano}', '🔥', 'kpi-brown'), md=2),
        dbc.Col(kpi_box(f"{kpi['temp_max']:.1f}°C", 'Temp. Máxima', '🌡️', 'kpi-orange'), md=2),
        dbc.Col(kpi_box(f"{kpi['temp_med']:.1f}°C", 'Temp. Média', '📊', 'kpi-teal'), md=2),
        dbc.Col(kpi_box(f"{kpi['umidade']:.0f}%", 'Umidade Média', '💧', 'kpi-green'), md=2),
        dbc.Col(kpi_box(kpi['n_eventos'], 'Nº de Ondas', '🌊', 'kpi-dark'), md=2),
        dbc.Col(kpi_box(f"{kpi['ehf_max']:.1f}", 'EHF Máximo', '⚡', 'kpi-brown'), md=2),
    ]
    return f_temp, f_umid, f_ehf, kpi_row, f_cal, f_ridge


@app.callback(
    Output('graf-polar', 'figure'),
    Output('graf-heatmap-hist', 'figure'),
    Output('graf-rank-temp', 'figure'),
    Output('graf-rank-dur', 'figure'),
    Output('graf-tendencia', 'figure'),
    Output('graf-anomalia', 'figure'),
    Input('hw-cidade', 'value'),
    Input('hw-ano', 'value'),
    Input('hw-heatmap-tipo', 'value'),
)
def update_ondas(cidade, ano, heatmap_tipo):
    freq   = polar_mensal(cidade)
    f_pol  = fig_polar_mensal(freq, cidade)
    piv    = heatmap_cidade_ano(heatmap_tipo)
    labels = {'dias_hw': 'Dias OC', 'temp_max': 'Temp. Máx (°C)', 'ehf_max': 'EHF Máx'}
    f_heat = fig_heatmap_historico(piv, labels.get(heatmap_tipo, 'Dias OC'))
    r_temp = ranking_cidades('temp_med')
    r_dur  = ranking_cidades('duracao')
    f_rt   = fig_ranking_barras(r_temp, 'Temperatura Média nas Ondas de Calor', ORANGE)
    f_rd   = fig_ranking_barras(r_dur,  'Duração Média das Ondas de Calor (dias)', TEAL)
    tend   = tendencia_anual(cidade)
    f_tend = fig_tendencia_anual(tend, cidade)
    anual, baseline = anomalia_termica(cidade)
    f_anom = fig_anomalia_termica(anual, cidade, baseline)
    return f_pol, f_heat, f_rt, f_rd, f_tend, f_anom


@app.callback(
    Output('ext-polar', 'figure'),
    Output('tabela-extremos', 'children'),
    Input('ext-cidade', 'value'),
    Input('ext-anos', 'value'),
    Input('ext-intensidade', 'value'),
)
def update_extremos(cidade, anos, intensidade):
    c = cidade if cidade != 'Todas' else 'Belém'
    freq  = polar_mensal(c)
    f_pol = fig_polar_mensal(freq, cidade)
    tbl   = eventos_extremos_tabela(cidade=cidade, ano_min=anos[0], ano_max=anos[1], intensidade=intensidade)
    tabela = dash_table.DataTable(
        data=tbl.to_dict('records'),
        columns=[{'name': c, 'id': c} for c in tbl.columns],
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': TEAL, 'color': 'white', 'fontWeight': 'bold', 'fontSize': '12px'},
        style_cell={'fontSize': '12px', 'padding': '6px 10px', 'textAlign': 'left'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}],
        export_format='csv',
        page_size=15,
        sort_action='native',
        filter_action='native',
    )
    return f_pol, tabela


@app.callback(
    Output('graf-sazonalidade', 'figure'),
    Input('alerta-cidade', 'value'),
)
def update_sazonalidade(cidade):
    saz = sazonalidade_decadal(cidade)
    return fig_sazonalidade_decadal(saz, cidade)


@app.callback(
    Output('graf-radar', 'figure'),
    Input('radar-cidades', 'value'),
)
def update_radar(cidades):
    if not cidades:
        cidades = ['Belém', 'Cuiabá', 'São Paulo']
    return fig_radar_cidade(df_all, cidades)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)
