import base64
import json
from io import BytesIO

import numpy as np
import pycurl
import streamlit as st
from PIL import Image


def encode_image(array, dtype=np.uint8):
    """Encode an array to base64 encoded string or bytes.
    Args:
        array: numpy.array
        dtype
    Returns:
        base64 encoded string
    """
    if array is None:
        return None
    return base64.b64encode(np.asarray(array, dtype=dtype)).decode("utf-8")


def main():
    st.title("COVID-19 Chest X-ray Image Classification")

    url = st.text_input("Input endpoint url.")
    token = st.text_input("Input token.")
    uploaded_file = st.file_uploader("Upload an image.")

    if url and token and uploaded_file:
        if url[:4] == 'http' and url[4] != 's':
            url = 'https' + url[4:]

        image = Image.open(uploaded_file)

        img = np.asarray(image.convert("RGB"))
        img_shape = img.shape
        encoded_img = encode_image(img.ravel())
        data = json.dumps({"encoded_image": encoded_img,
                           "image_shape": img_shape}).encode('utf-8')

        headers = ['Content-Type: application/json']
        headers.append('X-Bedrock-Api-Token: ' + token)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPHEADER, headers)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.TIMEOUT_MS, 30000)
        c.setopt(pycurl.POSTFIELDSIZE, len(data))
        c.setopt(pycurl.READDATA, BytesIO(data))
        c.setopt(pycurl.WRITEDATA, buffer)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.perform()
        c.close()

        prob = json.loads(buffer.getvalue().decode('utf-8'))["prob"]

        st.subheader(f"Probability of having COVID-19 = {prob:.6f}")
        st.image(image, caption="Uploaded Image", use_column_width=True)


if __name__ == "__main__":
    main()
