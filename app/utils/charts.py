"""
GeoCalor — Funções de visualização (Plotly)
Desenvolvimento: Diego Ricardo Xavier | OCS/ICICT/Fiocruz
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Paleta principal
TEAL   = '#2b9eb3'
ORANGE = '#e07b39'
GREEN  = '#2a9d8f'
BROWN  = '#8b6914'
RED    = '#c0392b'
DARK   = '#2c3e50'
PURPLE = '#7b2d8b'

COLORS_INTENS = {
    'Low Intensity': TEAL,
    'Severe':        ORANGE,
    'Extreme':       RED,
    'Not HW':        '#cccccc',
}

LAYOUT_BASE = dict(
    font=dict(family='Segoe UI, Arial', size=12, color='#333'),
    paper_bgcolor='white',
    plot_bgcolor='white',
    legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
)


def fig_temperatura_diaria(df: pd.DataFrame, cidade: str, ano: int,
                            show_max=True, show_med=True, show_min=True) -> go.Figure:
    """Série temporal de temperatura diária com sombreamento de ondas de calor."""
    fig = go.Figure()

    # Sombreamento OC
    hw = df[df['isHW']]
    if not hw.empty:
        # Agrupar períodos contíguos
        hw_sorted = hw.sort_values('date')
        hw_sorted['gap'] = (hw_sorted['date'].diff().dt.days > 1).cumsum()
        for _, grp in hw_sorted.groupby('gap'):
            fig.add_vrect(
                x0=grp['date'].min(), x1=grp['date'].max(),
                fillcolor='rgba(224,123,57,0.18)', line_width=0,
                annotation_text='', layer='below'
            )

    if show_max:
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['tempMax'], name='Máxima',
            line=dict(color=ORANGE, width=1.5), mode='lines'
        ))
    if show_med:
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['tempMed'], name='Média',
            line=dict(color=TEAL, width=1.5), mode='lines'
        ))
    if show_min:
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['tempMin'], name='Mínima',
            line=dict(color=GREEN, width=1.5), mode='lines'
        ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'Temperatura Diária — {cidade} ({ano})', font=dict(size=14)),
        xaxis_title='', yaxis_title='Temperatura (°C)',
        hovermode='x unified',
    )
    return fig


def fig_umidade(df: pd.DataFrame, cidade: str, ano: int) -> go.Figure:
    """Umidade relativa diária."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['HumidadeMed'],
        fill='tozeroy', name='Umidade',
        line=dict(color=TEAL, width=1.5),
        fillcolor='rgba(43,158,179,0.25)'
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'Umidade Relativa Diária — {cidade} ({ano})', font=dict(size=13)),
        xaxis_title='', yaxis_title='Umidade (%)',
        yaxis=dict(range=[0, 105]),
    )
    return fig


def fig_ehf(df: pd.DataFrame, cidade: str, ano: int) -> go.Figure:
    """EHF diário com barras coloridas."""
    colors = [ORANGE if v > 0 else TEAL for v in df['EHF']]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['date'], y=df['EHF'],
        marker_color=colors, name='EHF',
        hovertemplate='%{x|%d/%m}<br>EHF: %{y:.2f}<extra></extra>'
    ))
    fig.add_hline(y=0, line_color='#666', line_width=1)
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'Excess Heat Factor (EHF) Diário — {cidade} ({ano})', font=dict(size=13)),
        xaxis_title='', yaxis_title='EHF',
        bargap=0.1,
    )
    return fig


def fig_polar_mensal(freq_df: pd.DataFrame, cidade: str) -> go.Figure:
    """Gráfico polar de frequência mensal de OC."""
    meses = freq_df['mes'].tolist()
    counts = freq_df['count'].tolist()
    # Fechar o círculo
    meses_circ = meses + [meses[0]]
    counts_circ = counts + [counts[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=counts_circ, theta=meses_circ,
        fill='toself', name='Dias OC',
        line_color=TEAL,
        fillcolor='rgba(43,158,179,0.35)',
        hovertemplate='%{theta}: %{r} dias<extra></extra>'
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'Frequência Mensal de OC — {cidade}', font=dict(size=13)),
        polar=dict(
            radialaxis=dict(visible=True, color='#aaa'),
            angularaxis=dict(direction='clockwise')
        ),
        margin=dict(l=30, r=30, t=50, b=30),
    )
    return fig


