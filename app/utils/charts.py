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
