import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import io
import fitz  # PyMuPDF

import fitz  # PyMuPDF
import io
from PIL import Image

def render_page(doc, pagenum, max_size):
    page = doc.load_page(pagenum)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    img = resize_image(img, max_size)

    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    return byte_arr.getvalue()

def pdf_to_images(pdf_bytes: bytes, max_size: int) -> list[bytes]:
    doc = fitz.open("pdf", pdf_bytes)

    byte_images = []
    for i in range(len(doc)):
        byte_images.append(render_page(doc, i, max_size))

    return byte_images

def resize_image(image, max_size):
    # Resize image if it's larger than max_size
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = tuple([int(x*ratio) for x in image.size])
        image = image.resize(new_size, Image.ANTIALIAS)
    return image

def process_page(doc, page, max_size):
    byte_images = []
    for img in page.get_images(full=True):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        if pix.n < 5:       # this is GRAY or RGB
            pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        else:               # CMYK: convert to RGB first
            pix1 = fitz.Pixmap(fitz.csRGB, pix)
            pil_img = Image.frombytes("RGB", [pix1.width, pix1.height], pix1.samples)
            pix1 = None
        pix = None

        pil_img = resize_image(pil_img, max_size)

        byte_arr = io.BytesIO()
        pil_img.save(byte_arr, format='PNG')
        byte_images.append(byte_arr.getvalue())
    return byte_images

def pdf_bytes_to_images(pdf_bytes, max_size):
    doc = fitz.open("pdf", pdf_bytes)

    byte_images = []
    for i in range(len(doc)):
        byte_images.extend(process_page(doc, doc[i], max_size))

    return byte_images


def main():
    st.title('😱Generative AI with Google API')
    # see also: https://docs.kanaries.net/ja/topics/Streamlit/streamlit-upload-file
    uploaded_file = st.file_uploader("ファイルを選択してください", type=['pdf'])
    default_prompt = """
        この画像たちはPDFの最初の3ページである。このPDFに対していい感じに日本語のファイル名をつけたい。以下のjsonフォーマットでページ名の候補を挙げて。
        ただしおすすめ度は0〜100の整数でつけて。
        [
          {"fileName": <候補のタイトル1>.pdf, "recommendedLevel": <おすすめ度1>},
          {"fileName": <候補のタイトル2>.pdf, "recommendedLevel": <おすすめ度2>},
          ...
        ]
    """
    prompt = st.text_area('Prompt', default_prompt)
    api_key = st.text_input('Google AI Studio API Key' '')

    if uploaded_file is not None and prompt.strip() != '':
        pushed = st.button('Request')

        if pushed:
            # APIキーの設定
            genai.configure(api_key=api_key)
            # バイトとしてファイルを読み取る場合：
            bytes_data = uploaded_file.getvalue()
            # st.write(bytes_data)

            ext = os.path.splitext(uploaded_file.name)[1][1:]

            images = pdf_to_images(bytes_data, 1280)

            # モデルの設定
            model = genai.GenerativeModel('gemini-pro-vision')

            st.write(prompt)
            for image in images:
              st.image(image)

            pictures = [{
                'mime_type': f'image/png',
                'data': image
            } for image in images]

            response = model.generate_content(
                contents=[prompt] + pictures[:3]
            )
            st.write(response.text)

            # st.image(resized_bytes_data)


