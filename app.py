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
        html.Img(src='/assets/header_geocalor.png', style={'maxWidth':'100px','marginBottom':'6px'}),
        html.Br(),
        html.Img(src='/assets/header_ocs.png', style={'maxWidth':'100px','marginTop':'4px'}),
        html.P('Monitoramento de ondas de calor e impactos na saúde', style={'marginTop':'6px'}),
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
    html.Img(src='/assets/header_ocs.png', style={'height':'38px','background':'white','borderRadius':'6px','padding':'3px'}),
])

footer = html.Div(id='footer', children=[
    html.Div([
        html.Img(src='/assets/logo_pcdas.png', style={'height':'30px','marginRight':'12px','verticalAlign':'middle'}),
        html.Img(src='/assets/header_ocs.png', style={'height':'30px','marginRight':'12px','verticalAlign':'middle','background':'white','borderRadius':'4px','padding':'2px'}),
    ], style={'marginBottom':'8px'}),
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
            html.H5('Regiões Metropolitanas'),
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
        html.Div([
            html.Img(src='/assets/unb.png'),
            html.Img(src='/assets/cnpq.png'),
            html.Img(src='/assets/fiocruz.jpg'),
            html.Img(src='/assets/inmet.png'),
            html.Img(src='/assets/icea.png'),
            html.Img(src='/assets/observatorio.png'),
            html.Img(src='/assets/logo_pcdas.png'),
        ]),
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
        html.P([html.Strong('Construção do Painel: '), 'Bruno Porto e Hendesson Alves']),
        html.P([html.Strong('Desenvolvimento do Painel (versão Python — GeoCalor Dash): '), 'Diego Ricardo Xavier | OCS/ICICT/Fiocruz']),
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
    dbc.Row(id='kpi-temp-row', className='mb-3'),
    chart_card('✨ Calendário EHF — Visualização por Semana do Ano', [
        dcc.Graph(id='graf-calendario', config={'displayModeBar': False}),
    ], 'purple'),
    chart_card('✨ Distribuição Mensal de Temperatura Máxima (Ridge Plot)', [
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
    chart_card('✨ Anomalia de Temperatura Média Anual (estilo IPCC)', [
        dcc.Graph(id='graf-anomalia', config={'displayModeBar': False}),
    ], 'orange'),
])

tab_extremos = html.Div(className='page-wrapper', children=[
    chart_card('Mapa Interativo de Eventos Extremos nas Regiões Metropolitanas', [
        html.P('Visualização geoespacial das 15 Regiões Metropolitanas monitoradas pelo GeoCalor.', style={'padding':'8px 12px','fontSize':'13px','color':'#555'}),
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
                html.P('A tabela abaixo mostra os eventos de onda de calor identificados pelo índice EHF.', style={'fontSize':'12px','color':'#666'}),
                html.Div(id='tabela-extremos'),
            ]),
        ]), md=7),
    ]),
    chart_card('Distribuição de Intensidade das Ondas de Calor por Cidade', [
        dcc.Graph(id='graf-dist-intens', figure=fig_distribuicao_intensidade(distribuicao_intensidade()), config={'displayModeBar': False}),
    ], 'brown'),
])

tab_alertas = html.Div(className='page-wrapper', children=[
    html.Div(className='filter-bar', children=[
        dd('alerta-cidade', [{'label': c, 'value': c} for c in CIDADES], 'Belém', 'Região Metropolitana:'),
    ]),
    chart_card('Sazonalidade das Ondas de Calor por Década', [
        dcc.Graph(id='graf-sazonalidade', config={'displayModeBar': False}),
    ], 'teal'),
    chart_card('✨ Evolução Anual dos Dias de OC por Intensidade — Todas as RMs', [
        dcc.Graph(id='graf-stream', figure=fig_streamgraph_intensidade(df_all), config={'displayModeBar': False}),
    ], 'orange'),
])

tab_saude_mental = html.Div(className='page-wrapper', children=[
    html.Div(className='info-card', children=[
        html.H5('🧠 Saúde Mental (SIA) — Em desenvolvimento'),
        html.P('Esta seção apresentará a análise dos atendimentos ambulatoriais de saúde mental (SIA) em períodos de ondas de calor.'),
    ]),
])

