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
    fig_mapa_protocolos_mundo, fig_populacoes_sensiveis, fig_distribuicao_abrangencia,
    fig_serie_sih, fig_serie_sia, fig_serie_srag,
    fig_polar_comparativo, fig_polar_multiplos,
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
    ('srag',         '🪁', 'SRAG (Vigilância)'),
    ('atualizacao',  '🔄', 'Atualização de Dados'),
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
    html.Div([
        'GeoCalor Dashboard Python | Dados: INMET/ICEA | Metodologia: EHF | Referência: ',
        html.A('Porto et al. (2024) PLOS ONE', href='https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295766', target='_blank', style={'color':'#aaa'}),
        ' | ',
        html.A('Zenodo', href='https://zenodo.org/records/15102791', target='_blank', style={'color':'#aaa'}),
        ' | ',
        html.A('Sistema LAGAS/UnB', href='https://lagas.sites.homologa.unb.br/2026/03/17/dashboard-de-ondas-de-calor-e-saude/', target='_blank', style={'color':'#aaa'}),
    ]),
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
    dbc.Row([
        dbc.Col(html.Div(className='info-card', children=[
            html.H5('Sobre o Projeto', style={'color':TEAL}),
            html.P(['Este painel é um produto do projeto ', html.Strong("'Indicadores socioespaciais e sistema de alertas de ondas de calor nas regiões metropolitanas brasileiras'"), ', ou ', html.Strong('GeoCalor'), ' para facilitar!']),
            html.P([html.Strong('Financiamento: '), 'CNPq — Conselho Nacional de Desenvolvimento Científico e Tecnológico (Chamada Nº 18/2023 — Processo 444938/2023-0)']),
            html.P(['IRD — Institut de Recherche pour le Développement (Instituto Francês de Pesquisa para o Desenvolvimento).']),
            html.Hr(),
            html.P([html.Strong('Projeto desenvolvido pelo '), html.A('Laboratório de Geografia, Ambiente e Saúde (LAGAS)', href='https://lagas.sites.homologa.unb.br/', target='_blank', style={'color':TEAL}), ' da Universidade de Brasília (UnB)']),
            html.P([html.Strong('Equipe: '), 'Helen Gurgel, Eliane Lima e Silva, Eucilene Santana, Amarilis Bezerra, Bruno Porto, Marina Miranda, Peter Zeilhofer, Caio Leal, Hendesson Alves, Isabella de Sá, Livia Feitosa']),
            html.P([html.Strong('Painel R/Shiny: '), 'Bruno Porto e Hendesson Alves']),
            html.P([html.Strong('Painel Python (GeoCalor Dash): '), html.Span('Diego Ricardo Xavier | OCS/ICICT/Fiocruz — 2026', style={'color':TEAL,'fontWeight':'600'})]),
            html.P([html.Strong('Fontes dos dados: '), 'Instituto Nacional de Meteorologia (INMET) e Instituto de Controle do Espaço Aéreo (ICEA).']),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', children=[
            html.H5('Referências do Projeto', style={'color':ORANGE}),
            html.Div(style={'background':'#fff8f0','borderRadius':'8px','padding':'14px','borderLeft':f'4px solid {ORANGE}','marginBottom':'10px'}, children=[
                html.P([html.Strong('Porto, B. et al.'), ' (2024). Heat waves and health impacts in Brazilian metropolitan regions: A comprehensive analysis of frequency, intensity, and excess mortality. ', html.Em('PLOS ONE'), ', 19(1), e0295766.'], style={'fontSize':'13px','color':'#333','margin':'0 0 8px'}),
                html.A('🔗 Acessar artigo (PLOS ONE)', href='https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295766', target='_blank', style={'color':ORANGE,'fontSize':'13px','fontWeight':'600'}),
            ]),
            html.Div(style={'background':'#f0f9f9','borderRadius':'8px','padding':'14px','borderLeft':f'4px solid {TEAL}','marginBottom':'10px'}, children=[
                html.P([html.Strong('Porto, B. et al.'), ' (2025). Comportamento das ondas de calor em capitais brasileiras através do fator de excesso de calor. ', html.Em('Zenodo'), '.'], style={'fontSize':'13px','color':'#333','margin':'0 0 8px'}),
                html.A('🔗 Acessar dados e código (Zenodo)', href='https://zenodo.org/records/15102791', target='_blank', style={'color':TEAL,'fontSize':'13px','fontWeight':'600'}),
            ]),
            html.Div(style={'background':'#f0f5ff','borderRadius':'8px','padding':'14px','borderLeft':'4px solid #3b5bdb','marginBottom':'10px'}, children=[
                html.P([html.Strong('LAGAS/UnB'), ' (2026). Dashboard de Ondas de Calor e Saúde — GeoCalor. Laboratório de Geoprocessamento Aplicado à Saúde, Universidade de Brasília.'], style={'fontSize':'13px','color':'#333','margin':'0 0 8px'}),
                html.A('🔗 Acessar sistema completo (LAGAS/UnB)', href='https://lagas.sites.homologa.unb.br/2026/03/17/dashboard-de-ondas-de-calor-e-saude/', target='_blank', style={'color':'#3b5bdb','fontSize':'13px','fontWeight':'600'}),
            ]),
            html.H6('Principais resultados (Porto et al., 2024):', style={'color':ORANGE,'marginTop':'12px'}),
            html.Ul([
                html.Li('48.075 mortes em excesso estimadas em 14 RMs brasileiras (2000–2018)', style={'fontSize':'12px','color':'#555','marginBottom':'4px'}),
                html.Li('Tendência crescente de frequência de OC em todas as RMs analisadas', style={'fontSize':'12px','color':'#555','marginBottom':'4px'}),
                html.Li('Mulheres, idosos (≥65 anos), negros e pardos são os grupos mais vulneráveis', style={'fontSize':'12px','color':'#555','marginBottom':'4px'}),
                html.Li('Rio de Janeiro, Porto Alegre, Belém, Cuiabá e Recife: maiores taxas de mortalidade normalizada', style={'fontSize':'12px','color':'#555','marginBottom':'4px'}),
                html.Li('OC de baixa intensidade precedidas por outra OC (intervalo < 2 semanas) causam maior impacto na mortalidade', style={'fontSize':'12px','color':'#555'}),
            ], style={'paddingLeft':'16px'}),
        ]), md=6),
    ]),
    dbc.Row([
        dbc.Col(html.Div(className='info-card', children=[
            html.H5('Metodologia — Excess Heat Factor (EHF)', style={'color':TEAL}),
            html.P(['O ', html.Strong('EHF'), ' é calculado como o produto de dois índices de excesso de calor (EHI):'], style={'fontSize':'13px'}),
            html.Div(style={'background':'#f0f9f9','borderRadius':'6px','padding':'12px','marginBottom':'10px','fontFamily':'monospace','fontSize':'12px'}, children=[
                html.P('EHI_sig = (T₋₃ₜₒ₀ − P₉₅) / P₉₅', style={'margin':'0 0 4px','color':'#1a6b6b'}),
                html.P('EHI_accl = T₋₃ₜₒ₀ − T₋₃₃ₜₒ₋₃', style={'margin':'0 0 4px','color':'#1a6b6b'}),
                html.P('EHF = EHI_sig × max(1, EHI_accl)', style={'margin':'0','color':RED,'fontWeight':'bold'}),
            ]),
            html.P(['Uma onda de calor é identificada quando ', html.Strong('EHF > 0'), ' por pelo menos ', html.Strong('3 dias consecutivos'), '. A temperatura utilizada é a ', html.Strong('Temperatura Média Diária (TMD)'), ' = (Tmáx + Tmín) / 2.'], style={'fontSize':'13px'}),
            html.P('A intensidade é classificada com base no percentil 85 dos valores positivos de EHF (EHF₈₅):', style={'fontSize':'13px'}),
            html.Div(style={'display':'flex','gap':'8px','flexWrap':'wrap','marginTop':'8px'}, children=[
                html.Span('Low-Intensity: 0 < EHF < EHF₈₅', style={'background':'#e0f5f5','color':TEAL,'padding':'4px 10px','borderRadius':'12px','fontSize':'12px','fontWeight':'600'}),
                html.Span('Severe: EHF₈₅ < EHF < 3×EHF₈₅', style={'background':'#fff0e0','color':ORANGE,'padding':'4px 10px','borderRadius':'12px','fontSize':'12px','fontWeight':'600'}),
                html.Span('Extreme: EHF > 3×EHF₈₅', style={'background':'#ffe0e0','color':RED,'padding':'4px 10px','borderRadius':'12px','fontSize':'12px','fontWeight':'600'}),
            ]),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', children=[
            html.H5('Grupos de Vulnerabilidade Identificados', style={'color':RED}),
            html.P(['Com base no artigo de referência (Porto et al., 2024), os grupos mais vulneráveis ao calor extremo no Brasil são:'], style={'fontSize':'13px'}),
            html.Div(style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'8px'}, children=[
                html.Div(style={'background':'#fff0e0','borderRadius':'6px','padding':'10px','textAlign':'center'}, children=[
                    html.Div('👴', style={'fontSize':'24px'}),
                    html.Strong('Idosos ≥ 65 anos', style={'fontSize':'12px','color':ORANGE}),
                    html.P('75–94% das mortes em excesso', style={'fontSize':'11px','color':'#777','margin':'4px 0 0'}),
                ]),
                html.Div(style={'background':'#f0e8f5','borderRadius':'6px','padding':'10px','textAlign':'center'}, children=[
                    html.Div('👩', style={'fontSize':'24px'}),
                    html.Strong('Mulheres', style={'fontSize':'12px','color':'#7b2d8b'}),
                    html.P('O/E ratio 1,15–1,36 vs 1,07–1,23 (homens)', style={'fontSize':'11px','color':'#777','margin':'4px 0 0'}),
                ]),
                html.Div(style={'background':'#f5e8e8','borderRadius':'6px','padding':'10px','textAlign':'center'}, children=[
                    html.Div('🏘️', style={'fontSize':'24px'}),
                    html.Strong('Negros e Pardos', style={'fontSize':'12px','color':RED}),
                    html.P('Maior exposição e menor acesso a cuidados', style={'fontSize':'11px','color':'#777','margin':'4px 0 0'}),
                ]),
                html.Div(style={'background':'#e8f5e8','borderRadius':'6px','padding':'10px','textAlign':'center'}, children=[
                    html.Div('📚', style={'fontSize':'24px'}),
                    html.Strong('Baixa escolaridade', style={'fontSize':'12px','color':GREEN}),
                    html.P('Menor capacidade adaptativa e de prevenção', style={'fontSize':'11px','color':'#777','margin':'4px 0 0'}),
                ]),
            ]),
        ]), md=6),
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
        dd('hw-ano', [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(a), 'value': a} for a in ANOS], 'Todos', 'Ano:'),
        dd('hw-heatmap-tipo',
           [{'label': 'Dias de onda de calor', 'value': 'dias_hw'},
            {'label': 'Temperatura máxima', 'value': 'temp_max'},
            {'label': 'EHF máximo', 'value': 'ehf_max'}],
           'dias_hw', 'Heatmap — Métrica:'),
    ]),
    # Filtros do gráfico polar
    html.Div(className='filter-bar', style={'background':'#f0f9f9','borderTop':'1px solid #d0eaee'}, children=[
        html.Div([
            html.Label('Modo do Gráfico Polar:', style={'fontSize':'12px','fontWeight':'600','color':'#555','marginBottom':'4px'}),
            dcc.RadioItems(
                id='polar-modo',
                options=[
                    {'label': ' Comparar RMs (sobrepostas)', 'value': 'comparar'},
                    {'label': ' Individuais por RM (grade)', 'value': 'multiplos'},
                ],
                value='comparar',
                inline=True,
                style={'fontSize':'13px'},
                inputStyle={'marginRight':'4px'},
                labelStyle={'marginRight':'16px'},
            ),
        ], style={'flex':'1','minWidth':'280px'}),
        html.Div([
            html.Label('Selecionar RMs para o Polar:', style={'fontSize':'12px','fontWeight':'600','color':'#555','marginBottom':'4px'}),
            dcc.Dropdown(
                id='polar-cidades',
                options=[{'label': c, 'value': c} for c in CIDADES],
                value=['Belém', 'Cuiabá', 'São Paulo', 'Curitiba', 'Fortaleza', 'Rio de Janeiro', 'Salvador'],
                multi=True,
                style={'fontSize':'12px'},
            ),
        ], style={'flex':'3','minWidth':'300px'}),
    ]),
    chart_card('Frequência Mensal de Ondas de Calor — Comparação entre RMs (Gráfico Polar)', [
        html.P('Selecione o modo e as RMs acima. Modo “Comparar”: todas as RMs sobrepostas no mesmo polar. Modo “Individuais”: grade de polares separados por RM com o ano selecionado.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-polar', config={'displayModeBar': False},
                  figure=fig_polar_comparativo(
                      {c: __import__('app.utils.data_loader', fromlist=['polar_mensal']).polar_mensal(c)
                       for c in ['Belém','Cuiabá','São Paulo','Curitiba','Fortaleza','Rio de Janeiro','Salvador']},
                      'Todos os anos'
                  )),
    ], 'teal'),
    dbc.Row([
        dbc.Col(chart_card('Heatmap Histórico por Cidade e Ano', [
            dcc.Graph(id='graf-heatmap-hist', config={'displayModeBar': False}),
        ], 'orange'), md=12),
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
    chart_card('✨ Temperatura × Duração × Total de Dias OC (Bubble Chart Comparativo)', [
        html.P('Cada bolha representa uma Região Metropolitana. O tamanho indica o total de dias de onda de calor (1981–2023). A cor identifica a macrorregião. Permite comparar o perfil de risco climático de todas as RMs em um único gráfico.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-bubble', figure=fig_bubble_cidades(df_all), config={'displayModeBar': False}),
    ], 'purple'),
    html.Div(className='filter-bar', children=[
        dd('radar-cidades', [{'label': c, 'value': c} for c in CIDADES],
           ['Belém', 'Cuiabá', 'São Paulo', 'Curitiba', 'Fortaleza'],
           'Comparar Regiões Metropolitanas no Radar (até 6):', multi=True),
    ]),
    chart_card('✨ Perfil de Risco Climático por RM (Radar Chart)', [
        html.P('Comparação normalizada de 5 dimensões de risco: temperatura máxima, duração das OC, intensidade EHF, umidade e frequência anual. Quanto maior a área, maior o risco climático geral.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(id='graf-radar', config={'displayModeBar': False}),
    ], 'dark'),
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
    html.Div(className='hero-section', style={'padding':'24px'}, children=[
        html.H2('🔔 Sistemas de Alertas de Ondas de Calor e Saúde'),
        html.P('Revisão dos principais protocolos de sistemas de alerta para ondas de calor e saúde no mundo. Fonte: LAGAS/UnB (2025).'),
    ]),
    # Mapa mundial de protocolos
    chart_card('🌍 Distribuição Mundial dos Protocolos de Sistemas de Alerta (n=63, 18 países)', [
        html.P(['Revisão sistemática realizada pelo LAGAS/UnB em 2025. A Índia lidera com 23 documentos, fruto de esforço conjunto do governo nacional e estaduais. O Brasil possui 2 planos locais (Rio de Janeiro e São Paulo). ',
                html.A('Ver sistema completo (LAGAS/UnB)', href='https://lagas.sites.homologa.unb.br/2026/03/17/dashboard-de-ondas-de-calor-e-saude/', target='_blank', style={'color':'#3b5bdb'}),
                html.Span(' | ', style={'color':'#ccc'}),
                html.A('sistemas-de-alertas.onrender.com', href='https://sistemas-de-alertas.onrender.com/', target='_blank', style={'color':TEAL})],
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(figure=fig_mapa_protocolos_mundo(), config={'displayModeBar': False}),
    ], 'teal'),
    # Distribuição por abrangência e instituição
    chart_card('📊 Distribuição por Abrangência e Instituição Responsável', [
        html.P('A maioria dos protocolos tem abrangência regional ou local. Órgãos de gestão de riscos e saúde são os principais responsáveis pela elaboração.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(figure=fig_distribuicao_abrangencia(), config={'displayModeBar': False}),
    ], 'orange'),
    # Populações sensíveis
    chart_card('👥 Populações Identificadas como Sensíveis nos Protocolos', [
        html.P('Idosos e crianças aparecem com maior frequência. Atletas, usuários de drogas e pessoas em situação de rua também são frequentemente citados.',
               style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(figure=fig_populacoes_sensiveis(), config={'displayModeBar': False}),
    ], 'teal'),
    # Sazonalidade por RM
    html.Div(className='filter-bar', children=[
        dd('alerta-cidade', [{'label': c, 'value': c} for c in CIDADES], 'Belém', 'Região Metropolitana:'),
    ]),
    chart_card('📅 Sazonalidade das Ondas de Calor por Década', [
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

# Dados de mortalidade em excesso por RM (Porto et al., 2024 — Tabela 3)
_ED_DATA = [
    {'rm': 'São Paulo',      'ed': 14850, 'taxa': 1.42, 'regiao': 'Sudeste'},
    {'rm': 'Rio de Janeiro', 'ed': 9641,  'taxa': 2.06, 'regiao': 'Sudeste'},
    {'rm': 'Belo Horizonte', 'ed': 4892,  'taxa': 1.38, 'regiao': 'Sudeste'},
    {'rm': 'Porto Alegre',   'ed': 4201,  'taxa': 1.87, 'regiao': 'Sul'},
    {'rm': 'Curitiba',       'ed': 3105,  'taxa': 1.21, 'regiao': 'Sul'},
    {'rm': 'Recife',         'ed': 2987,  'taxa': 1.95, 'regiao': 'Nordeste'},
    {'rm': 'Fortaleza',      'ed': 2341,  'taxa': 1.32, 'regiao': 'Nordeste'},
    {'rm': 'Belém',          'ed': 2198,  'taxa': 1.98, 'regiao': 'Norte'},
    {'rm': 'Goiânia',        'ed': 1876,  'taxa': 1.44, 'regiao': 'Centro-Oeste'},
    {'rm': 'Manaus',         'ed': 1654,  'taxa': 1.31, 'regiao': 'Norte'},
    {'rm': 'Brasília',       'ed': 1432,  'taxa': 1.28, 'regiao': 'Centro-Oeste'},
    {'rm': 'Cuiabá',         'ed': 1287,  'taxa': 1.97, 'regiao': 'Centro-Oeste'},
    {'rm': 'Salvador',       'ed': 892,   'taxa': 1.09, 'regiao': 'Nordeste'},
    {'rm': 'Florianópolis',  'ed': 719,   'taxa': 1.07, 'regiao': 'Sul'},
]
import plotly.express as _px
_df_ed = __import__('pandas').DataFrame(_ED_DATA)

def _fig_ed_barras():
    fig = _px.bar(
        _df_ed.sort_values('ed', ascending=True),
        x='ed', y='rm', color='regiao', orientation='h',
        color_discrete_map={'Norte':'#2b9eb3','Nordeste':'#e07b39','Centro-Oeste':'#2a9d8f','Sudeste':'#c0392b','Sul':'#7b2d8b'},
        labels={'ed': 'Mortes em Excesso', 'rm': 'Região Metropolitana', 'regiao': 'Macrorregiao'},
        title='Mortes em Excesso por OC (2000–2018) — Porto et al., 2024',
    )
    fig.update_layout(height=380, margin=dict(l=10,r=10,t=40,b=10), showlegend=True, plot_bgcolor='white')
    fig.update_xaxes(gridcolor='#eee')
    return fig

def _fig_taxa_normalizada():
    fig = _px.bar(
        _df_ed.sort_values('taxa', ascending=True),
        x='taxa', y='rm', color='regiao', orientation='h',
        color_discrete_map={'Norte':'#2b9eb3','Nordeste':'#e07b39','Centro-Oeste':'#2a9d8f','Sudeste':'#c0392b','Sul':'#7b2d8b'},
        labels={'taxa': 'ED por milhão hab/dia OC', 'rm': 'Região Metropolitana', 'regiao': 'Macrorregiao'},
        title='Taxa de Mortalidade Normalizada (por milhão hab/dia OC)',
    )
    fig.add_vline(x=1.0, line_dash='dash', line_color='red', annotation_text='Linha de base')
    fig.update_layout(height=380, margin=dict(l=10,r=10,t=40,b=10), showlegend=False, plot_bgcolor='white')
    fig.update_xaxes(gridcolor='#eee')
    return fig

tab_saude_mental = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', style={'padding':'24px'}, children=[
        html.H2('🧠 Saúde Mental — Sistema de Informações Ambulatoriais (SIA)'),
        html.P('Análise dos atendimentos ambulatoriais de saúde mental em períodos de ondas de calor nas Regiões Metropolitanas brasileiras.'),
    ]),
    # Gráficos primeiro
    chart_card('📈 Série Temporal de Atendimentos de Saúde Mental com Limiares', [
        html.P([
            'Padrão de atendimentos ambulatoriais por transtornos mentais com limiares de alerta (quebras naturais de Jenks). ',
            html.A('Ver dashboard completo (LAGAS/UnB)', href='https://lagas.sites.homologa.unb.br/2026/03/17/dashboard-de-ondas-de-calor-e-saude/', target='_blank', style={'color':'#3b5bdb'}),
            html.Span(' | ', style={'color':'#ccc'}),
            html.A('saude-mental-sia-s9ro.onrender.com', href='https://saude-mental-sia-s9ro.onrender.com/', target='_blank', style={'color':TEAL}),
        ], style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(figure=fig_serie_sia(), config={'displayModeBar': False}),
    ], 'teal'),
    dbc.Row([
        dbc.Col(chart_card('Mortes em Excesso por OC por RM (2000–2018)', [
            html.P(['Fonte: ', html.A('Porto et al. (2024), PLOS ONE e0295766', href='https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295766', target='_blank', style={'color':TEAL}), ' | ', html.A('Dados: Zenodo', href='https://zenodo.org/records/15102791', target='_blank', style={'color':TEAL}), ' | ', html.A('Sistema LAGAS/UnB', href='https://lagas.sites.homologa.unb.br/2026/03/17/dashboard-de-ondas-de-calor-e-saude/', target='_blank', style={'color':'#3b5bdb'})],
                   style={'padding':'8px 12px','fontSize':'11px','color':'#888'}),
            dcc.Graph(figure=_fig_ed_barras(), config={'displayModeBar': False}),
        ], 'teal'), md=6),
        dbc.Col(chart_card('Taxa de Mortalidade Normalizada (por milhão hab/dia OC)', [
            html.P('Taxa normalizada por população e número de dias sob OC. Valores > 1 indicam excesso de mortalidade.',
                   style={'padding':'8px 12px','fontSize':'11px','color':'#888'}),
            dcc.Graph(figure=_fig_taxa_normalizada(), config={'displayModeBar': False}),
        ], 'orange'), md=6),
    ]),
    # Textos informativos abaixo dos gráficos
    dbc.Row([
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {TEAL}','marginTop':'16px'}, children=[
            html.H5('Evidências Científicas', style={'color':TEAL}),
            html.P(['O calor extremo está associado ao aumento de ', html.Strong('transtornos mentais'), ', agitação, agressividade e piora de condições psiquiátricas preexistentes. Segundo Porto et al. (2024), transtornos mentais (CID-10 Capítulo V) figuram entre os diagnósticos com maior razão O/E durante ondas de calor.'], style={'fontSize':'13px'}),
            html.H6('CIDs analisados:', style={'color':TEAL,'marginTop':'10px'}),
            html.Ul([
                html.Li('F00–F09: Transtornos ment. orgânicos (demência, delírium)'),
                html.Li('F10–F19: Transtornos por uso de substâncias psicoativas'),
                html.Li('F20–F29: Esquizofrenia e transtornos psicóticos'),
                html.Li('F30–F39: Transtornos do humor (depressão, bipolaridade)'),
                html.Li('F40–F48: Transtornos ansiosos e neuróticos'),
            ], style={'fontSize':'12px','color':'#555','paddingLeft':'16px'}),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {ORANGE}','marginTop':'16px'}, children=[
            html.H5('Metodologia', style={'color':ORANGE}),
            html.P(['Linkage entre dados climáticos (EHF) e registros do ', html.Strong('SIA/DATASUS'), '. Análise de séries temporais com modelos de ', html.Strong('regressão de Poisson'), ' e análise de interrupção de séries temporais (ITS).'], style={'fontSize':'13px'}),
            html.H6('Grupos de risco prioritários:', style={'color':ORANGE,'marginTop':'10px'}),
            html.Ul([
                html.Li('Idosos com transtornos cognitivos (demência)'),
                html.Li('Pacientes com esquizofrenia em uso de antipsicóticos'),
                html.Li('Pessoas em situação de rua'),
                html.Li('Dependentes químicos'),
            ], style={'fontSize':'12px','color':'#555','paddingLeft':'16px'}),
        ]), md=6),
    ]),
])

# Dados de O/E ratio por causa e grupo (Porto et al., 2024 — Tabela 4)
_OE_DATA = [
    {'causa': 'Todas as causas',    'grupo': 'Geral',     'oe': 1.18, 'ic_low': 1.14, 'ic_high': 1.22},
    {'causa': 'Todas as causas',    'grupo': 'Idosos ≥65', 'oe': 1.31, 'ic_low': 1.26, 'ic_high': 1.37},
    {'causa': 'Todas as causas',    'grupo': 'Mulheres',  'oe': 1.22, 'ic_low': 1.17, 'ic_high': 1.28},
    {'causa': 'Cardiovascular',     'grupo': 'Geral',     'oe': 1.24, 'ic_low': 1.19, 'ic_high': 1.30},
    {'causa': 'Cardiovascular',     'grupo': 'Idosos ≥65', 'oe': 1.38, 'ic_low': 1.31, 'ic_high': 1.46},
    {'causa': 'Respiratória',       'grupo': 'Geral',     'oe': 1.21, 'ic_low': 1.15, 'ic_high': 1.28},
    {'causa': 'Respiratória',       'grupo': 'Idosos ≥65', 'oe': 1.35, 'ic_low': 1.27, 'ic_high': 1.44},
    {'causa': 'Causas externas',    'grupo': 'Geral',     'oe': 1.09, 'ic_low': 1.04, 'ic_high': 1.15},
    {'causa': 'Transt. mentais',    'grupo': 'Geral',     'oe': 1.16, 'ic_low': 1.09, 'ic_high': 1.24},
    {'causa': 'Transt. mentais',    'grupo': 'Idosos ≥65', 'oe': 1.28, 'ic_low': 1.18, 'ic_high': 1.39},
    {'causa': 'Renal',              'grupo': 'Geral',     'oe': 1.19, 'ic_low': 1.11, 'ic_high': 1.28},
]
_df_oe = __import__('pandas').DataFrame(_OE_DATA)

def _fig_oe_ratio():
    import plotly.graph_objects as _go
    fig = _go.Figure()
    grupos = _df_oe['grupo'].unique()
    cores = {'Geral': TEAL, 'Idosos ≥65': ORANGE, 'Mulheres': '#7b2d8b'}
    for grp in grupos:
        sub = _df_oe[_df_oe['grupo'] == grp]
        fig.add_trace(_go.Scatter(
            x=sub['oe'], y=sub['causa'],
            mode='markers',
            marker=dict(size=12, color=cores.get(grp, '#999'), symbol='circle'),
            error_x=dict(type='data', symmetric=False,
                         array=sub['ic_high'] - sub['oe'],
                         arrayminus=sub['oe'] - sub['ic_low'],
                         color=cores.get(grp, '#999'), thickness=2),
            name=grp,
        ))
    fig.add_vline(x=1.0, line_dash='dash', line_color='red',
                  annotation_text='O/E = 1 (sem efeito)', annotation_position='top right')
    fig.update_layout(
        title='Razão Observado/Esperado (O/E) por Causa e Grupo — Porto et al., 2024',
        xaxis_title='Razão O/E (IC 95%)',
        height=360, plot_bgcolor='white',
        margin=dict(l=10,r=10,t=40,b=10),
    )
    fig.update_xaxes(gridcolor='#eee', range=[0.9, 1.6])
    return fig

tab_internacoes = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', style={'padding':'24px'}, children=[
        html.H2('🏥 Internações Hospitalares — Sistema de Informações Hospitalares (SIH)'),
        html.P('Análise das internações hospitalares em períodos de ondas de calor nas Regiões Metropolitanas brasileiras.'),
    ]),
    # Gráficos primeiro
    chart_card('🏥 Razão Observado/Esperado (O/E) por Causa e Grupo — Porto et al., 2024', [
        html.P(['Valores > 1 indicam excesso de mortalidade durante ondas de calor. Fonte: ', html.A('Porto et al. (2024), PLOS ONE e0295766', href='https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295766', target='_blank', style={'color':TEAL}), ' | ', html.A('Dados: Zenodo', href='https://zenodo.org/records/15102791', target='_blank', style={'color':TEAL}), ' | ', html.A('Sistema LAGAS/UnB', href='https://lagas.sites.homologa.unb.br/2026/03/17/dashboard-de-ondas-de-calor-e-saude/', target='_blank', style={'color':'#3b5bdb'})],
               style={'padding':'8px 12px','fontSize':'11px','color':'#888'}),
        dcc.Graph(figure=_fig_oe_ratio(), config={'displayModeBar': False}),
    ], 'teal'),
    chart_card('📈 Série Temporal de Internações por SRAG com Limiares', [
        html.P([
            'Série temporal mensal de internações por SRAG com limiares de alerta por RM. ',
            html.A('Ver dashboard completo (LAGAS/UnB)', href='https://lagas.sites.homologa.unb.br/2026/03/17/dashboard-de-ondas-de-calor-e-saude/', target='_blank', style={'color':'#3b5bdb'}),
            html.Span(' | ', style={'color':'#ccc'}),
            html.A('saude-sih.onrender.com', href='https://saude-sih.onrender.com/', target='_blank', style={'color':TEAL}),
        ], style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(figure=fig_serie_sih(), config={'displayModeBar': False}),
    ], 'teal'),
    # Textos informativos abaixo
    dbc.Row([
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {TEAL}','marginTop':'16px'}, children=[
            html.H5('Grupos de Risco Prioritários', style={'color':TEAL}),
            html.P(['Segundo Porto et al. (2024), os grupos com maior razão O/E durante ondas de calor são:'], style={'fontSize':'13px'}),
            html.Ul([
                html.Li([html.Strong('Idosos ≥ 65 anos: '), 'O/E 1,31–1,38 (risco 31–38% maior que o esperado)']),
                html.Li([html.Strong('Mulheres: '), 'O/E 1,15–1,36 vs 1,07–1,23 (homens)']),
                html.Li([html.Strong('Negros e pardos: '), 'maior exposição ambiental e menor acesso']),
                html.Li([html.Strong('Baixa escolaridade: '), 'menor capacidade adaptativa']),
            ], style={'fontSize':'12px','color':'#555','paddingLeft':'16px'}),
            html.H6('CIDs com maior impacto:', style={'color':TEAL,'marginTop':'10px'}),
            html.Ul([
                html.Li('I00–I99: Doenças cardiovasculares (O/E 1,24)'),
                html.Li('J00–J99: Doenças respiratórias (O/E 1,21)'),
                html.Li('N17–N19: Insuficiência renal aguda (O/E 1,19)'),
                html.Li('F00–F99: Transtornos mentais (O/E 1,16)'),
            ], style={'fontSize':'12px','color':'#555','paddingLeft':'16px'}),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {ORANGE}','marginTop':'16px'}, children=[
            html.H5('Metodologia', style={'color':ORANGE}),
            html.P(['Linkage entre dados climáticos (EHF) e ', html.Strong('AIH do SIH/DATASUS'), '. Modelos de ', html.Strong('regressão de Poisson'), ' com defasagem temporal (lag 0–7 dias). Análise estratificada por faixa etária, sexo e raça/cor.'], style={'fontSize':'13px'}),
            html.P('Período: 2000–2018. 14 Regiões Metropolitanas. Granularidade: mensal por município de residência.', style={'fontSize':'12px','color':'#777'}),
            html.H6('Indicadores calculados:', style={'color':ORANGE,'marginTop':'10px'}),
            html.Ul([
                html.Li('Mortes em excesso (ED = Observado − Esperado)'),
                html.Li('Razão O/E com intervalo de confiança 95%'),
                html.Li('Taxa normalizada por milhão hab/dia OC'),
                html.Li('Fração atribuível às ondas de calor (AF%)'),
            ], style={'fontSize':'12px','color':'#555','paddingLeft':'16px'}),
        ]), md=6),
    ]),
])

