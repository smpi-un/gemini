import streamlit as st
import google.generativeai as genai

# APIキーの設定
genai.configure(api_key="AIzaSyBmWC0GzLq4A9icYRgHc42mlz_JVEhz0-g")

# Streamlitのインターフェース設定
st.title('😱Generative AI with Google API')
user_input = st.text_input("Enter your question:")
user_input = st.text_input("Enter your question:")

if user_input:
    # モデルの設定
    model = genai.GenerativeModel('gemini-pro')

    # ユーザーの入力をモデルに渡す
    response = model.generate_content(user_input)
    print(response)

    # 結果を表示
    st.write(response.text)

