"""
GeoCalor — Módulo de carregamento e pré-processamento de dados
Desenvolvimento: Diego Ricardo Xavier | OCS/ICICT/Fiocruz
"""

import gzip
import os
import pandas as pd
import numpy as np

DATA_PATH = os.path.join(os.path.dirname(__file__), '../../data/temp.csv.gz')

_df_cache = None


def load_data() -> pd.DataFrame:
    """Carrega e cacheia o dataset principal."""
    global _df_cache
    if _df_cache is not None:
        return _df_cache

    with gzip.open(DATA_PATH, 'rt') as f:
        df = pd.read_csv(f)

    # Padronizar índice de data
    df['date'] = pd.to_datetime(df['index'])
    df['month_name'] = df['date'].dt.strftime('%b')
    df['month_num'] = df['date'].dt.month
    df['day_of_year'] = df['date'].dt.dayofyear

    # Garantir tipos
    df['isHW'] = df['isHW'].astype(bool)
    df['year'] = df['year'].astype(int)

    # Ordenar cidades alfabeticamente (Belém primeiro para default)
    _df_cache = df.sort_values(['cidade', 'date']).reset_index(drop=True)
    return _df_cache


def get_cidades() -> list:
    df = load_data()
    return sorted(df['cidade'].unique().tolist())


def get_anos() -> list:
    df = load_data()
    return sorted(df['year'].unique().tolist())


def filter_df(cidade=None, ano=None, intensidade=None) -> pd.DataFrame:
    df = load_data()
    if cidade and cidade != 'Todas':
        df = df[df['cidade'] == cidade]
    if ano and ano != 'Todos':
        df = df[df['year'] == int(ano)]
    if intensidade and intensidade != 'Todas':
        df = df[df['HW_Intensity'] == intensidade]
    return df


# ── Estatísticas agregadas ──────────────────────────────────────────────────

def kpi_global() -> dict:
    df = load_data()
    return {
        'n_cidades': df['cidade'].nunique(),
        'n_anos': df['year'].nunique(),
        'n_registros': len(df),
        'dias_hw': int(df['isHW'].sum()),
        'ano_min': int(df['year'].min()),
        'ano_max': int(df['year'].max()),
    }


def kpi_cidade_ano(cidade: str, ano: int) -> dict:
    df = filter_df(cidade=cidade, ano=str(ano))
    hw = df[df['isHW']]
    return {
        'dias_hw': int(df['isHW'].sum()),
        'temp_max': round(float(df['tempMax'].max()), 1),
        'temp_med': round(float(df['tempMed'].mean()), 1),
        'umidade': round(float(df['HumidadeMed'].mean()), 1),
        'n_eventos': int(df['group'].max()) if df['group'].max() > 0 else 0,
        'ehf_max': round(float(df['EHF'].max()), 2),
    }


def heatmap_cidade_ano(metrica: str = 'dias_hw') -> pd.DataFrame:
    """Retorna pivot: cidades × anos com a métrica escolhida."""
    df = load_data()
    if metrica == 'dias_hw':
        piv = df.groupby(['cidade', 'year'])['isHW'].sum().reset_index()
        piv.columns = ['cidade', 'year', 'valor']
    elif metrica == 'temp_max':
        piv = df.groupby(['cidade', 'year'])['tempMax'].max().reset_index()
        piv.columns = ['cidade', 'year', 'valor']
    elif metrica == 'ehf_max':
        piv = df.groupby(['cidade', 'year'])['EHF'].max().reset_index()
        piv.columns = ['cidade', 'year', 'valor']
    else:
        piv = df.groupby(['cidade', 'year'])['isHW'].sum().reset_index()
        piv.columns = ['cidade', 'year', 'valor']
    return piv.pivot(index='cidade', columns='year', values='valor')


def polar_mensal(cidade: str) -> pd.DataFrame:
    """Frequência mensal de ondas de calor para gráfico polar."""
    df = filter_df(cidade=cidade)
    hw = df[df['isHW']]
    freq = hw.groupby('month_num').size().reset_index(name='count')
    meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    freq['mes'] = freq['month_num'].apply(lambda x: meses[x-1])
    # Garantir todos os meses
    full = pd.DataFrame({'month_num': range(1,13), 'mes': meses})
    freq = full.merge(freq, on=['month_num','mes'], how='left').fillna(0)
    return freq