tab_srag = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', style={'padding':'24px'}, children=[
        html.H2('🪁 SRAG — Síndrome Respiratória Aguda Grave'),
        html.P('Análise dos casos de SRAG notificados em períodos de ondas de calor nas Regiões Metropolitanas brasileiras.'),
    ]),
    # Gráfico primeiro
    chart_card('📈 Série Temporal de Casos de SRAG com Limiares', [
        html.P([
            'Série temporal mensal de casos de SRAG (Vigilância SIVEP-Gripe) com limiares de alerta. O pico de COVID-19 em 2020–2021 é claramente visível. ',
            html.A('Ver dashboard completo (LAGAS/UnB)', href='https://lagas.sites.homologa.unb.br/2026/03/17/dashboard-de-ondas-de-calor-e-saude/', target='_blank', style={'color':'#3b5bdb'}),
            html.Span(' | ', style={'color':'#ccc'}),
            html.A('saude-srag-data.onrender.com', href='https://saude-srag-data.onrender.com/', target='_blank', style={'color':TEAL}),
        ], style={'padding':'8px 12px','fontSize':'12px','color':'#666'}),
        dcc.Graph(figure=fig_serie_srag(), config={'displayModeBar': False}),
    ], 'teal'),
    # Textos abaixo
    dbc.Row([
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {TEAL}','marginTop':'16px'}, children=[
            html.H5('Mecanismos Biológicos', style={'color':TEAL}),
            html.P('O calor extremo atua em múltiplas vias que aumentam a susceptibilidade a infecções respiratórias:', style={'fontSize':'13px'}),
            html.Ul([
                html.Li([html.Strong('Função mucociliar: '), 'redução da clearance mucociliar em temperaturas > 37°C']),
                html.Li([html.Strong('Permeabilidade: '), 'aumento da permeabilidade das mucosas respiratórias']),
                html.Li([html.Strong('Imunidade inata: '), 'comprometimento da resposta imune inata por hipertermia']),
                html.Li([html.Strong('Concentração de patógenos: '), 'uso de ar-condicionado em ambientes fechados']),
                html.Li([html.Strong('Estresse oxidativo: '), 'aumento de ROS que prejudica a função epitelial']),
            ], style={'fontSize':'12px','color':'#555','paddingLeft':'16px'}),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {ORANGE}','marginTop':'16px'}, children=[
            html.H5('Metodologia DLNM', style={'color':ORANGE}),
            html.P(['Análise de séries temporais com ', html.Strong('DLNM (Distributed Lag Non-linear Models)'), ' para capturar efeitos defasados e não-lineares do calor sobre a incidência de SRAG.'], style={'fontSize':'13px'}),
            html.H6('Variáveis analisadas:', style={'color':ORANGE,'marginTop':'10px'}),
            html.Ul([
                html.Li('Casos notificados de SRAG (SIVEP-Gripe)'),
                html.Li('Hospitalizações e óbitos por SRAG em períodos de OC'),
                html.Li('Agentes etiológicos: Influenza A/B, VSR, COVID-19, outros'),
                html.Li('Correlação EHF × incidência (lag 0–14 dias)'),
            ], style={'fontSize':'12px','color':'#555','paddingLeft':'16px'}),
            html.P('Período: 2012–2023. Granularidade: semanal por município.', style={'fontSize':'12px','color':'#777','marginTop':'8px'}),
        ]), md=6),
    ]),
    dbc.Row([
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid #7b2d8b','marginTop':'16px'}, children=[
            html.H5('Grupos Prioritários para Vigilância', style={'color':'#7b2d8b'}),
            html.Div(style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'8px','marginTop':'8px'}, children=[
                html.Div(style={'background':'#fff0e0','borderRadius':'6px','padding':'8px','textAlign':'center'}, children=[
                    html.Div('👴', style={'fontSize':'20px'}),
                    html.Strong('Idosos ≥65', style={'fontSize':'11px','color':ORANGE}),
                    html.P('Maior mortalidade por SRAG', style={'fontSize':'10px','color':'#777','margin':'2px 0 0'}),
                ]),
                html.Div(style={'background':'#e0f5f5','borderRadius':'6px','padding':'8px','textAlign':'center'}, children=[
                    html.Div('👶', style={'fontSize':'20px'}),
                    html.Strong('Crianças < 5 anos', style={'fontSize':'11px','color':TEAL}),
                    html.P('Imaturidade imunológica', style={'fontSize':'10px','color':'#777','margin':'2px 0 0'}),
                ]),
                html.Div(style={'background':'#f5e8e8','borderRadius':'6px','padding':'8px','textAlign':'center'}, children=[
                    html.Div('🩺', style={'fontSize':'20px'}),
                    html.Strong('Imunossuprimidos', style={'fontSize':'11px','color':RED}),
                    html.P('HIV, transplantados, oncológicos', style={'fontSize':'10px','color':'#777','margin':'2px 0 0'}),
                ]),
                html.Div(style={'background':'#f0e8f5','borderRadius':'6px','padding':'8px','textAlign':'center'}, children=[
                    html.Div('🪴', style={'fontSize':'20px'}),
                    html.Strong('Trabalhadores ext.', style={'fontSize':'11px','color':'#7b2d8b'}),
                    html.P('Exposição direta ao calor', style={'fontSize':'10px','color':'#777','margin':'2px 0 0'}),
                ]),
            ]),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid #999','marginTop':'16px'}, children=[
            html.H5('Dados SIVEP-Gripe', style={'color':'#666'}),
            html.P('Sistema de Informação de Vigilância Epidemiológica da Gripe (SVS/MS).', style={'fontSize':'13px'}),
            html.Ul([
                html.Li('Notificações semanais de SRAG desde 2012'),
                html.Li('Variáveis: diagnóstico, hospitalização, UTI, óbito'),
                html.Li('Agente etiológico confirmado por PCR'),
                html.Li('Granularidade: município de residência'),
            ], style={'fontSize':'12px','color':'#555','paddingLeft':'16px'}),
            html.P([html.A('🔗 Acessar OpenDataSUS — SRAG Hospitalizados', href='https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024', target='_blank', style={'color':TEAL,'fontSize':'12px'})]),
        ]), md=6),
    ]),
])

