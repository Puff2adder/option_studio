"""Shared presentation helpers."""

import streamlit as st


CSS = """
<style>
.stApp{background:linear-gradient(180deg,#f7f9fc 0%,#fff 18%)}
.block-container{max-width:1220px;padding-top:1.25rem;padding-bottom:4rem}
h1,h2,h3{color:#17365d;letter-spacing:-.02em} h1{font-size:2.1rem!important}
h2{font-size:1.45rem!important;margin-top:1.2rem!important} h3{font-size:1.1rem!important}
div[data-testid="stMetric"]{background:#fff;border:1px solid #dce4ee;border-radius:12px;padding:.7rem 1rem;box-shadow:0 2px 8px rgba(23,54,93,.05)}
.hero{background:linear-gradient(120deg,#17365d,#2e74b5);color:white;border-radius:18px;padding:1.3rem 1.55rem;margin:.4rem 0 1.1rem;box-shadow:0 8px 24px rgba(23,54,93,.16)}
.hero h2{color:white!important;margin:0 0 .35rem!important}.hero p{margin:0;color:#eef5ff;font-size:1.02rem}
.concept{background:#eef4fa;border-left:5px solid #2e74b5;border-radius:8px;padding:.8rem 1rem;margin:.65rem 0}
.why{background:#fff8e8;border-left:5px solid #d9a441;border-radius:8px;padding:.8rem 1rem;margin:.65rem 0}
.success-box{background:#edf8f1;border-left:5px solid #2d8a55;border-radius:8px;padding:.8rem 1rem;margin:.65rem 0}
.small-note{font-size:.88rem;color:#5f6b76}[data-testid="stDataFrame"]{border:1px solid #dce4ee;border-radius:10px;overflow:hidden}
.stButton>button{border-radius:9px;font-weight:600}
</style>
"""


def configure_page():
    st.set_page_config(page_title="Options Strategy Learning Studio", page_icon="📈", layout="wide",
                       initial_sidebar_state="expanded")
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title, subtitle):
    st.markdown(f'<div class="hero"><h2>{title}</h2><p>{subtitle}</p></div>', unsafe_allow_html=True)


def concept(title, text):
    st.markdown(f'<div class="concept"><strong>{title}</strong><br>{text}</div>', unsafe_allow_html=True)


def why_it_matters(text):
    st.markdown(f'<div class="why"><strong>Why this matters</strong><br>{text}</div>', unsafe_allow_html=True)


def success_box(title, text):
    st.markdown(f'<div class="success-box"><strong>{title}</strong><br>{text}</div>', unsafe_allow_html=True)


def signed_money(value):
    return f"{'-' if value < 0 else ''}${abs(value):,.2f}"