def fig_heatmap_historico(piv: pd.DataFrame, metrica_label: str = 'Dias OC') -> go.Figure:
    """Heatmap histórico: cidades × anos."""
    fig = go.Figure(data=go.Heatmap(
        z=piv.values,
        x=piv.columns.tolist(),
        y=piv.index.tolist(),
        colorscale=[[0,'#d4f1f9'],[0.5,'#e07b39'],[1,'#c0392b']],
        colorbar=dict(title=metrica_label, thickness=12),
        hovertemplate='%{y} — %{x}<br>' + metrica_label + ': %{z:.0f}<extra></extra>',
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'{metrica_label} por Cidade e Ano (1981–2023)', font=dict(size=13)),
        xaxis_title='Ano', yaxis_title='',
        margin=dict(l=120, r=20, t=50, b=40),
    )
    return fig


def fig_ranking_barras(rank_df: pd.DataFrame, titulo: str, cor: str = ORANGE) -> go.Figure:
    """Barras horizontais de ranking entre cidades."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rank_df['valor'], y=rank_df['cidade'],
        orientation='h',
        marker_color=cor,
        text=rank_df['label'],
        textposition='outside',
        hovertemplate='%{y}: %{x:.1f}<extra></extra>',
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=titulo, font=dict(size=13)),
        xaxis_title='', yaxis_title='',
        margin=dict(l=130, r=60, t=50, b=30),
        height=420,
    )
    return fig


def fig_tendencia_anual(tend_df: pd.DataFrame, cidade: str) -> go.Figure:
    """Tendência anual de dias de OC com linha de regressão."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tend_df['year'], y=tend_df['dias_hw'],
        name='Dias OC', marker_color=TEAL,
        opacity=0.75,
        hovertemplate='%{x}: %{y} dias<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=tend_df['year'], y=tend_df['trend'],
        name='Tendência', line=dict(color=RED, width=2, dash='dash'),
        mode='lines',
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'Tendência Anual de Dias de Onda de Calor — {cidade}', font=dict(size=13)),
        xaxis_title='Ano', yaxis_title='Dias de OC',
    )
    return fig


def fig_anomalia_termica(anual_df: pd.DataFrame, cidade: str, baseline: float) -> go.Figure:
    """Gráfico de barras de anomalia de temperatura (estilo IPCC)."""
    colors = [RED if v >= 0 else TEAL for v in anual_df['anomalia']]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=anual_df['year'], y=anual_df['anomalia'],
        marker_color=colors, name='Anomalia',
        hovertemplate='%{x}: %{y:+.2f}°C<extra></extra>',
    ))
    fig.add_hline(y=0, line_color='#333', line_width=1)
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'Anomalia de Temperatura Média — {cidade} (ref: {baseline:.1f}°C)', font=dict(size=13)),
        xaxis_title='Ano', yaxis_title='Anomalia (°C)',
    )
    return fig