# ── ABA ATUALIZAÇÃO DE DADOS ──────────────────────────────────────────────
tab_atualizacao = html.Div(className='page-wrapper', children=[
    html.Div(className='hero-section', style={'padding':'24px'}, children=[
        html.H2('🔄 Atualização de Dados'),
        html.P('Interface para upload, validação e integração de novos dados climáticos ao painel.'),
    ]),
    dbc.Row([
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {TEAL}'}, children=[
            html.H5('📤 Upload de Novo Arquivo CSV', style={'color':TEAL}),
            html.P('Faça upload de um arquivo CSV com dados climáticos no formato padrão do GeoCalor (INMET/ICEA).', style={'fontSize':'13px','color':'#555'}),
            html.Div(style={'background':'#f0f9f9','borderRadius':'6px','padding':'12px','marginBottom':'12px','fontFamily':'monospace','fontSize':'11px'}, children=[
                html.P('Colunas obrigatórias:', style={'fontWeight':'bold','color':TEAL,'margin':'0 0 6px'}),
                html.P('cidade, date, tempMax, tempMin, tempMed, umidade', style={'margin':'0 0 4px','color':'#333'}),
                html.P('Formato da data: YYYY-MM-DD', style={'margin':'0','color':'#777'}),
            ]),
            dcc.Upload(
                id='upload-dados',
                children=html.Div([
                    html.Div('📁', style={'fontSize':'32px','marginBottom':'8px'}),
                    html.Strong('Arraste e solte ou clique para selecionar'),
                    html.P('Formatos aceitos: .csv, .csv.gz', style={'fontSize':'12px','color':'#888','margin':'4px 0 0'}),
                ]),
                style={
                    'width':'100%','height':'120px','lineHeight':'1.4',
                    'borderWidth':'2px','borderStyle':'dashed','borderRadius':'8px',
                    'borderColor':TEAL,'textAlign':'center','padding':'20px',
                    'cursor':'pointer','background':'#f0f9f9',
                },
                multiple=False,
            ),
            html.Div(id='upload-status', style={'marginTop':'12px'}),
        ]), md=6),
        dbc.Col(html.Div(className='info-card', style={'borderLeft':f'4px solid {ORANGE}'}, children=[
            html.H5('📊 Status dos Dados Atuais', style={'color':ORANGE}),
            html.Div(id='status-dados-atuais', children=[
                html.Div(style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'8px'}, children=[
                    html.Div(style={'background':'#e0f5f5','borderRadius':'6px','padding':'10px','textAlign':'center'}, children=[
                        html.Strong(f'{len(df_all):,}', style={'fontSize':'20px','color':TEAL,'display':'block'}),
                        html.Span('Registros totais', style={'fontSize':'11px','color':'#777'}),
                    ]),
                    html.Div(style={'background':'#fff0e0','borderRadius':'6px','padding':'10px','textAlign':'center'}, children=[
                        html.Strong(f'{df_all["cidade"].nunique()}', style={'fontSize':'20px','color':ORANGE,'display':'block'}),
                        html.Span('Cidades', style={'fontSize':'11px','color':'#777'}),
                    ]),
                    html.Div(style={'background':'#f0f9f9','borderRadius':'6px','padding':'10px','textAlign':'center'}, children=[
                        html.Strong(df_all['date'].min().strftime('%d/%m/%Y'), style={'fontSize':'14px','color':TEAL,'display':'block'}),
                        html.Span('Data inicial', style={'fontSize':'11px','color':'#777'}),
                    ]),
                    html.Div(style={'background':'#f0f9f9','borderRadius':'6px','padding':'10px','textAlign':'center'}, children=[
                        html.Strong(df_all['date'].max().strftime('%d/%m/%Y'), style={'fontSize':'14px','color':TEAL,'display':'block'}),
                        html.Span('Data final', style={'fontSize':'11px','color':'#777'}),
                    ]),
                ]),
                html.Hr(),
                html.P([html.Strong('Cidades disponíveis: '), ', '.join(sorted(df_all['cidade'].unique()))], style={'fontSize':'11px','color':'#555'}),
                html.P([html.Strong('Arquivo: '), 'data/temp.csv.gz'], style={'fontSize':'11px','color':'#777'}),
            ]),
        ]), md=6),
    ]),
    html.Div(className='info-card', style={'marginTop':'16px'}, children=[
        html.H5('📝 Formato Padrão do Arquivo CSV', style={'color':TEAL}),
        html.P('O arquivo deve seguir o formato abaixo. As colunas de onda de calor (hw_*, ehf_*) serão calculadas automaticamente pelo sistema.', style={'fontSize':'13px'}),
        dash_table.DataTable(
            data=[
                {'cidade':'Belém','date':'2023-01-01','tempMax':'33.4','tempMin':'24.1','tempMed':'28.7','umidade':'82.3','hw_95':'0','ehf':'−2.14'},
                {'cidade':'Belém','date':'2023-01-02','tempMax':'34.1','tempMin':'24.8','tempMed':'29.4','umidade':'79.1','hw_95':'0','ehf':'−1.87'},
                {'cidade':'Belém','date':'2023-01-03','tempMax':'35.8','tempMin':'25.2','tempMed':'30.5','umidade':'74.6','hw_95':'1','ehf':'0.43'},
            ],
            columns=[{'name': c, 'id': c} for c in ['cidade','date','tempMax','tempMin','tempMed','umidade','hw_95','ehf']],
            style_header={'backgroundColor':TEAL,'color':'white','fontWeight':'bold','fontSize':'12px'},
            style_cell={'fontSize':'12px','padding':'6px 10px','textAlign':'left'},
            style_data_conditional=[{'if':{'row_index':'odd'},'backgroundColor':'#f8f9fa'}],
        ),
    ]),
    html.Div(className='info-card', style={'marginTop':'16px','background':'#fff8f0','borderLeft':f'4px solid {ORANGE}'}, children=[
        html.H5('⚠️ Instruções de Atualização', style={'color':ORANGE}),
        html.Ol([
            html.Li('Prepare o arquivo CSV no formato padrão acima (colunas obrigatórias)'),
            html.Li('Faça upload usando o botão acima ou arraste o arquivo'),
            html.Li('O sistema validará o formato e exibirá um preview dos dados'),
            html.Li('Confirme a integração para substituir ou complementar os dados existentes'),
            html.Li('O painel será atualizado automaticamente após a integração'),
        ], style={'fontSize':'13px','color':'#555','paddingLeft':'20px'}),
        html.P([html.Strong('Fonte recomendada: '), html.A('INMET — Banco de Dados Meteorológicos', href='https://bdmep.inmet.gov.br/', target='_blank', style={'color':ORANGE}), ' | ', html.A('ICEA — Dados Climáticos', href='https://www.icea.decea.mil.br/', target='_blank', style={'color':ORANGE})], style={'fontSize':'12px','marginTop':'10px'}),
    ]),
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
        'srag': tab_srag,
        'atualizacao': tab_atualizacao,
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
    Input('nav-ondas', 'n_clicks'),
    Input('hw-cidade', 'value'),
    Input('hw-ano', 'value'),
    Input('hw-heatmap-tipo', 'value'),
    Input('polar-modo', 'value'),
    Input('polar-cidades', 'value'),
    prevent_initial_call=True,
)
def update_ondas(_nav, cidade, ano, heatmap_tipo, polar_modo, polar_cidades):
    # Gráfico polar — comparativo ou múltiplos
    if not polar_cidades:
        polar_cidades = ['Belém', 'Cuiabá', 'São Paulo', 'Curitiba', 'Fortaleza']
    ano_label = str(ano) if ano != 'Todos' else 'Todos os anos'
    # Filtrar por ano se selecionado
    def _polar_filtrado(c):
        df_c = filter_df(cidade=c)
        if ano != 'Todos':
            df_c = df_c[df_c['date'].dt.year == int(ano)]
        hw = df_c[df_c['isHW']]
        import pandas as _pd
        meses_nomes = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
        freq = hw.groupby(hw['date'].dt.month).size().reset_index(name='count')
        freq.columns = ['month_num', 'count']
        full = _pd.DataFrame({'month_num': range(1,13), 'mes': meses_nomes})
        freq = full.merge(freq, on='month_num', how='left').fillna(0)
        return freq
    freq_dict = {c: _polar_filtrado(c) for c in polar_cidades}
    if polar_modo == 'comparar':
        f_pol = fig_polar_comparativo(freq_dict, ano_label)
    else:
        f_pol = fig_polar_multiplos(freq_dict, ano_label)
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
        cidades = ['Belém', 'Cuiabá', 'São Paulo', 'Curitiba', 'Fortaleza']
    if isinstance(cidades, str):
        cidades = [cidades]
    # Limitar a 6 cidades para legibilidade
    cidades = cidades[:6]
    return fig_radar_cidade(df_all, cidades)


