import base64
import os
import fitz  # PyMuPDF
import pandas as pd


def read_pdf_text(file) -> str:
    """يقرأ نص PDF باستخدام PyMuPDF"""
    text = ""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        text = f"خطأ في قراءة الملف: {e}"
    return text


def read_excel_file(file) -> pd.DataFrame:
    """يقرأ ملف Excel ويُرجع DataFrame"""
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        return pd.DataFrame({"خطأ": [str(e)]})


def download_button(obj, filename: str, label: str):
    """زر تحميل ملف داخل Streamlit"""
    b64 = base64.b64encode(obj.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a>'
    return href

