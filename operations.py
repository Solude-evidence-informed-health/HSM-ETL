import pandas as pd
import numpy as np
from icecream import ic


#MESES = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
LISTA_COLUNAS_ESSENCIAIS = [
    'MICROORGANISMO/CULTURA',
    'TOPOGRAFIA',
    'DATA'
    ]
LISTA_COLUNAS_DROPAR = [
    'PACIENTE',
    'CHSM',
    'SETOR',
    'LEITO',
    'ufcCS',
    'DATA'
    ]
VARIACOES_ERRADAS = [
    'MECANISMO DE RESISTÊNCIA',
    'MECANISMO DE RESISTÊNCIA ',
    'MECANISMO \nDE RESISTÊNCIA',
    'MECANISMO \nDE RESISTÊNCIA ',
]
DICT_COLUNAS_RENOMEAR = {
    'MICROORGANISMO/CULTURA': 'microrganismo',
    'TOPOGRAFIA': 'sitio'
    }
LISTA_COLUNAS_NAO_ANTIBIOTICOS = [
    'ano',
    'semestre',
    'microrganismo',
    'sitio'
    ]
DICT_COLUNAS_AJUSTADAS = {
    'antb': 'Antibiótico',
    'microrganismo': 'Microrganismo',
    'sitio': 'sítio',
    'ano': 'Ano',
    'semestre': 'periodo',
    'n_amostra': 'n_amostra',
    'n_sensivel': 'n_sensivel',
    'sensibilidade': 'Sensibilidade',
}

        
def verificar_e_dropar_nulos(df):
    ic("Executando etapa de verificação e dropagem de nulos...")
    try:
        # Verificar se há dados nulos e em quais colunas
        for coluna_essencial in LISTA_COLUNAS_ESSENCIAIS:
            value = df[coluna_essencial].isnull()
            ic(f"Coluna {coluna_essencial} possui dados nulos? {value.any()}")
            if value.sum() > 0:
                ic(f"Dados nulos em {coluna_essencial}: {value.sum()}")

        # Dataframe com dados nulos apenas nas colunas essenciais
        df_nulo = pd.DataFrame()
        for coluna_essencial in LISTA_COLUNAS_ESSENCIAIS:
            df_nulo = pd.concat([df_nulo, df.loc[df[coluna_essencial].isnull()]], ignore_index=True)
        df_nulo.drop_duplicates(inplace=True)
        df_nulo.reset_index(drop=True, inplace=True)
        ic(len(df_nulo))

        # Dataframe sem dados nulos apenas nas colunas essenciais
        df_nao_nulo = df.dropna(subset=LISTA_COLUNAS_ESSENCIAIS)
        df_nao_nulo.reset_index(drop=True, inplace=True)
        ic(len(df_nao_nulo))
    except Exception as e:
        ic('Erro ao verificar e dropar nulos: ', e)
        exit()
    return df_nao_nulo, df_nulo
        

def tratamentos_especificos_de_inconsistencias(df):
    ic("Executando etapa de tratamentos específicos de inconsistências...")
    ic(len(df))   
    try:
        df_inconsistencias = pd.DataFrame()
    except Exception as e:
        ic('Erro ao criar dataframe de inconsistências: ', e)
        exit()
    return df, df_inconsistencias


def criar_colunas_ano_e_semestre(df):
    ic("Executando etapa de criação de colunas de ano e semestre...")
    ic(len(df))
    ic(df.info())
    try:
        df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
        df['ano'] = df['DATA'].dt.year.astype(int)
        df['semestre'] = df['DATA'].dt.quarter.astype(int)
        df['semestre'] = df['semestre'].apply(lambda x: 1 if x<=2 else 2)
    except Exception as e:
        ic('Erro ao criar colunas de ano e semestre: ', e)
        exit()
    return df
    