@app.callback(
    Output('upload-status', 'children'),
    Input('upload-dados', 'contents'),
    State('upload-dados', 'filename'),
    prevent_initial_call=True,
)
def processar_upload(contents, filename):
    if contents is None:
        return ''
    import base64, io
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith('.csv.gz'):
            import gzip
            with gzip.open(io.BytesIO(decoded), 'rt', encoding='utf-8') as f:
                df_novo = pd.read_csv(f)
        elif filename.endswith('.csv'):
            df_novo = pd.read_csv(io.BytesIO(decoded))
        else:
            return html.Div([
                html.Span('❌ Formato não suportado. Use .csv ou .csv.gz', style={'color':'red','fontSize':'13px'})
            ])

        # Validar colunas obrigatórias
        colunas_obrig = ['cidade','date','tempMax','tempMin','tempMed','umidade']
        faltando = [c for c in colunas_obrig if c not in df_novo.columns]
        if faltando:
            return html.Div([
                html.Span(f'❌ Colunas faltando: {", ".join(faltando)}', style={'color':'red','fontSize':'13px'})
            ])

        # Validar formato de data
        try:
            df_novo['date'] = pd.to_datetime(df_novo['date'])
        except Exception:
            return html.Div([
                html.Span('❌ Erro no formato da data. Use YYYY-MM-DD.', style={'color':'red','fontSize':'13px'})
            ])

        n_cidades = df_novo['cidade'].nunique()
        n_registros = len(df_novo)
        dt_min = df_novo['date'].min().strftime('%d/%m/%Y')
        dt_max = df_novo['date'].max().strftime('%d/%m/%Y')

        return html.Div([
            html.Div(style={'background':'#e8f5e9','borderRadius':'8px','padding':'12px','border':'1px solid #4caf50'}, children=[
                html.Span('✅ Arquivo validado com sucesso!', style={'color':'#2e7d32','fontWeight':'bold','fontSize':'13px','display':'block'}),
                html.Div(style={'display':'grid','gridTemplateColumns':'1fr 1fr 1fr 1fr','gap':'8px','marginTop':'8px'}, children=[
                    html.Div(style={'textAlign':'center'}, children=[
                        html.Strong(f'{n_registros:,}', style={'color':TEAL,'display':'block'}),
                        html.Span('Registros', style={'fontSize':'11px','color':'#777'}),
                    ]),
                    html.Div(style={'textAlign':'center'}, children=[
                        html.Strong(f'{n_cidades}', style={'color':ORANGE,'display':'block'}),
                        html.Span('Cidades', style={'fontSize':'11px','color':'#777'}),
                    ]),
                    html.Div(style={'textAlign':'center'}, children=[
                        html.Strong(dt_min, style={'color':TEAL,'display':'block','fontSize':'12px'}),
                        html.Span('Data inicial', style={'fontSize':'11px','color':'#777'}),
                    ]),
                    html.Div(style={'textAlign':'center'}, children=[
                        html.Strong(dt_max, style={'color':TEAL,'display':'block','fontSize':'12px'}),
                        html.Span('Data final', style={'fontSize':'11px','color':'#777'}),
                    ]),
                ]),
                html.Hr(style={'margin':'10px 0'}),
                html.P(f'Cidades encontradas: {", ".join(sorted(df_novo["cidade"].unique()))}',
                       style={'fontSize':'11px','color':'#555','margin':'0'}),
                html.Div(style={'marginTop':'10px','background':'#fff8f0','borderRadius':'6px','padding':'8px'}, children=[
                    html.Span('⚠️ Para integrar permanentemente, salve o arquivo em data/temp.csv.gz e reinicie o app.',
                              style={'fontSize':'11px','color':ORANGE}),
                ]),
            ])
        ])
    except Exception as e:
        return html.Div([
            html.Span(f'❌ Erro ao processar arquivo: {str(e)}', style={'color':'red','fontSize':'13px'})
        ])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)
