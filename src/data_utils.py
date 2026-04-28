# src/data_utils.py
"""
Funções reutilizáveis de carregamento e limpeza de dados.
Extraídas de notebooks/01_limpeza_dados.ipynb para evitar duplicação.

Uso no notebook:
    import sys
    sys.path.append('..')          # sobe um nível até a raiz do projeto
    from src.data_utils import (
        carregar_snis,
        preparar_populacao_referencia,
        calcular_flags_evidencia,
        processar_saude,
        validar_populacao,
        analisar_municipio,
    )
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# 1. Carregamento
# ---------------------------------------------------------------------------

def carregar_snis(project_id: str, sigla_uf: str = 'ES', ano_min: int = 2006) -> pd.DataFrame:
    """
    Carrega dados do SNIS via BigQuery e retorna DataFrame bruto.

    Parâmetros
    ----------
    project_id : str
        ID do projeto no Google Cloud (ex: 'analise-saneamento').
    sigla_uf : str
        Sigla da UF a filtrar (padrão 'ES').
    ano_min : int
        Ano mínimo de corte (padrão 2006).

    Retorna
    -------
    pd.DataFrame com as colunas brutas do SNIS.
    """
    import pandas_gbq

    sql = f"""
    SELECT
      ano,
      id_municipio,
      sigla_uf,
      quantidade_economia_residencial_ativa_agua,
      quantidade_economia_residencial_ativa_esgoto,
      quantidade_ligacao_total_agua,
      quantidade_ligacao_total_esgoto,
      populacao_urbana,
      populacao_atendida_agua,
      indice_atendimento_total_agua,
      indice_atendimento_esgoto_agua,
      indice_atendimento_urbano_agua,
      indice_tratamento_esgoto,
      indice_perda_distribuicao_agua,
      indice_consumo_agua_per_capita,
      volume_esgoto_coletado,
      volume_esgoto_tratado,
      extensao_rede_agua,
      extensao_rede_esgoto,
      populacao_atentida_esgoto AS populacao_urbana_atendida_esgoto,
      quantidade_ligacao_ativa_esgoto,
      investimento_total_municipio,
      investimento_total_estado,
      investimento_total_prestador,
      despesa_exploracao,
      arrecadacao_total,
      receita_operacional
    FROM `basedosdados.br_mdr_snis.municipio_agua_esgoto`
    WHERE sigla_uf = '{sigla_uf}' AND ano >= {ano_min}
    """

    try:
        df = pandas_gbq.read_gbq(sql, project_id=project_id)
        print(f"✅ Dados do {sigla_uf} carregados: {df.shape}")
        return df
    except Exception as e:
        raise RuntimeError(f"Erro ao acessar a tabela de saneamento: {e}")


# ---------------------------------------------------------------------------
# 2. Limpeza de população
# ---------------------------------------------------------------------------

def preparar_populacao_referencia(df_base: pd.DataFrame) -> pd.DataFrame:
    """
    Imputa e interpola populacao_ref com fallback para populacao_atendida_agua.

    Reconstrói a coluna a partir das colunas-base para evitar estado
    inconsistente quando as células forem reexecutadas fora de ordem.

    Parâmetros
    ----------
    df_base : pd.DataFrame
        DataFrame contendo ao menos 'populacao_urbana' e 'populacao_atendida_agua'.

    Retorna
    -------
    pd.DataFrame com as colunas de população adicionadas/atualizadas.
    """
    df_base = df_base.copy().sort_values(['id_municipio', 'ano'])

    if 'populacao_ref_bruta' in df_base.columns:
        pop_base = df_base['populacao_ref_bruta']
    else:
        pop_base = df_base['populacao_urbana']

    df_base['populacao_urbana_limpa'] = pop_base
    df_base['populacao_urbana_era_nula'] = df_base['populacao_urbana_limpa'].isna()

    df_base['populacao_ref'] = df_base['populacao_urbana_limpa']
    mask_fallback = df_base['populacao_ref'].isna()
    df_base.loc[mask_fallback, 'populacao_ref'] = df_base.loc[mask_fallback, 'populacao_atendida_agua']

    df_base['populacao_usou_fallback_agua'] = (
        df_base['populacao_urbana_era_nula'] & df_base['populacao_atendida_agua'].notna()
    )

    df_base['fonte_populacao'] = np.where(
        df_base['populacao_urbana_limpa'].notna(),
        'urbana',
        np.where(
            df_base['populacao_atendida_agua'].notna(),
            'agua',
            'missing'
        )
    )

    # Nula = ainda nula após todos os fallbacks (para interpolação)
    df_base['populacao_ref_era_nula'] = df_base['populacao_ref'].isna()
    df_base['populacao_ref'] = df_base.groupby('id_municipio')['populacao_ref'].transform(
        lambda x: x.interpolate(method='linear', limit=2, limit_area='inside')
    )

    return df_base


# ---------------------------------------------------------------------------
# 3. Flags de evidência de esgoto
# ---------------------------------------------------------------------------

def calcular_flags_evidencia(df: pd.DataFrame):
    """
    Retorna (tem_rede, tem_trat_real) como Series booleanas.

    Recalcula a partir das colunas-base do df recebido.
    Evita estado global inconsistente quando células são reexecutadas fora de ordem.

    Parâmetros
    ----------
    df : pd.DataFrame

    Retorna
    -------
    tuple[pd.Series, pd.Series]
        (tem_rede, tem_trat_real)
    """
    evidencias_coleta = [c for c in [
        'extensao_rede_esgoto',
        'populacao_urbana_atendida_esgoto',
        'quantidade_ligacao_ativa_esgoto'
    ] if c in df.columns]

    evidencias_tratamento = [c for c in ['volume_esgoto_tratado'] if c in df.columns]

    tem_rede = (
        df[evidencias_coleta].fillna(0).gt(0).any(axis=1)
        if evidencias_coleta else pd.Series(False, index=df.index)
    )
    tem_trat_real = (
        df[evidencias_tratamento].fillna(0).gt(0).any(axis=1)
        if evidencias_tratamento else pd.Series(False, index=df.index)
    )

    return tem_rede, tem_trat_real


# ---------------------------------------------------------------------------
# 4. Integração com DATASUS/TabNet
# ---------------------------------------------------------------------------

def processar_saude(arquivo: str, nome_metrica: str) -> pd.DataFrame:
    """
    Carrega e limpa CSV do TabNet (DATASUS), retorna long format.

    Detecta dinamicamente a faixa útil de dados e evita dependência de
    skipfooter fixo, que não funciona com engine='c'.

    Parâmetros
    ----------
    arquivo : str
        Caminho para o CSV exportado do TabNet (separador ';', ISO-8859-1).
    nome_metrica : str
        Nome da coluna de valor a criar (ex: 'internacoes_agua').

    Retorna
    -------
    pd.DataFrame com colunas ['id_municipio_6', 'ano', nome_metrica].
    """
    df_raw = pd.read_csv(
        arquivo,
        sep=';',
        encoding='iso-8859-1',
        header=None,
        dtype=str
    )

    col0 = df_raw.iloc[:, 0].fillna('').astype(str).str.strip()
    mask_id = col0.str.match(r'^\d{6,}')

    if not mask_id.any():
        raise ValueError(f'Não foi possível identificar linhas de municípios em {arquivo}.')

    primeiro_dado = int(mask_id.idxmax())
    inicio = max(primeiro_dado - 1, 0)  # linha de cabeçalho logo antes do primeiro município

    apos_primeiro = col0.iloc[primeiro_dado + 1:]
    mask_fim = ~apos_primeiro.str.match(r'^\d{6,}')

    # idxmax() retornaria o PRIMEIRO True, mas nonzero() torna a intenção explícita:
    # queremos parar na primeira linha que NÃO seja um município válido
    # (ex: rodapé "Total", linha vazia, nota de rodapé).
    # Se todas as linhas forem municípios válidos, usamos len(df_raw) como sentinela.
    indices_fim = mask_fim.to_numpy().nonzero()[0]
    fim = int(apos_primeiro.index[indices_fim[0]]) if len(indices_fim) > 0 else len(df_raw)

    nrows = max(fim - inicio - 1, 1)

    df_s = pd.read_csv(
        arquivo,
        sep=';',
        encoding='iso-8859-1',
        skiprows=inicio,
        nrows=nrows
    )

    df_s = df_s.drop(columns=['Total', 'total'], errors='ignore')
    col_mun = df_s.columns[0]
    df_s = df_s[df_s[col_mun].astype(str).str.extract(r'^(\d{6})')[0].notna()].copy()

    df_long = df_s.melt(
        id_vars=[col_mun],
        var_name='ano_bruto',
        value_name=nome_metrica
    )

    df_long['id_municipio_6'] = df_long[col_mun].astype(str).str.extract(r'^(\d{6})')[0].str.strip()
    df_long['ano'] = pd.to_numeric(
        df_long['ano_bruto'].astype(str).str.extract(r'(\d{4})')[0], errors='coerce'
    )

    # Conversão robusta de contagem (formato brasileiro com ponto como milhar)
    df_long[nome_metrica] = (
        df_long[nome_metrica]
        .astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .str.strip()
        .replace({'-': None, '': None, 'nan': None})
    )
    df_long[nome_metrica] = pd.to_numeric(df_long[nome_metrica], errors='coerce')

    df_limpo = df_long.dropna(subset=['ano', 'id_municipio_6']).copy()
    df_limpo['ano'] = df_limpo['ano'].astype(int)
    df_limpo[nome_metrica] = df_limpo[nome_metrica].fillna(0)

    return df_limpo[['id_municipio_6', 'ano', nome_metrica]]


# ---------------------------------------------------------------------------
# 5. Validação de qualidade da população
# ---------------------------------------------------------------------------

def validar_populacao(df: pd.DataFrame):
    """
    Valida qualidade da coluna populacao_ref e retorna relatório + df anotado.

    Parâmetros
    ----------
    df : pd.DataFrame com colunas 'id_municipio', 'ano', 'populacao_ref'.

    Retorna
    -------
    tuple[dict, pd.DataFrame]
        (relatorio, df_anotado)
        - relatorio: dicionário com DataFrames de cada categoria de problema.
        - df_anotado: df original enriquecido com colunas auxiliares de diagnóstico.
    """
    df = df.sort_values(['id_municipio', 'ano']).copy()
    relatorio = {}

    # 1. Valores inválidos
    invalidos = df[df['populacao_ref'].isna() | (df['populacao_ref'] <= 0)]
    relatorio['valores_invalidos'] = invalidos

    # 2. Crescimento ano a ano (%)
    df['populacao_anterior'] = df.groupby('id_municipio')['populacao_ref'].shift(1)
    df['crescimento_pct'] = (
        (df['populacao_ref'] - df['populacao_anterior']) / df['populacao_anterior']
    ) * 100
    relatorio['crescimento_absurdo'] = df[df['crescimento_pct'].abs() > 20]

    # 3. Outliers (z-score por município via transform vetorizado)
    df['outlier'] = df.groupby('id_municipio', group_keys=False)['populacao_ref'].transform(
        lambda s: ((s - s.mean()) / s.std()).abs().gt(3)
        if pd.notna(s.std()) and s.std() != 0
        else pd.Series(False, index=s.index)
    )
    relatorio['outliers'] = df[df['outlier']]

    # 4. Saltos absolutos grandes
    df['delta_abs'] = (df['populacao_ref'] - df['populacao_anterior']).abs()
    relatorio['saltos_grandes'] = df[df['delta_abs'] > df['populacao_ref'] * 0.15]

    # 5. Lacunas originalmente imputadas
    if 'populacao_ref_era_nula' in df.columns:
        relatorio['valores_imputados'] = df[df['populacao_ref_era_nula']]
    else:
        relatorio['valores_imputados'] = df.iloc[0:0].copy()

    print("\n📊 RELATÓRIO DE VALIDAÇÃO DA POPULAÇÃO\n")
    print(f"❌ Valores inválidos: {len(relatorio['valores_invalidos'])}")
    print(f"📈 Crescimentos suspeitos (>20%): {len(relatorio['crescimento_absurdo'])}")
    print(f"📊 Outliers estatísticos: {len(relatorio['outliers'])}")
    print(f"⚠️ Saltos absolutos grandes: {len(relatorio['saltos_grandes'])}")
    print(f"🩹 Valores imputados/interpolados: {len(relatorio['valores_imputados'])}")

    # Apelidos e coluna adicional para células de classificação posteriores usarem sem recalcular
    df['pop_ant'] = df['populacao_anterior']
    df['pop_prox'] = df.groupby('id_municipio')['populacao_ref'].shift(-1)

    return relatorio, df


# ---------------------------------------------------------------------------
# 6. Diagnóstico por município
# ---------------------------------------------------------------------------

def analisar_municipio(df: pd.DataFrame, municipio_id) -> None:
    """
    Exibe série temporal de populacao_ref com crescimento % para um município.

    Parâmetros
    ----------
    df : pd.DataFrame retornado por validar_populacao (contém 'crescimento_pct').
    municipio_id : str | int
        Código do município (6 ou 7 dígitos).
    """
    df_m = df[df['id_municipio'].astype(str) == str(municipio_id)].sort_values('ano')

    print(df_m[['ano', 'populacao_ref', 'crescimento_pct']])

    plt.plot(df_m['ano'], df_m['populacao_ref'], marker='o')
    plt.title(f"Município {municipio_id}")
    plt.grid()
    plt.show()