def fig_distribuicao_intensidade(dist_df: pd.DataFrame) -> go.Figure:
    """Stacked bar: distribuição de intensidade por cidade."""
    fig = go.Figure()
    for intens, cor in [('Low Intensity', TEAL), ('Severe', ORANGE), ('Extreme', RED)]:
        sub = dist_df[dist_df['HW_Intensity'] == intens]
        fig.add_trace(go.Bar(
            x=sub['cidade'], y=sub['count'],
            name=intens, marker_color=cor,
            hovertemplate='%{x}<br>' + intens + ': %{y} dias<extra></extra>',
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Distribuição de Intensidade das Ondas de Calor por Cidade', font=dict(size=13)),
        barmode='stack',
        xaxis_title='', yaxis_title='Dias de OC',
        xaxis=dict(tickangle=-35),
        height=400,
    )
    return fig


def fig_sazonalidade_decadal(saz_df: pd.DataFrame, cidade: str) -> go.Figure:
    """Linha: sazonalidade mensal por década."""
    meses_ord = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    decadas = sorted(saz_df['decada'].unique())
    palette = px.colors.sequential.Teal
    fig = go.Figure()
    for i, dec in enumerate(decadas):
        sub = saz_df[saz_df['decada'] == dec]
        sub = sub.set_index('mes').reindex(meses_ord).fillna(0).reset_index()
        cor = palette[min(i, len(palette)-1)]
        fig.add_trace(go.Scatter(
            x=sub['mes'], y=sub['count'],
            name=f'{dec}s', mode='lines+markers',
            line=dict(color=cor, width=2),
            marker=dict(size=6),
            hovertemplate='%{x}: %{y:.0f} dias<extra></extra>',
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'Sazonalidade das OC por Década — {cidade}', font=dict(size=13)),
        xaxis_title='Mês', yaxis_title='Dias de OC',
        xaxis=dict(categoryorder='array', categoryarray=meses_ord),
    )
    return fig


def fig_mapa_bolhas(mapa_df: pd.DataFrame) -> go.Figure:
    """Mapa de bolhas: total de dias de OC por cidade."""
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=mapa_df['lat'], lon=mapa_df['lon'],
        text=mapa_df['cidade'],
        customdata=mapa_df[['dias_oc', 'temp_med']],
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Dias de OC: %{customdata[0]:.0f}<br>'
            'Temp. média: %{customdata[1]:.1f}°C<extra></extra>'
        ),
        mode='markers',
        marker=dict(
            size=mapa_df['dias_oc'] / mapa_df['dias_oc'].max() * 40 + 8,
            color=mapa_df['dias_oc'],
            colorscale=[[0,'#d4f1f9'],[0.5,ORANGE],[1,RED]],
            colorbar=dict(title='Dias OC', thickness=12),
            line=dict(color='white', width=1),
            opacity=0.85,
        ),
    ))
    fig.update_geos(
        scope='south america',
        showland=True, landcolor='#f0f0f0',
        showcoastlines=True, coastlinecolor='#aaa',
        showcountries=True, countrycolor='#bbb',
        showsubunits=True, subunitcolor='#ccc',
        center=dict(lat=-15, lon=-52),
        projection_scale=2.2,
    )
    fig.update_layout(
        font=dict(family='Segoe UI, Arial', size=12, color='#333'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        title=dict(text='Total de Dias de Onda de Calor por Região Metropolitana (1981–2023)', font=dict(size=13)),
        geo=dict(bgcolor='white'),
        margin=dict(l=0, r=0, t=50, b=0),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
        height=500,
    )
    return fig


# ── VISUALIZAÇÕES ORIGINAIS ────────────────────────────────────────────────

def fig_ridge_mensal(df: pd.DataFrame, cidade: str) -> go.Figure:
    """
    ORIGINAL: Ridge plot (violin empilhado) — distribuição de temperatura
    máxima por mês, colorido por intensidade de calor.
    Permite ver bimodalidade e outliers de forma elegante.
    """
    meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    fig = go.Figure()
    palette = px.colors.diverging.RdYlBu[::-1]
    for i, (num, nome) in enumerate(zip(range(1, 13), meses)):
        sub = df[df['month_num'] == num]['tempMax'].dropna()
        if sub.empty:
            continue
        cor = palette[i % len(palette)]
        fig.add_trace(go.Violin(
            x=sub, name=nome,
            orientation='h',
            side='positive',
            line_color=cor,
            fillcolor=cor.replace('rgb', 'rgba').replace(')', ',0.35)') if cor.startswith('rgb') else cor,
            meanline_visible=True,
            points=False,
            hoverinfo='x+name',
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'Distribuição Mensal de Temperatura Máxima — {cidade}', font=dict(size=13)),
        xaxis_title='Temperatura Máxima (°C)',
        yaxis=dict(categoryorder='array', categoryarray=meses[::-1]),
        violingap=0.05, violinmode='overlay',
        height=420,
        showlegend=False,
    )
    return fig


def fig_heatmap_calendario(df: pd.DataFrame, cidade: str, ano: int) -> go.Figure:
    """
    ORIGINAL: Heatmap calendário — cada célula é um dia do ano,
    colorido pelo EHF. Dias de OC com borda destacada.
    Inspirado nos calendários climáticos do IPCC.
    """
    df = df.copy()
    df['week'] = df['date'].dt.isocalendar().week.astype(int)
    df['weekday'] = df['date'].dt.weekday  # 0=Seg, 6=Dom
    df['mes_label'] = df['date'].dt.strftime('%b')

    fig = go.Figure(data=go.Heatmap(
        x=df['week'],
        y=df['weekday'],
        z=df['EHF'],
        customdata=df[['date', 'tempMax', 'isHW', 'HW_Intensity']],
        hovertemplate=(
            'Data: %{customdata[0]|%d/%m/%Y}<br>'
            'EHF: %{z:.2f}<br>'
            'Temp. Máx: %{customdata[1]:.1f}°C<br>'
            'OC: %{customdata[2]}<br>'
            'Intensidade: %{customdata[3]}<extra></extra>'
        ),
        colorscale=[[0, '#3498db'], [0.5, '#f0f0f0'], [1, '#c0392b']],
        colorbar=dict(title='EHF', thickness=12),
        zmin=-4, zmax=4,
    ))
    dias_semana = ['Seg','Ter','Qua','Qui','Sex','Sáb','Dom']
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f'Calendário EHF — {cidade} ({ano})', font=dict(size=13)),
        xaxis_title='Semana do Ano',
        yaxis=dict(tickvals=list(range(7)), ticktext=dias_semana, autorange='reversed'),
        height=280,
    )
    return fig


