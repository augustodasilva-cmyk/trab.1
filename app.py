import os
import json
import re
import time
from collections import defaultdict

import streamlit as st
from groq import Groq

st.set_page_config(page_title="Professor Einstein", page_icon="📚")

# =========================
# API KEY
# =========================
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Configure sua GROQ_API_KEY nos Secrets do Streamlit.")
    st.stop()

client = Groq(api_key=api_key)

# =========================
# ESTADO
# =========================
if "pontuacao" not in st.session_state:
    st.session_state.pontuacao = 0
    st.session_state.acertos = 0
    st.session_state.erros = 0
    st.session_state.questao = None
    st.session_state.resposta = None
    st.session_state.inicio = None

# =========================
# FUNÇÃO IA
# =========================
def gerar_questao(tema, dificuldade):
    prompt = f"""
Crie uma questão de vestibular de História sobre: {tema}
Dificuldade: {dificuldade}

Formato JSON:
{{
"pergunta": "...",
"alternativas": {{
"A": "...",
"B": "...",
"C": "...",
"D": "..."
}},
"gabarito": "A",
"explicacao": "..."
}}
"""

    resposta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    texto = resposta.choices[0].message.content
    return json.loads(texto)

# =========================
# UI
# =========================
st.title("📚 Professor Einstein")

tema = st.text_input("Tema")
dificuldade = st.selectbox("Dificuldade", ["fácil", "média", "difícil"])
tempo_limite = st.slider("Tempo (segundos)", 10, 120, 30)

if st.button("Gerar questão"):
    st.session_state.questao = gerar_questao(tema, dificuldade)
    st.session_state.inicio = time.time()
    st.session_state.resposta = None

q = st.session_state.questao

if q:
    tempo = int(time.time() - st.session_state.inicio)
    st.info(f"⏱️ Tempo: {tempo}s")

    st.write(q["pergunta"])

    st.session_state.resposta = st.radio(
        "Escolha:",
        ["A", "B", "C", "D"],
        format_func=lambda x: f"{x}) {q['alternativas'][x]}"
    )

    if st.button("Corrigir"):
        tempo_total = int(time.time() - st.session_state.inicio)
        certo = st.session_state.resposta == q["gabarito"]

        if certo:
            st.success("✅ Correto!")
            st.session_state.acertos += 1
            pontos = 20
            if tempo_total < 15:
                pontos += 10
            st.session_state.pontuacao += pontos
        else:
            st.error(f"❌ Errado! Gabarito: {q['gabarito']}")
            st.session_state.erros += 1

        st.write("Explicação:")
        st.write(q["explicacao"])

# =========================
# RANKING
# =========================
st.divider()

total = st.session_state.acertos + st.session_state.erros
aproveitamento = (st.session_state.acertos / total * 100) if total else 0

st.write("### 🏆 Ranking")
st.write(f"Pontuação: {st.session_state.pontuacao}")
st.write(f"Aproveitamento: {aproveitamento:.1f}%")

if st.session_state.pontuacao > 200:
    st.write("🏆 Mestre do Vestibular")
elif st.session_state.pontuacao > 100:
    st.write("🥇 Excelente")
else:
    st.write("📘 Em evolução")
