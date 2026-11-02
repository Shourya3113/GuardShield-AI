"""Colours and small HTML helpers shared by the tabs (same palette as the paper's failure map)."""

import streamlit as st

NAVY, TEAL, RED, BLUE, PURPLE, AMBER, GREY, INK = "#1f3a5f", "#2a9d8f", "#d64545", "#2f7fd8", "#5b3fa8", "#e9a23b", "#9aa5b1", "#1d2733"

CSS = """
<style>
.block-container {padding-top: 1.6rem; max-width: 1400px;}
.gs-header {display:flex; align-items:baseline; gap:.8rem; margin-bottom:.2rem;}
.gs-header h1 {font-size:1.9rem; margin:0; color:#1f3a5f;}
.gs-header span {color:#55606e;}
.card-title {font-weight:600; color:#1f3a5f; margin:.2rem 0 .3rem 0;}
.card-title b {display:inline-block; width:1.5rem; height:1.5rem; line-height:1.5rem; text-align:center; border-radius:50%;
               background:#1f3a5f; color:white; margin-right:.45rem; font-size:.85rem;}
.tokens {font-family: Consolas, monospace; font-size:.95rem; line-height:2.0; min-height:3rem; padding:.4rem .5rem;
         border:1px solid #e3e8ee; border-radius:8px; background:white; white-space:pre-wrap;}
.tok {padding:.12rem .05rem; border-radius:3px;}
.muted {color:#55606e;}
.verdict {border-radius:10px; padding:.9rem 1.1rem; margin:.8rem 0; color:white;}
.verdict h3 {margin:0 0 .2rem 0; font-size:1.15rem; color:white;}
.verdict p {margin:0; opacity:.95;}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def card_title(number: str, text: str):
    st.markdown(f"<div class='card-title'><b>{number}</b>{text}</div>", unsafe_allow_html=True)


def banner(title: str, text: str, color: str):
    st.markdown(f"<div class='verdict' style='background:{color}'><h3>{title}</h3><p>{text}</p></div>", unsafe_allow_html=True)