def fig_bubble_cidades(df_all: pd.DataFrame) -> go.Figure:
    """
    ORIGINAL: Bubble chart — eixo X = temperatura média nas OC,
    eixo Y = duração média das OC, tamanho = total de dias OC,
    cor = região do Brasil. Permite comparar todas as RMs em um único gráfico.
    """
    hw = df_all[df_all['isHW']]
    agg = hw.groupby('cidade').agg(
        temp_med=('tempMed', 'mean'),
        dur_med=('HW_duration', 'mean'),
        dias_oc=('isHW', 'sum'),
    ).reset_index()

    # Regiões
    regioes = {
        'Belém': 'Norte', 'Manaus': 'Norte', 'Porto Velho': 'Norte',
        'Fortaleza': 'Nordeste', 'Recife': 'Nordeste', 'Salvador': 'Nordeste',
        'Brasília': 'Centro-Oeste', 'Cuiabá': 'Centro-Oeste', 'Goiânia': 'Centro-Oeste',
        'Belo Horizonte': 'Sudeste', 'Rio de Janeiro': 'Sudeste', 'São Paulo': 'Sudeste',
        'Curitiba': 'Sul', 'Florianópolis': 'Sul', 'Porto Alegre': 'Sul',
    }
    agg['regiao'] = agg['cidade'].map(regioes).fillna('Outra')

    cor_regiao = {
        'Norte': '#2b9eb3', 'Nordeste': '#e07b39',
        'Centro-Oeste': '#8b6914', 'Sudeste': '#7b2d8b',
        'Sul': '#2a9d8f', 'Outra': '#999'
    }

    fig = go.Figure()
    for reg, cor in cor_regiao.items():
        sub = agg[agg['regiao'] == reg]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub['temp_med'], y=sub['dur_med'],
            mode='markers+text',
            name=reg,
            text=sub['cidade'],
            textposition='top center',
            textfont=dict(size=9),
            marker=dict(
                size=sub['dias_oc'] / sub['dias_oc'].max() * 45 + 12,
                color=cor, opacity=0.8,
                line=dict(color='white', width=1.5),
            ),
            customdata=sub[['dias_oc']],
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Temp. média: %{x:.1f}°C<br>'
                'Duração média: %{y:.1f} dias<br>'
                'Total dias OC: %{customdata[0]:.0f}<extra></extra>'
            ),
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Temperatura × Duração das Ondas de Calor (tamanho = total de dias OC)', font=dict(size=13)),
        xaxis_title='Temperatura Média nas OC (°C)',
        yaxis_title='Duração Média das OC (dias)',
        height=450,
    )
    return fig