def dropar_e_renomear_colunas(df):
    ic("Executando etapa de dropagem e renomeação de colunas...")
    ic(len(df))
    ic(df.info())
    try:
        df.drop(columns=LISTA_COLUNAS_DROPAR, inplace=True)
        for varicao_errada in VARIACOES_ERRADAS:
            try:
                df.drop(columns=varicao_errada, inplace=True)
            except:
                pass
        df.rename(columns=DICT_COLUNAS_RENOMEAR, inplace=True)
        # drop any column with the name 'Unnamed' in it
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    except Exception as e:
        ic('Erro ao dropar e renomear colunas: ', e)
        exit()
    return df
    

def traduzir_e_agrupar_terminologias(df, df_terminologias):
    ic("Executando etapa de tradução e agrupamento de terminologias...")
    ic(len(df))
    ic(df.info())
    try:
        dict_terminologias = df_terminologias.set_index('Antigo').to_dict()['Novo']
        df['microrganismo'] = df['microrganismo'].apply(lambda x: dict_terminologias[x] if x in dict_terminologias.keys() else x)
        # é preciso transformar para excel?
        df_traduzido = df.copy()
    except Exception as e:
        ic('Erro ao traduzir e agrupar terminologias: ', e)
        exit()
    return df_traduzido, df


def extrair_lista_de_antibioticos(df):
    ic("Executando etapa de extração de lista de antibióticos...")
    ic(len(df))
    ic(df.info())
    try:
        lista_colunas_antibioticos = []
        for coluna in df.columns:
            if coluna not in LISTA_COLUNAS_NAO_ANTIBIOTICOS:
                lista_colunas_antibioticos.append(coluna)
        ic(lista_colunas_antibioticos)
    except Exception as e:
        ic('Erro ao extrair lista de antibióticos: ', e)
        exit()
    return lista_colunas_antibioticos
                

def trasformacao_de_formato(lista_colunas_antibioticos, df):
    ic("Executando etapa de criação de dataframe transformado...")
    ic(len(df))
    ic(df.info())
    df_transformado = pd.DataFrame()
    try:
        for index, linha in df.iterrows():
            amostras_total = 0
            amostras_sensiveis = 0            
            for coluna in lista_colunas_antibioticos:
                if linha[coluna] == 'S':
                    amostras_total = amostras_total + 1
                    amostras_sensiveis = amostras_sensiveis + 1
                elif linha[coluna] == 'R':
                    amostras_total = amostras_total + 1
            for coluna in lista_colunas_antibioticos:
                if linha[coluna] == 'S' or linha[coluna] == 'R':
                    temp_df = df.loc[df.index == index][LISTA_COLUNAS_NAO_ANTIBIOTICOS].copy()
                    temp_df['antb'] = coluna
                    temp_df['n_amostra'] = amostras_total
                    temp_df['n_sensivel'] = amostras_sensiveis
                    temp_df['sensibilidade'] = round(amostras_sensiveis/amostras_total, 2)
                    temp_df['sensibilidade'] = temp_df['sensibilidade'] * 100
                    df_transformado = pd.concat([df_transformado, temp_df], ignore_index=True)
        df_transformado.reset_index(drop=True, inplace=True)
    except Exception as e:
        ic('Erro ao criar dataframe transformado: ', e)
        exit()
    return df_transformado


def ajuste_de_nomes_e_colunas(df):
    ic("Executando etapa de ajuste de nomes e colunas...")
    ic(len(df))
    ic(df.info())
    # renomear colunas segundo dict_de_colunas
    df = df.rename(columns=DICT_COLUNAS_AJUSTADAS)
    # Apenas a primeira letra maiuscula em cada texto
    df['Microrganismo'] = df['Microrganismo'].str.title()
    df['Antibiótico'] = df['Antibiótico'].str.title()
    df['sítio'] = df['sítio'].str.title()
    # ajustar periodo
    df['periodo'] = df['periodo'].apply(lambda x: '1º sem.' if x==1 else '2º sem.')
    df['periodo'] = df['periodo'] + " de " + df['Ano'].astype(str)
    lista_de_valores_de_dict_colunas_ajustadas = list(DICT_COLUNAS_AJUSTADAS.values())
    df = df.loc[:, lista_de_valores_de_dict_colunas_ajustadas].copy()
    return df, df