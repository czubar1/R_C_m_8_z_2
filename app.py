import streamlit as st
import openai
from dotenv import load_dotenv
import os
import tiktoken

# Załaduj zmienne środowiskowe
load_dotenv()

# Inicjalizacja historii
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar: klucz API
with st.sidebar:
    st.header("🔐 Klucz API OpenAI")
    api_key_input = st.text_input("Wprowadź swój klucz API:", type="password")
    if api_key_input:
        openai.api_key = api_key_input
    else:
        st.warning("⚠️ Wprowadź klucz API, aby korzystać z chatbota.")
    st.markdown("---")

    # Wybór modelu
    model_choice = st.selectbox(
        "Wybierz model OpenAI:",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
        index=2
    )

    # Statystyki
    st.header("📊 Statystyki zapytania")
    token_count_placeholder = st.empty()
    cost_placeholder = st.empty()
    st.markdown("---")

    # Historia jako klikalne przyciski
    st.subheader("🕘 Historia pytań")
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        if st.button(item["question"], key=f"history_{i}"):
            st.markdown("### 🔁 Odtworzona odpowiedź:")
            st.write(f"**Pytanie:** {item['question']}")
            st.write(f"**Odpowiedź:** {item['answer']}")

# Główna część aplikacji
st.title("💬 Chatbot do analizy kodu")

code_input = st.text_area("Wklej kod, który chcesz przeanalizować:", height=200)
question = st.text_input("Zadaj pytanie o kod (np. 'Co robi ta funkcja?')")

# Funkcja do liczenia tokenów
def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Funkcja do wysyłania zapytania
def ask_openai(code, question, model="gpt-4o"):
    prompt = f"""
Jesteś ekspertem od Pythona. Oto kod użytkownika:

{code}

Pytanie: {question}
Odpowiedz jasno i zwięźle.
"""
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500
    )
    reply = response.choices[0].message.content

    # Liczenie tokenów
    input_tokens = count_tokens(prompt, model)
    output_tokens = count_tokens(reply, model)
    total_tokens = input_tokens + output_tokens
    cost = total_tokens / 1000 * 0.0015

    token_count_placeholder.write(f"🔢 Tokeny: {total_tokens}")
    cost_placeholder.write(f"💰 Koszt: ${cost:.4f}")

    return reply

# Obsługa zapytania
if st.button("Wyślij zapytanie", key="send_button"):
    if not openai.api_key:
        st.error("❌ Brak klucza API. Wprowadź go w lewym pasku.")
    elif code_input and question:
        answer = ask_openai(code_input, question, model=model_choice)
        st.session_state.history.append({"question": question, "answer": answer})
        st.markdown("### 🧠 Odpowiedź chatbota:")
        st.write(answer)
    else:
        st.warning("Wpisz kod i pytanie, zanim wyślesz zapytanie.")
        
        