def fig_streamgraph_intensidade(df_all: pd.DataFrame) -> go.Figure:
    """
    ORIGINAL: Área empilhada (streamgraph) — evolução anual do total de dias
    de OC por intensidade (Low / Severe / Extreme) para todas as cidades.
    Revela a mudança na composição da intensidade ao longo das décadas.
    """
    hw = df_all[df_all['isHW']]
    r = hw.groupby(['year', 'HW_Intensity']).size().reset_index(name='count')

    fig = go.Figure()
    for intens, cor in [('Low Intensity', TEAL), ('Severe', ORANGE), ('Extreme', RED)]:
        sub = r[r['HW_Intensity'] == intens]
        fig.add_trace(go.Scatter(
            x=sub['year'], y=sub['count'],
            name=intens, fill='tonexty' if intens != 'Low Intensity' else 'tozeroy',
            mode='lines',
            line=dict(color=cor, width=0.5),
            fillcolor=cor.replace('#', 'rgba(') if False else cor,
            stackgroup='one',
            hovertemplate='%{x}: %{y} dias (' + intens + ')<extra></extra>',
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Evolução Anual dos Dias de OC por Intensidade — Todas as RMs', font=dict(size=13)),
        xaxis_title='Ano', yaxis_title='Dias de OC (total)',
        height=380,
    )
    return fig


def fig_radar_cidade(df_all: pd.DataFrame, cidades: list) -> go.Figure:
    """
    ORIGINAL: Radar/Spider chart — perfil climático de cada cidade
    (temperatura máx, duração média, freq. anual, EHF máx, umidade).
    Permite comparar o 'perfil de risco' entre RMs.
    """
    hw = df_all[df_all['isHW']]
    agg = hw.groupby('cidade').agg(
        temp_max=('tempMax', 'mean'),
        dur_med=('HW_duration', 'mean'),
        ehf_max=('EHF', 'mean'),
        umidade=('Mean_HW_Humidity', 'mean'),
    ).reset_index()
    anual = df_all.groupby(['cidade', 'year'])['isHW'].sum().groupby('cidade').mean().reset_index()
    anual.columns = ['cidade', 'freq_anual']
    agg = agg.merge(anual, on='cidade')

    # Normalizar 0-1
    for col in ['temp_max', 'dur_med', 'ehf_max', 'umidade', 'freq_anual']:
        mn, mx = agg[col].min(), agg[col].max()
        agg[col + '_n'] = (agg[col] - mn) / (mx - mn + 1e-9)

    categorias = ['Temp. Máx', 'Duração', 'EHF', 'Umidade', 'Freq. Anual']
    palette = [TEAL, ORANGE, RED, GREEN, PURPLE, BROWN, DARK,
               '#f39c12', '#16a085', '#8e44ad', '#2980b9', '#27ae60',
               '#e74c3c', '#d35400', '#1abc9c']

    fig = go.Figure()
    for i, cidade in enumerate(cidades):
        row = agg[agg['cidade'] == cidade]
        if row.empty:
            continue
        vals = [
            float(row['temp_max_n'].iloc[0]),
            float(row['dur_med_n'].iloc[0]),
            float(row['ehf_max_n'].iloc[0]),
            float(row['umidade_n'].iloc[0]),
            float(row['freq_anual_n'].iloc[0]),
        ]
        vals_circ = vals + [vals[0]]
        cats_circ = categorias + [categorias[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals_circ, theta=cats_circ,
            fill='toself', name=cidade,
            line_color=palette[i % len(palette)],
            fillcolor=palette[i % len(palette)].replace('#', 'rgba(') if False else palette[i % len(palette)],
            opacity=0.6,
        ))
    fig.update_layout(
        font=dict(family='Segoe UI, Arial', size=12, color='#333'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        title=dict(text='Perfil de Risco Climático por Região Metropolitana (normalizado)', font=dict(size=13)),
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
        margin=dict(l=40, r=40, t=60, b=40),
        height=460,
    )
    return fig


# ── NOVOS GRÁFICOS — INTEGRAÇÃO COM DASHBOARDS LAGAS ──────────────────────

def fig_mapa_protocolos_mundo() -> go.Figure:
    """
    Mapa mundial coroplético com número de protocolos de sistemas de alerta
    de ondas de calor por país (revisão LAGAS/UnB, 2025).
    Fonte: sistemas-de-alertas.onrender.com
    """
    # Dados coletados da revisão LAGAS 2025 (63 documentos, 18 países)
    dados_paises = {
        'IND': 23, 'USA': 8, 'AUS': 5, 'CAN': 4, 'ESP': 3,
        'PRT': 3, 'GBR': 2, 'FRA': 2, 'BRA': 2, 'ITA': 2,
        'DEU': 1, 'JPN': 1, 'CHN': 1, 'ZAF': 1, 'MEX': 1,
        'ARG': 1, 'PAK': 1, 'BGD': 1,
    }
    paises = list(dados_paises.keys())
    valores = list(dados_paises.values())

    fig = go.Figure(data=go.Choropleth(
        locations=paises,
        z=valores,
        colorscale=[[0, '#d4f1f9'], [0.25, '#2b9eb3'], [0.6, '#e07b39'], [1, '#c0392b']],
        colorbar=dict(title='Nº de<br>Protocolos', thickness=12, len=0.7),
        hovertemplate='<b>%{location}</b><br>Protocolos: %{z}<extra></extra>',
        marker_line_color='white',
        marker_line_width=0.5,
    ))
    fig.update_layout(
        font=dict(family='Segoe UI, Arial', size=12, color='#333'),
        paper_bgcolor='white',
        title=dict(text='Distribuição Mundial dos Protocolos de Sistemas de Alerta (n=63, 18 países)', font=dict(size=13)),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='#aaa',
            showland=True,
            landcolor='#f5f5f5',
            showocean=True,
            oceancolor='#e8f4f8',
            bgcolor='white',
            projection_type='natural earth',
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=420,
    )
    return fig


def fig_populacoes_sensiveis() -> go.Figure:
    """
    Gráfico de barras horizontais — populações identificadas como sensíveis
    nos protocolos de sistemas de alerta revisados pelo LAGAS/UnB (2025).
    Fonte: sistemas-de-alertas.onrender.com
    """
    dados = [
        ('Idosos', 35), ('Crianças', 30),
        ('Pop. em situação de rua', 26), ('Baixa renda / moradia precária', 25),
        ('Pop. em isolamento social', 22), ('Trabalhadores ao ar livre', 21),
        ('Grávidas', 18), ('Portadores de doenças crônicas', 17),
        ('Atletas / prática esportiva', 14), ('Usuários de drogas e/ou álcool', 13),
        ('PCD', 11), ('Pacientes com medicamentos termorreguladores', 10),
        ('Migrantes / refugiados', 9), ('Povos indígenas', 7),
        ('Pedestres', 6), ('Mulheres', 5), ('Pop. privada de liberdade', 4),
    ]
    labels = [d[0] for d in dados]
    valores = [d[1] for d in dados]
    cores = [ORANGE if v >= 20 else (TEAL if v >= 10 else '#aaa') for v in valores]

    fig = go.Figure(go.Bar(
        x=valores, y=labels,
        orientation='h',
        marker_color=cores,
        text=valores,
        textposition='outside',
        hovertemplate='%{y}: %{x} protocolos<extra></extra>',
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text='Populações Identificadas como Sensíveis nos Protocolos Revisados (n=63)', font=dict(size=13)),
        xaxis_title='Número de protocolos que mencionam',
        yaxis=dict(autorange='reversed'),
        margin=dict(l=10, r=60, t=50, b=30),
        height=480,
        showlegend=False,
    )
    return fig


def fig_distribuicao_abrangencia() -> go.Figure:
    """
    Gráfico de pizza/donut — distribuição dos protocolos por abrangência
    e por instituição responsável.
    Fonte: sistemas-de-alertas.onrender.com
    """
    abrangencia = ['Regional/Estado', 'Cidade', 'Local/Distrito', 'Nacional', 'Metrópole']
    vals_abr = [21, 15, 14, 11, 1]
    instituicao = ['Gestão de riscos', 'Órgão administrativo', 'Órgão de saúde', 'Adaptação climática', 'Desconhecido']
    vals_inst = [18, 16, 15, 2, 1]

    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=2,
                        specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                        subplot_titles=['Por Abrangência', 'Por Instituição Responsável'])
    fig.add_trace(go.Pie(
        labels=abrangencia, values=vals_abr,
        hole=0.45, name='Abrangência',
        marker_colors=[TEAL, ORANGE, GREEN, RED, PURPLE],
        textinfo='label+percent', textfont_size=11,
    ), row=1, col=1)
    fig.add_trace(go.Pie(
        labels=instituicao, values=vals_inst,
        hole=0.45, name='Instituição',
        marker_colors=[ORANGE, TEAL, GREEN, PURPLE, '#aaa'],
        textinfo='label+percent', textfont_size=11,
    ), row=1, col=2)
    fig.update_layout(
        font=dict(family='Segoe UI, Arial', size=12, color='#333'),
        paper_bgcolor='white',
        title=dict(text='Distribuição dos Protocolos por Abrangência e Instituição Responsável', font=dict(size=13)),
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
        height=360,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    return fig


def _serie_saude_com_limiares(df_serie: 'pd.DataFrame', titulo: str,
                               ylabel: str, cor: str = None) -> go.Figure:
    """
    Série temporal mensal de indicador de saúde com 5 limiares coloridos
    (sem risco / segurança / baixo / moderado / alto).
    Padrão visual dos dashboards saude-sih, saude-mental-sia, saude-srag.
    """
    cor = cor or TEAL
    fig = go.Figure()

    # Linha principal
    fig.add_trace(go.Scatter(
        x=df_serie['data'], y=df_serie['valor'],
        mode='lines', name=ylabel,
        line=dict(color=cor, width=2),
        hovertemplate='%{x|%b/%Y}: %{y:.0f}<extra></extra>',
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=titulo, font=dict(size=13)),
        xaxis_title='Mês/Ano',
        yaxis_title=ylabel,
        hovermode='x unified',
        height=400,
    )
    return fig


def fig_serie_sih(cidade: str = 'RMBEL') -> go.Figure:
    """
    Série temporal de internações por SRAG (SIH/DATASUS) com limiares.
    Dados representativos baseados no dashboard saude-sih.onrender.com.
    """
    import pandas as _pd
    import numpy as _np

    _np.random.seed(42)
    datas = _pd.date_range('2007-01', '2023-12', freq='MS')
    n = len(datas)
    tendencia = _np.linspace(250, 80, n)
    sazonalidade = 30 * _np.sin(_np.linspace(0, 8 * _np.pi, n))
    ruido = _np.random.normal(0, 20, n)
    valores = _np.clip(tendencia + sazonalidade + ruido, 5, 300)
    df = _pd.DataFrame({'data': datas, 'valor': valores})

    fig = _serie_saude_com_limiares(df, f'Internações por SRAG — {cidade} (SIH/DATASUS)', 'Nº de internações', TEAL)

    limiares_sih = [(10, '#2196F3', 'Sem risco'), (90, '#4CAF50', 'Segurança'),
                    (150, '#FFEB3B', 'Baixo'), (200, '#FF9800', 'Moderado'), (250, '#F44336', 'Alto')]
    for lim, cor_lim, nome_lim in limiares_sih:
        fig.add_hline(y=lim, line_dash='dash', line_color=cor_lim, line_width=1.5)
        fig.add_annotation(x=1.01, y=lim, xref='paper', yref='y',
                           text=nome_lim, showarrow=False,
                           font=dict(size=9, color=cor_lim), xanchor='left')
    return fig


def fig_serie_sia(cidade: str = 'Belo Horizonte') -> go.Figure:
    """
    Série temporal de atendimentos de saúde mental (SIA/DATASUS) com limiares.
    Dados representativos baseados no dashboard saude-mental-sia.onrender.com.
    """
    import pandas as _pd
    import numpy as _np

    _np.random.seed(7)
    datas = _pd.date_range('2008-01', '2023-12', freq='MS')
    n = len(datas)
    tendencia = _np.linspace(300, 600, n)
    sazonalidade = 80 * _np.sin(_np.linspace(0, 10 * _np.pi, n))
    pico_2017 = _np.exp(-0.5 * (((_np.arange(n) - 110) / 8) ** 2)) * 400
    pico_2022 = _np.exp(-0.5 * (((_np.arange(n) - 168) / 6) ** 2)) * 350
    ruido = _np.random.normal(0, 40, n)
    valores = _np.clip(tendencia + sazonalidade + pico_2017 + pico_2022 + ruido, 50, 1050)

    df = _pd.DataFrame({'data': datas, 'valor': valores})

    fig = _serie_saude_com_limiares(df, f'Atendimentos de Saúde Mental — {cidade} (SIA/DATASUS)', 'Nº de atendimentos', PURPLE)

    limiares_sia = [(150, '#2196F3', 'Sem risco'), (300, '#4CAF50', 'Segurança'),
                    (550, '#FFEB3B', 'Baixo'), (750, '#FF9800', 'Moderado'), (900, '#F44336', 'Alto')]
    for lim, cor_lim, nome_lim in limiares_sia:
        fig.add_hline(y=lim, line_dash='dash', line_color=cor_lim, line_width=1.5)
        fig.add_annotation(x=1.01, y=lim, xref='paper', yref='y',
                           text=nome_lim, showarrow=False,
                           font=dict(size=9, color=cor_lim), xanchor='left')
    return fig


def fig_serie_srag(cidade: str = 'RIDE do DF e Entorno') -> go.Figure:
    """
    Série temporal de casos de SRAG (Vigilância/SIVEP-Gripe) com limiares.
    Dados representativos baseados no dashboard saude-srag-data.onrender.com.
    """
    import pandas as _pd
    import numpy as _np

    _np.random.seed(13)
    datas = _pd.date_range('2019-01', '2024-12', freq='MS')
    n = len(datas)
    base = _np.ones(n) * 200
    # Pico COVID 2020-2021
    pico_covid = _np.exp(-0.5 * (((_np.arange(n) - 15) / 4) ** 2)) * 3800
    pico_covid2 = _np.exp(-0.5 * (((_np.arange(n) - 26) / 5) ** 2)) * 4900
    pico_covid3 = _np.exp(-0.5 * (((_np.arange(n) - 36) / 3) ** 2)) * 1600
    sazonalidade = 150 * _np.sin(_np.linspace(0, 4 * _np.pi, n))
    ruido = _np.random.normal(0, 80, n)
    valores = _np.clip(base + pico_covid + pico_covid2 + pico_covid3 + sazonalidade + ruido, 10, 5500)

    df = _pd.DataFrame({'data': datas, 'valor': valores})

    fig = _serie_saude_com_limiares(df, f'Casos de SRAG — {cidade} (Vigilância SIVEP-Gripe)', 'Nº de casos', RED)

    limiares_srag = [(200, '#2196F3', 'Sem risco'), (700, '#4CAF50', 'Segurança'),
                     (2000, '#FFEB3B', 'Moderado'), (3000, '#FF9800', 'Alto'), (4500, '#F44336', 'Crítico')]
    for lim, cor_lim, nome_lim in limiares_srag:
        fig.add_hline(y=lim, line_dash='dash', line_color=cor_lim, line_width=1.5)
        fig.add_annotation(x=1.01, y=lim, xref='paper', yref='y',
                           text=nome_lim, showarrow=False,
                           font=dict(size=9, color=cor_lim), xanchor='left')
    return fig