def ranking_cidades(metrica: str = 'temp_med') -> pd.DataFrame:
    df = load_data()
    hw = df[df['isHW']]
    if metrica == 'temp_med':
        r = hw.groupby('cidade')['tempMed'].mean().reset_index()
        r.columns = ['cidade', 'valor']
        r['label'] = r['valor'].round(1).astype(str) + '°C'
    elif metrica == 'duracao':
        r = hw.groupby('cidade')['HW_duration'].mean().reset_index()
        r.columns = ['cidade', 'valor']
        r['label'] = r['valor'].round(1).astype(str) + ' dias'
    elif metrica == 'dias_hw':
        r = df.groupby('cidade')['isHW'].sum().reset_index()
        r.columns = ['cidade', 'valor']
        r['label'] = r['valor'].astype(str) + ' dias'
    return r.sort_values('valor', ascending=True)


def tendencia_anual(cidade: str) -> pd.DataFrame:
    """Tendência anual de dias de OC por cidade."""
    df = filter_df(cidade=cidade)
    t = df.groupby('year')['isHW'].sum().reset_index()
    t.columns = ['year', 'dias_hw']
    # Regressão linear simples
    if len(t) > 2:
        z = np.polyfit(t['year'], t['dias_hw'], 1)
        t['trend'] = np.polyval(z, t['year'])
    else:
        t['trend'] = t['dias_hw']
    return t


def anomalia_termica(cidade: str) -> pd.DataFrame:
    """Anomalia de temperatura média anual em relação à média histórica."""
    df = filter_df(cidade=cidade)
    anual = df.groupby('year')['tempMed'].mean().reset_index()
    baseline = anual['tempMed'].mean()
    anual['anomalia'] = anual['tempMed'] - baseline
    anual['cor'] = anual['anomalia'].apply(lambda x: 'pos' if x >= 0 else 'neg')
    return anual, baseline


def climatologia_diaria(cidade: str) -> pd.DataFrame:
    """Climatologia diária (média histórica por dia do ano)."""
    df = filter_df(cidade=cidade)
    clim = df.groupby('day_of_year').agg(
        tmax_clim=('tempMax', 'mean'),
        tmed_clim=('tempMed', 'mean'),
        tmin_clim=('tempMin', 'mean'),
    ).reset_index()
    return clim


def distribuicao_intensidade() -> pd.DataFrame:
    """Distribuição de dias de OC por intensidade e cidade."""
    df = load_data()
    hw = df[df['isHW']]
    r = hw.groupby(['cidade', 'HW_Intensity']).size().reset_index(name='count')
    return r


def sazonalidade_decadal(cidade: str) -> pd.DataFrame:
    """Frequência mensal de OC por década."""
    df = filter_df(cidade=cidade)
    df = df.copy()
    df['decada'] = (df['year'] // 10) * 10
    hw = df[df['isHW']]
    r = hw.groupby(['decada', 'month_num']).size().reset_index(name='count')
    meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    r['mes'] = r['month_num'].apply(lambda x: meses[x-1])
    return r


def eventos_extremos_tabela(cidade=None, ano_min=1981, ano_max=2023, intensidade=None) -> pd.DataFrame:
    """Tabela de eventos extremos por cidade."""
    df = load_data()
    if cidade and cidade != 'Todas':
        df = df[df['cidade'] == cidade]
    df = df[(df['year'] >= ano_min) & (df['year'] <= ano_max)]
    if intensidade and intensidade != 'Todas':
        df = df[df['HW_Intensity'] == intensidade]

    hw = df[df['isHW']]
    r = hw.groupby('cidade').agg(
        dias_oc=('isHW', 'sum'),
        n_ondas=('group', 'nunique'),
        temp_med=('tempMed', 'mean'),
        dur_med=('HW_duration', 'mean'),
        ehf_med=('EHF', 'mean'),
        temp_anom=('tempAnom', 'mean'),
    ).reset_index()
    r.columns = ['Cidade', 'Dias OC', 'Nº Ondas', 'Temp. Média (°C)', 'Duração Média', 'EHF Médio', 'Anomalia (°C)']
    r = r.round(2)
    return r.sort_values('Dias OC', ascending=False)


def mapa_dados() -> pd.DataFrame:
    """Dados para o mapa: total de dias de OC por cidade com lat/lon."""
    df = load_data()
    r = df.groupby('cidade').agg(
        dias_oc=('isHW', 'sum'),
        lat=('Lat', 'first'),
        lon=('Long', 'first'),
        temp_med=('tempMed', 'mean'),
    ).reset_index()
    return r
