import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import io
import fitz  # PyMuPDF

import fitz  # PyMuPDF
import io
from PIL import Image

def resize_image(image, max_size: int):
    if max_size <= 0:
        return image
    # Resize image if it's larger than max_size
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = tuple([int(x*ratio) for x in image.size])
        image = image.resize(new_size, Image.AFFINE)
    return image

compression_rate = 30

def render_page(doc, pagenum: int, max_size: int):
    page = doc.load_page(pagenum)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    img = resize_image(img, max_size)

    byte_arr = io.BytesIO()
    img.save(byte_arr, format='WEBP', quality=compression_rate)
    return byte_arr.getvalue()

def pdf_to_images(pdf_bytes: bytes, max_size: int) -> list[bytes]:
    doc = fitz.open("pdf", pdf_bytes)

    byte_images = []
    for i in range(len(doc)):
        byte_images.append(render_page(doc, i, max_size))

    return byte_images



def main():
    st.title('PDFのタイトルをつける')
    # see also: https://docs.kanaries.net/ja/topics/Streamlit/streamlit-upload-file
    uploaded_file = st.file_uploader("ファイルを選択してください", type=['pdf'])
    default_prompt = """
この画像たちはPDFの最初の3ページである。このPDFに対していい感じに日本語のファイル名をつけたい。
まずOCRをして内容を読み、固有名詞を中心にキーワードを抽出し、なるべくバリエーションに富んだ日本語のファイル名の候補を複数提案して。
結果は以下のjsonフォーマットでページ名の候補を挙げて。ただしおすすめ度は0〜100の整数でつけて。
{
  keywords: [<OCRで抽出した中のキーワードのリスト>],
  title: [
    {"fileName": <候補のタイトル1>.pdf, "recommendedLevel": <おすすめ度1>},
    {"fileName": <候補のタイトル2>.pdf, "recommendedLevel": <おすすめ度2>},
    ...
  ]
}
""".strip()
    prompt = st.text_area('Prompt', default_prompt)
    page_num_str = st.text_input('送信するページ数(最大16)', 16)
    max_size_str = st.text_input('画像を縮小する場合の長辺のサイズ(px)(0の場合は縮小しない)', 1280)
    api_key = st.text_input('Google AI Studio API Key', '', type="password")

    if uploaded_file is not None and prompt.strip() != '' and api_key.strip() != '' and page_num_str.isnumeric() and max_size_str.isnumeric():
        pushed = st.button('Request')
        page_num = int(page_num_str)
        max_size = int(max_size_str)

        if pushed:
            # APIキーの設定
            genai.configure(api_key=api_key)
            # バイトとしてファイルを読み取る場合：
            bytes_data = uploaded_file.getvalue()
            # st.write(bytes_data)

            ext = os.path.splitext(uploaded_file.name)[1][1:]

            images = pdf_to_images(bytes_data, max_size)

            # モデルの設定
            model = genai.GenerativeModel('gemini-pro-vision')

            send_page_num = min(page_num, 16) if page_num > 0 else 16
            st.write(prompt)
            for image in images[:send_page_num]:
              st.image(image)

            pictures = [{
                'mime_type': f'image/webp',
                'data': image
            } for image in images]

            contents = [prompt] + pictures[:send_page_num]

            response = model.generate_content(contents=contents)
            st.write(response.text)

            # st.image(resized_bytes_data)



main()