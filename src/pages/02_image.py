import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import io
 

def resize_image(image_data: bytes, max_size: int) -> bytes:
    # バイナリデータを画像オブジェクトに変換
    image = Image.open(io.BytesIO(image_data))

    # 画像の元のサイズを取得
    width, height = image.size

    # 長辺が指定サイズを超えている場合のみリサイズを実行
    if max(width, height) > max_size:
        # 縦横比を保持したままリサイズ
        if width > height:
            new_width = max_size
            new_height = int(max_size * height / width)
        else:
            new_height = max_size
            new_width = int(max_size * width / height)

        # リサイズを実行
        image = image.resize((new_width, new_height), Image.LANCZOS)

    # 画像オブジェクトをバイナリデータに戻す
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='WEBP')

    return byte_arr.getvalue()

def main():
    st.title('画像にタイトルをつける')
    # see also: https://docs.kanaries.net/ja/topics/Streamlit/streamlit-upload-file
    uploaded_file = st.file_uploader("ファイルを選択してください", type=['avif', 'webp', 'png', 'jpg'])
    prompt = st.text_area('Prompt', 'この画像にタイトルをつけて。')
    api_key = st.text_input('Google AI Studio API Key', '', type="password")
    # APIキーの設定
    genai.configure(api_key=api_key)

    if uploaded_file is not None and prompt.strip() != '' and api_key.strip() != '':
        pushed = st.button('Request')

        if pushed:
            # バイトとしてファイルを読み取る場合：
            bytes_data = uploaded_file.getvalue()
            # st.write(bytes_data)

            ext = os.path.splitext(uploaded_file.name)[1][1:]


            # モデルの設定
            model = genai.GenerativeModel('gemini-pro-vision')

            st.write(prompt)
            st.image(bytes_data)

            resized_bytes_data = resize_image(bytes_data, 512)

            picture = [{
                'mime_type': f'image/{ext}',
                'data': resized_bytes_data
            }]

            response = model.generate_content(
                contents=[prompt, picture[0]]
            )
            st.write(response.text)

            st.image(resized_bytes_data)


main()