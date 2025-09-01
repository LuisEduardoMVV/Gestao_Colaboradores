import streamlit as st
from logic import get_dataframes, get_possible_matches, insert_matches_to_database

confirmedMatches, tiDFProcessed, rhDFProcessed = get_dataframes()
matches_df, tiNoMatches_df = get_possible_matches(tiDFProcessed, rhDFProcessed)

if 'matches_confirmed' not in st.session_state:
    st.session_state.matches_confirmed = confirmedMatches

if 'possible_matches' not in st.session_state:
    st.session_state.possible_matches = matches_df

if 'not_matched' not in st.session_state:
    st.session_state.not_matched = tiNoMatches_df

st.title("Gestão de colaboradores")

st.subheader("Matches Confirmados")
st.write(confirmedMatches)

st.subheader("Possíveis Matches")
checked_indices = []

with st.form("form_possible_matches"):
    for idx, row in st.session_state.possible_matches.iterrows():
        cols = st.columns([3, 3, 1.5])
        cols[0].write(row["Nome para exibição"])
        cols[1].write(row["Nome"])
        checked = cols[2].checkbox("Confirmar", key=f"check_{idx}")
        if checked:
            checked_indices.append(idx)
    submitted = st.form_submit_button("Confirmar Selecionados")

if submitted and checked_indices:
    confirmed_rows = st.session_state.possible_matches.loc[checked_indices]
    insert_matches_to_database(confirmed_rows, confirmedMatches)
    st.success(f"{len(checked_indices)} matches confirmados com sucesso!\nLinhas inseridas no banco de dados.")

    st.session_state.possible_matches = st.session_state.possible_matches.drop(checked_indices).reset_index(drop=True)