import streamlit as st
import google.generativeai as genai

# APIキーの設定

# Streamlitのインターフェース設定
st.title('😱Generative AI with Google API')
user_input = st.text_input("Enter your question:")

api_key = st.text_input('Google AI Studio API Key' '')

if user_input.strip() != "" and api_key.strip() != "":
    # モデルの設定
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    # ユーザーの入力をモデルに渡す
    response = model.generate_content(user_input)
    print(response)

    # 結果を表示
    st.write(response.text)


