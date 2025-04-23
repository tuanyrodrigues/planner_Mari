import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import calendar

# Configuração do idioma
dias_semana_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

# Funções para carregar/salvar alunos e treinos
def carregar_alunos():
    try:
        with open('alunos_dias_fixos.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_alunos(alunos):
    with open('alunos_dias_fixos.json', 'w') as f:
        json.dump(alunos, f, indent=4)

def carregar_treinos():
    try:
        with open('treinos_alunos.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_treinos(treinos):
    with open('treinos_alunos.json', 'w') as f:
        json.dump(treinos, f, indent=4)

st.set_page_config(page_title="Agenda Mariana Belotto", page_icon="📅", layout="wide")
st.title("📅 Agenda Mariana Belotto")
st.write("Clique em um dia para ver os alunos com treino e seus respectivos treinos.")

# Carregar dados
alunos = carregar_alunos()
treinos = carregar_treinos()

# Cadastro de aluno
with st.expander("👤 Cadastrar Aluno"):
    nome_aluno = st.text_input("Nome do Aluno")
    dias_fixos = st.multiselect("Dias fixos do treino", dias_semana_pt)
    if st.button("Salvar Aluno"):
        if nome_aluno:
            alunos[nome_aluno] = dias_fixos
            salvar_alunos(alunos)
            st.success(f"Aluno {nome_aluno} salvo com sucesso!")

# Excluir aluno existente
with st.expander("Excluir Aluno"):
    if alunos:
        aluno_para_excluir = st.selectbox("Selecione o aluno que deseja excluir", list(alunos.keys()))
        if st.button("Excluir Aluno"):
            if aluno_para_excluir in alunos:
                del alunos[aluno_para_excluir]
                treinos.pop(aluno_para_excluir, None)  # remove os treinos também se houver
                salvar_alunos(alunos)
                salvar_treinos(treinos)
                st.success(f"Aluno {aluno_para_excluir} excluído com sucesso!")
    else:
        st.info("Nenhum aluno cadastrado ainda.")

# Cadastro de treino
with st.expander("🏋️‍♀️ Cadastrar Treino Personalizado"):
    aluno_selecionado = st.selectbox("Selecione o Aluno", list(alunos.keys()) or [""])
    if aluno_selecionado:
        dia_escolhido = st.selectbox("Dia da Semana", dias_semana_pt)
        treino_texto = st.text_area("Digite o treino:")
        if st.button("Salvar Treino"):
            if aluno_selecionado not in treinos:
                treinos[aluno_selecionado] = {}
            treinos[aluno_selecionado][dia_escolhido] = treino_texto
            salvar_treinos(treinos)
            st.success(f"Uhuuuul!!! Treino de {aluno_selecionado} na {dia_escolhido} salvo com sucesso!")

# Navegação do calendário
st.subheader("🗓️ Calendário")
meses = list(calendar.month_name)[1:]
anos = list(range(datetime.now().year, 2026))
col1, col2 = st.columns(2)
with col1:
    mes = st.selectbox("Mês", meses, index=datetime.now().month - 1)
with col2:
    ano = st.selectbox("Ano", anos, index=0)

mes_num = meses.index(mes) + 1
primeiro_dia = datetime(ano, mes_num, 1)
ultimo_dia = datetime(ano, mes_num, calendar.monthrange(ano, mes_num)[1])

# Geração do calendário
dias_do_mes = [primeiro_dia + timedelta(days=i) for i in range((ultimo_dia - primeiro_dia).days + 1)]
tabela_calendario = pd.DataFrame(columns=dias_semana_pt)
linha = []

for dia in dias_do_mes:
    nome_dia = dias_semana_pt[dia.weekday()]
    linha.append((dia.strftime("%d/%m"), nome_dia))

# Montar calendário formatado
semana = []
matriz = []
for data, nome_dia in linha:
    while len(semana) < dias_semana_pt.index(nome_dia):
        semana.append("")
    semana.append(data)
    if len(semana) == 7:
        matriz.append(semana)
        semana = []
if semana:
    while len(semana) < 7:
        semana.append("")
    matriz.append(semana)

df_cal = pd.DataFrame(matriz, columns=dias_semana_pt)
st.dataframe(df_cal, use_container_width=True)

# Seleção de dia e exibição de treinos
dias_validos = [data for data, _ in linha]
dia_selecionado = st.selectbox("Escolha o dia (DD/MM):", dias_validos)

if dia_selecionado:
    data_obj = datetime.strptime(f"{dia_selecionado}/{ano}", "%d/%m/%Y")
    nome_dia_semana = dias_semana_pt[data_obj.weekday()]

    alunos_do_dia = [a for a, dias in alunos.items() if nome_dia_semana in dias]
    if alunos_do_dia:
        st.subheader(f"Alunos com treino na {nome_dia_semana}, dia {dia_selecionado}")
        for aluno in alunos_do_dia:
            treino = treinos.get(aluno, {}).get(nome_dia_semana, "Treino não cadastrado :( ")
            with st.expander(f"📌 {aluno}"):
                st.write(treino)
    else:
        st.info(f"Nenhum aluno com treino cadastrado para {nome_dia_semana}.")