tab_internacoes = html.Div(className='page-wrapper', children=[
    html.Div(className='info-card', children=[
        html.H5('🏥 Internações (SIH) — Em desenvolvimento'),
        html.P('Esta seção apresentará a análise das internações hospitalares (SIH) em períodos de ondas de calor.'),
    ]),
])

tab_srag = html.Div(className='page-wrapper', children=[
    html.Div(className='info-card', children=[
        html.H5('🫁 SRAG (Vigilância) — Em desenvolvimento'),
        html.P('Esta seção apresentará a análise dos casos de SRAG em períodos de ondas de calor.'),
    ]),
])

tab_originais = html.Div(className='page-wrapper', children=[
    html.Div(className='info-card', children=[
        html.H5('✨ Visualizações Originais'),
        html.P('Visualizações inéditas desenvolvidas para a versão Python do GeoCalor, complementando as análises do painel original com novas perspectivas analíticas.'),
    ]),
    chart_card('✨ Temperatura × Duração × Total de Dias OC (Bubble Chart)', [
        html.P('Cada bolha representa uma Região Metropolitana. O tamanho indica o total de dias de onda de calor. A cor identifica a macrorregião do Brasil.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-bubble', figure=fig_bubble_cidades(df_all), config={'displayModeBar': False}),
    ], 'purple'),
    html.Div(className='filter-bar', children=[
        dd('radar-cidades', [{'label': c, 'value': c} for c in CIDADES],
           ['Belém', 'Cuiabá', 'São Paulo', 'Curitiba', 'Fortaleza'],
           'Comparar Regiões Metropolitanas:', multi=True),
    ]),
    chart_card('✨ Perfil de Risco Climático por RM (Radar Chart)', [
        html.P('Comparação normalizada de 5 dimensões de risco: temperatura máxima, duração das OC, intensidade EHF, umidade e frequência anual.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-radar', config={'displayModeBar': False}),
    ], 'dark'),
    chart_card('✨ Evolução da Composição de Intensidade ao Longo das Décadas', [
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
    state = args[-1]
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]['value'] is None:
        aba = state or 'inicio'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        aba = trigger_id.replace('nav-', '')
    mapa_abas = {
        'inicio': tab_inicio, 'sobre': tab_sobre,
        'temperaturas': tab_temperaturas, 'ondas': tab_ondas,
        'extremos': tab_extremos, 'alertas': tab_alertas,
        'saude_mental': tab_saude_mental, 'internacoes': tab_internacoes,
        'srag': tab_srag, 'originais': tab_originais,
    }
    return mapa_abas.get(aba, tab_inicio), aba


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
    df  = filter_df(cidade=cidade, ano=str(ano))
    kpi = kpi_cidade_ano(cidade, int(ano))
    show_max = 'max' in (vars_sel or [])
    show_med = 'med' in (vars_sel or [])
    show_min = 'min' in (vars_sel or [])
    f_temp = fig_temperatura_diaria(df, cidade, ano, show_max, show_med, show_min)
    f_umid = fig_umidade(df, cidade, ano)
    f_ehf  = fig_ehf(df, cidade, ano)
    f_cal  = fig_heatmap_calendario(df, cidade, ano)
    f_ridg = fig_ridge_mensal(filter_df(cidade=cidade), cidade)
    kpi_row = dbc.Row([
        dbc.Col(kpi_box(kpi['dias_hw'], 'Dias de onda de calor', '🔥', 'kpi-orange'), md=3),
        dbc.Col(kpi_box(f"{kpi['temp_max']}°C", 'Temperatura máxima', '🌡️', 'kpi-teal'), md=3),
        dbc.Col(kpi_box(f"{kpi['temp_med']}°C", 'Temperatura média', '📊', 'kpi-green'), md=3),
        dbc.Col(kpi_box(f"{kpi['umidade']}%", 'Umidade média', '💧', 'kpi-brown'), md=3),
    ])
    return f_temp, f_umid, f_ehf, kpi_row, f_cal, f_ridg


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
        style_header={'backgroundColor': '#2b9eb3', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '12px'},
        style_cell={'fontSize': '12px', 'padding': '6px 10px'},
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
