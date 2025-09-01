import os
import pandas as pd
from fuzzywuzzy import process, fuzz
from unidecode import unidecode
import psycopg2

db_params = {
    "database": "sigplus",
    "user": "postgres",
    "host": "localhost",
    "password": os.getenv("POSTGRES_PASSWORD"),
    "port": "5432"
}

rhSheetPath = "files/RH users.xlsx"
tiSheetPath = "files/TI users.xlsx"

emailGroups = [
    "Acesso Sindicato", "ACPL Impressão", "almoxarifado", "Automação  MVV", "Balança - MVV", "Barragem", "Bombeiro Civil",
    "Central de Segurança Patrimonial", "CMD", "Comunicação Interna", "Contato MVV", "Defensoria  AL", "Despacho MVV", "EUAX", "Ged MVV",
    "GLPI SML", "Guardião  Barragem", "Imprensa", "Intune Mvv", "Multiservi", "MVV  - Licenças TI", "MVV  Notas Fiscais",
    "MVV - Arquivos Engenharia", "MVV - CIPAMIN", "MVV - Clipping", "MVV - diligenciamento", "MVV - Fale Conosco", "MVV - Fortinet",
    "MVV - Oficio MASF", "MVV - Portaria Patrimonial", "MVV - Refeitório", "MVV - Sala Alagoas", "MVV - Sala Craíbas", "MVV - Sigmin - Atendimento",
    "MVV - SIGMIN E-mail Testes", "MVV - SIGMINA", "MVV - Supervisão Patrimonial", "MVV - TI", "MVV Sigmin Informe", "MVV Sistemas", "MVV Teste SSMA,",
    "Painel GPP", "Painel PCM", "Patrimonial Apps", "PCP PLANTA", "PMO", "PMO Impressão", "Port Images", "QSOFT", "Refeitório MVV",
    "Roda Com Elas", "Room Meeting - MVV", "Saneamento", "sefaz", "Segurança da Informação", "SGS Geosol", "SIGMIN", "Sso Sistemas",
    "Suporte RICC", "support Backup", "Teste5 ACG", "Topografia", "treinamento", "Modelo Analista Fiscal", "Prontuário Instalações Elétricas"
]

def normalizeName(name):
    name = unidecode(name)
    name = name.upper()
    return name

def load_normalized_data():
    dfRHRaw = pd.read_excel(rhSheetPath)
    dfTIRaw = pd.read_excel(tiSheetPath)
    dfTIRaw = dfTIRaw[~dfTIRaw["Nome para exibição"].isin(emailGroups)]
    dfRHRaw["Data Admissão"] = pd.to_datetime(dfRHRaw["Data Admissão"], errors='coerce')
    dfRHRaw.Nome = dfRHRaw.Nome.apply(normalizeName)
    dfTIRaw["Nome para exibição"] = dfTIRaw["Nome para exibição"].apply(normalizeName)
    return dfTIRaw, dfRHRaw

def get_dataframes():
    tiDFProcessed, rhDFProcessed = load_normalized_data()
    confirmedMatches = pd.merge(
        tiDFProcessed, rhDFProcessed, how="inner",
        left_on="Nome para exibição", right_on="Nome"
    )
    confirmedMatches = confirmedMatches[
        [
            "Estabelecimento", "Matrícula", "Nome", "Nome UPN", "Data Admissão", "Cargo Básico", "Nível Cargo",
            "Cargo Básico-Descrição", "Unid Lotação", "Unid Lotação-Descrição", "Unid Negócio", "Unid Negócio-Descrição",
            "Centro Custo", "Centro Custo-Descrição", "Supervisor", "Coordenador", "Gerente"
        ]
    ].rename(columns={
        "Estabelecimento": "estabelecimento", "Matrícula": "matricula", "Nome": "nome", "Nome UPN": "email",
        "Data Admissão": "data_admissao", "Cargo Básico": "cargo_basico", "Nível Cargo": "nivel_cargo",
        "Cargo Básico-Descrição": "cargo_basico_descricao", "Unid Lotação": "unid_lotacao",
        "Unid Lotação-Descrição": "unid_lotacao_descricao", "Unid Negócio": "unid_negocio",
        "Unid Negócio-Descrição": "unid_negocio_descricao", "Centro Custo": "centro_custo",
        "Centro Custo-Descrição": "centro_custo_descricao", "Supervisor": "supervisor",
        "Coordenador": "coordenador", "Gerente": "gerente"
    })
    tiDFProcessed = tiDFProcessed[~tiDFProcessed['Nome para exibição'].isin(confirmedMatches['nome'])]
    rhDFProcessed = rhDFProcessed[~rhDFProcessed['Nome'].isin(confirmedMatches['nome'])]
    return confirmedMatches, tiDFProcessed, rhDFProcessed

def get_possible_matches(tiDFProcessed, rhDFProcessed):
    matches = []
    tiNoMatches = []
    rh_names = rhDFProcessed['Nome'].tolist()
    for _, ti_row in tiDFProcessed.iterrows():
        ti_name = ti_row['Nome para exibição']
        ti_first_name = ti_name.split()[0] if ti_name.split() else ""
        possible_matches = process.extract(ti_name, rh_names, scorer=fuzz.WRatio, limit=3)
        filtered_matches = [
            name for name, _ in possible_matches
            if name.split()[0] == ti_first_name
        ]
        if filtered_matches:
            for match_name in filtered_matches:
                rh_row = rhDFProcessed[rhDFProcessed['Nome'] == match_name].iloc[0]
                merged_row = pd.concat([ti_row, rh_row], axis=0)
                matches.append(merged_row)
        else:
            tiNoMatches.append(ti_row)
    matches_df = pd.DataFrame(matches)
    tiNoMatches_df = pd.DataFrame(tiNoMatches)
    return matches_df, tiNoMatches_df

def insert_matches_to_database(confirmed_rows, confirmed_matches):
    df_rows = pd.DataFrame(confirmed_rows)
    df_rows = df_rows[
        [
            'Estabelecimento', 'Matrícula', 'Nome', 'Nome UPN', 'Data Admissão', 'Cargo Básico', 'Nível Cargo',
            'Cargo Básico-Descrição', 'Unid Lotação', 'Unid Lotação-Descrição', 'Unid Negócio', 'Unid Negócio-Descrição',
            'Centro Custo', 'Centro Custo-Descrição', 'Supervisor', 'Coordenador', 'Gerente'
        ]
    ]
    df_rows.columns = confirmed_matches.columns
    df_database = pd.concat([df_rows, confirmed_matches], axis=0)
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        for _, row in df_database.iterrows():
            cursor.execute("""
                INSERT INTO public.user_email (
                    estabelecimento, matricula, nome, data_admissao, cargo_basico, nivel_cargo,
                    cargo_basico_descricao, unid_lotacao, unid_lotacao_descricao, unid_negocio, unid_negocio_descricao,
                    centro_custo, centro_custo_descricao, supervisor, coordenador, gerente, email, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['estabelecimento'], row['matricula'], row['nome'], row['data_admissao'], row['cargo_basico'], row['nivel_cargo'],
                row['cargo_basico_descricao'], row['unid_lotacao'], row['unid_lotacao_descricao'], row['unid_negocio'],
                row['unid_negocio_descricao'], row['centro_custo'], row['centro_custo_descricao'], row['supervisor'],
                row['coordenador'], row['gerente'], row['email'], "ativo"
            ))
        conn.commit()
    except Exception as e:
        print(f"Error inserting matches to database: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    confirmedMatches, tiDFProcessed, rhDFProcessed = get_dataframes()
    print(confirmedMatches)
