import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
import json
from datetime import datetime, timedelta

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
with st.expander("🗑️ Excluir Aluno"):
    if alunos:
        aluno_para_excluir = st.selectbox("Selecione o aluno que deseja excluir", list(alunos.keys()))
        if st.button("Excluir Aluno"):
            if aluno_para_excluir in alunos:
                del alunos[aluno_para_excluir]
                treinos.pop(aluno_para_excluir, None)
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
        repeticao = st.selectbox("Repetir treino", ["Nunca", "Semanal", "Quinzenal", "Mensal"])
        if st.button("Salvar Treino"):
            if aluno_selecionado not in treinos:
                treinos[aluno_selecionado] = {}
            if dia_escolhido not in treinos[aluno_selecionado]:
                treinos[aluno_selecionado][dia_escolhido] = []
            treinos[aluno_selecionado][dia_escolhido].append({
                "treino": treino_texto,
                "repeticao": repeticao,
                "inicio": datetime.today().strftime("%Y-%m-%d")
            })
            salvar_treinos(treinos)
            st.success(f"Uhuuuul!!! Treino de {aluno_selecionado} na {dia_escolhido} salvo com sucesso!")

# Geração dos eventos para o calendário
eventos = []
data_inicio = datetime(datetime.now().year, 1, 1)
data_fim = datetime(datetime.now().year + 1, 1, 1)
dias_range = pd.date_range(start=data_inicio, end=data_fim)

for aluno, dias_fixos in alunos.items():
    treinos_aluno = treinos.get(aluno, {})
    for dia in dias_range:
        nome_dia = dias_semana_pt[dia.weekday()]
        if nome_dia in dias_fixos:
            treinos_dia = treinos_aluno.get(nome_dia, [])
            for item in treinos_dia:
                inicio_treino = datetime.strptime(item["inicio"], "%Y-%m-%d")
                diff = (dia - inicio_treino).days
                repetir = item["repeticao"]
                mostrar = False
                if repetir == "Nunca" and dia.date() == inicio_treino.date():
                    mostrar = True
                elif repetir == "Semanal" and diff % 7 == 0 and diff >= 0:
                    mostrar = True
                elif repetir == "Quinzenal" and diff % 14 == 0 and diff >= 0:
                    mostrar = True
                elif repetir == "Mensal" and dia.day == inicio_treino.day and dia >= inicio_treino:
                    mostrar = True
                if mostrar:
                    eventos.append({
                        "title": aluno,
                        "start": dia.strftime("%Y-%m-%d"),
                        "end": dia.strftime("%Y-%m-%d"),
                        "extendedProps": {
                            "treino": item["treino"]
                        }
                    })

# Calendário visual
st.subheader("🗓️ Visualização do Calendário")
cal_config = {
    "initialView": "dayGridMonth",
    "locale": "pt-br",
    "eventClick": {
        "enabled": True,
        "callback": "alert(info.event.extendedProps.treino);"
    },
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek"
    }
}

calendar(events=eventos, options=cal_config)
