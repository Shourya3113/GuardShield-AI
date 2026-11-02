"""
GuardShield AI demo dashboard.

    streamlit run dashboard/app.py

Tabs: Live pipeline (Stage 1 scan, generation with live entropy, Stage 2 fact check), Multi-turn & signing, and
Results (system metrics, the Study 1 failure map and Study 2, from the committed result files).
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402
import live  # noqa: E402
import multiturn  # noqa: E402
import results  # noqa: E402
from theme import inject_css  # noqa: E402

st.set_page_config(page_title="GuardShield AI", page_icon="\U0001f6e1️", layout="wide")
inject_css()
st.markdown("<div class='gs-header'><h1>\U0001f6e1️ GuardShield AI</h1><span>real-time prompt-injection defense "
            "and hallucination detection · sidecar proxy for LLM applications</span></div>", unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        st.header("Settings")
        gen = st.radio("Answer generator", ["Qwen2.5-0.5B (local)", "Ollama"],
                       help="The local model runs inside this app on the GPU and works offline. Ollama gives better answers "
                            "if it is running; the entropy chart needs it to return token probabilities.")
        s = {"generator": "local" if gen.startswith("Qwen") else "ollama", "generator_label": "Qwen2.5-0.5B"}
        if s["generator"] == "ollama":
            s["ollama_url"] = st.text_input("Ollama URL", engine.DEFAULT_OLLAMA_URL)
            models = engine.ollama_models(s["ollama_url"])
            if models:
                st.success(f"Ollama running · {len(models)} models")
                default = models.index("qwen2.5:3b") if "qwen2.5:3b" in models else 0
                s["ollama_model"] = st.selectbox("Model", models, index=default)
                s["generator_label"] = s["ollama_model"]
            else:
                st.error("Ollama is not reachable. Start it with `ollama serve`, or use the local model.")
                s["generator"] = "local"
        st.divider()
        s["stage1"] = st.slider("Stage 1 block threshold", 0.05, 0.95, 0.50, 0.05)
        s["entropy"] = st.slider("Entropy spike threshold (bits)", 0.50, 1.58, 1.25, 0.01, help="Maximum for top-3 entropy is log2(3) = 1.585 bits.")
        s["spikes"] = st.slider("Consecutive spikes to halt", 1, 5, 2)
        s["max_tokens"] = st.slider("Max new tokens", 10, 80, 40, 5)
        st.divider()
        st.success("Models loaded and warmed up", icon="✅")
        st.caption("Paper: *Guards That Reject the Unfamiliar* · code: github.com/Shourya3113/GuardShield-AI")
    return s


WARM_TEXTS = tuple(p for p, _ in live.PRESETS.values()) + tuple(t["content"] for t in multiturn.BENIGN + [multiturn.FORGED])
pipeline = engine.warmed_pipeline(WARM_TEXTS)  # loads and warms every model once, when the page first opens
settings = dict(sidebar(), pipeline=pipeline)
VIEWS = {"⚡ Live pipeline": live.render, "💬 Multi-turn & signing": multiturn.render, "📊 Results": results.render}
# a keyed selector keeps the chosen view across reruns (st.tabs jumps back to the first tab after a button press)
view = st.segmented_control("View", list(VIEWS), default=list(VIEWS)[0], key="view", label_visibility="collapsed")
st.write("")
VIEWS[view or list(VIEWS)[0]](settings)
