"""Results tab: system metrics, the Study 1 failure map and Study 2, all read from the committed result files."""

import plotly.graph_objects as go
import streamlit as st

import data
from theme import AMBER, GREY, INK, NAVY, PURPLE, RED, TEAL, BLUE

MODE_CODE = {None: 0, "stable": 1, "fail_closed": 2, "fail_open": 3, "both": 4}
MODE_COLORS = ["#ffffff", "#f0efec", RED, BLUE, PURPLE]


@st.cache_data
def _failure_map(run):
    return data.failure_map(run)


@st.cache_data
def _macros():
    return data.macros()


@st.cache_data
def _report(name):
    return data.report(name)


def kpis():
    m1, m2 = _report("raw_eval_in_distribution_test_698")["metrics"], _report("raw_eval_out_of_distribution_500")["metrics"]
    e = _report("raw_eval_pipeline_e2e")["metrics"]
    fe = _report("raw_eval_stage2_factuality_800")["per_source_breakdown"]["FEVER (NAACL 2018)"]
    cols = st.columns(6)
    cols[0].metric("Stage 1 recall (test)", f"{m1['recall']:.1%}")
    cols[1].metric("Stage 1 false positives", f"{m1['fpr']:.2%}")
    cols[2].metric("Recall, unseen attacks", f"{m2['recall']:.1%}")
    cols[3].metric("Stage 1 latency", f"{m1['latency_p50_ms']:.1f} ms")
    cols[4].metric("Full pipeline latency", f"{e['latency_p50_ms']:.1f} ms")
    cols[5].metric("Stage 2 AUROC (FEVER)", f"{fe['auroc']:.3f}")


def baselines() -> go.Figure:
    pai, tf = _report("table_external_baseline_protectai"), _report("table_tfidf_baseline_comparison")
    m1, m2 = _report("raw_eval_in_distribution_test_698")["metrics"], _report("raw_eval_out_of_distribution_500")["metrics"]
    models = ["TF-IDF + logistic regression", "ProtectAI DeBERTa-v3-base", "GuardShield DeBERTa-v3-small (ours)"]
    ins = [tf["in_distribution"]["recall"], pai["in_distribution"]["recall"], m1["recall"]]
    out = [tf["out_of_distribution"]["recall"], pai["out_of_distribution"]["recall"], m2["recall"]]
    fig = go.Figure([go.Bar(name="test set from training sources", x=models, y=[v * 100 for v in ins], marker_color=NAVY,
                            text=[f"{v:.1%}" for v in ins], textposition="outside"),
                     go.Bar(name="zero-shot set (never seen)", x=models, y=[v * 100 for v in out], marker_color=TEAL,
                            text=[f"{v:.1%}" for v in out], textposition="outside")])
    fig.update_layout(height=330, barmode="group", margin=dict(l=10, r=10, t=40, b=10), yaxis=dict(title="attack recall (%)", range=[0, 112]),
                      legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0), margin_t=80,
                      title=dict(text="Stage 1 against baselines on identical splits", y=0.97, yanchor="top", font=dict(size=14, color=NAVY)))
    return fig


def heatmap(fm) -> go.Figure:
    z, text, hover = [], [], []
    for row in fm["cells"]:
        z.append([MODE_CODE.get(c["mode"], 0) for c in row])
        text.append([f"{c['auroc']:.2f}".lstrip("0") + ("†" if c["signal"] == "destroyed" and c["family"] != "Clean" else "")
                     for c in row])
        hover.append([f"<b>{c['detector']}</b> · {c['family']}<br>AUROC {c['auroc']:.3f}"
                      + (f" [{c['ci'][0]:.2f}, {c['ci'][1]:.2f}]" if c["ci"] else "")
                      + f"<br>signal: {c['signal'] or 'n/a'}<br>mode: {data.MODE_LABEL.get(c['mode'], c['mode'])}"
                      + (f"<br>attack recall {c['tpr']:.1%} · benign FPR {c['fpr']:.1%}" if c["tpr"] is not None and c["fpr"] is not None else "")
                      for c in row])
    n = len(MODE_COLORS)
    scale = []
    for k, col in enumerate(MODE_COLORS):
        scale += [[k / n, col], [(k + 1) / n, col]]
    fig = go.Figure(go.Heatmap(z=z, x=fm["columns"], y=fm["rows"], text=text, texttemplate="%{text}", textfont=dict(size=11),
                               customdata=hover, hovertemplate="%{customdata}<extra></extra>", colorscale=scale,
                               zmin=-0.5, zmax=n - 0.5, showscale=False, xgap=2, ygap=2))
    fig.update_layout(height=640, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(autorange="reversed"),
                      xaxis=dict(side="top"), plot_bgcolor="white")
    return fig


def legend():
    items = [(RED, "fail-closed: blocks benign twins (+20 pts FPR)"), (BLUE, "fail-open: misses attacks (−20 pts recall)"),
             (PURPLE, "both"), ("#f0efec", "stable"), (None, "† intent signal destroyed (AUROC upper CI < 0.75)")]
    html = " ".join(f"<span style='display:inline-block;width:.9rem;height:.9rem;background:{c};border:1px solid #ccc;"
                    f"vertical-align:middle;margin:0 .3rem 0 .8rem'></span>{t}" if c else f"<span style='margin-left:.8rem'>{t}</span>"
                    for c, t in items)
    st.markdown(f"<div style='font-size:.85rem;color:{INK}'>{html}</div>", unsafe_allow_html=True)


def study2_charts():
    rows = data.study2(_macros())
    labels = [r["arm"].replace(" ", "<br>", 1) for r in rows]
    a = go.Figure([go.Bar(name="PIDS-Bench (new source)", x=labels, y=[r["pids_auc"] for r in rows], marker_color=NAVY,
                          text=[f"{r['pids_auc']:.2f}" for r in rows], textposition="outside"),
                   go.Bar(name="Gandalf (familiar source)", x=labels, y=[r["gandalf_auc"] for r in rows], marker_color=GREY)])
    a.add_hline(y=0.5, line=dict(color=RED, dash="dot"), annotation_text="chance")
    a.update_layout(height=340, barmode="group", margin=dict(l=10, r=10, t=40, b=10), yaxis=dict(title="AUROC, seen character families", range=[0.4, 1.0]),
                    legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0), margin_t=80,
                    title=dict(text="Separating attacks from twins (higher is better)", y=0.97, yanchor="top", font=dict(size=14, color=NAVY)))
    b = go.Figure(go.Bar(x=labels, y=[r["pids_fpr"] for r in rows], marker_color=[GREY, GREY, TEAL, AMBER, TEAL],
                         text=[f"{r['pids_fpr']:.0f}%" for r in rows], textposition="outside"))
    b.update_layout(height=340, margin=dict(l=10, r=10, t=80, b=10), yaxis=dict(title="benign FPR at 90% recall (%)", range=[0, 112]),
                    title=dict(text="Harmless prompts blocked (lower is better)", font=dict(size=14, color=NAVY)))
    pts = data.coupling(_macros())
    c = go.Figure([go.Scatter(x=[p["ratio"] for p in pts], y=[p["recall"] for p in pts], name="attack recall", mode="lines+markers",
                              line=dict(color=BLUE, width=3)),
                   go.Scatter(x=[p["ratio"] for p in pts], y=[p["fpr"] for p in pts], name="benign-twin FPR", mode="lines+markers",
                              line=dict(color=RED, width=3, dash="dash"))])
    c.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10), xaxis=dict(title="share of training examples given a perturbed copy",
                    tickvals=[0, 0.25, 0.5, 1]), yaxis=dict(title="% at default threshold", range=[0, 105]),
                    legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0), margin_t=80,
                    title=dict(text="Augmentation lowers recall and false alarms together", y=0.97, yanchor="top", font=dict(size=14, color=NAVY)))
    return a, b, c


def render(settings):
    st.subheader("GuardShield system")
    kpis()
    st.plotly_chart(baselines(), use_container_width=True, config={"displayModeBar": False})

    st.subheader("Study 1 · failure map of 19 detectors")
    src = st.radio("Data source", list(data.SOURCES), horizontal=True, label_visibility="collapsed")
    fm = _failure_map(data.SOURCES[src])
    n = data.failure_counts(fm)
    cols = st.columns(4)
    cols[0].metric(f"Signal destroyed ({n['destroyed'] / n['cells']:.0%} of cells)", f"{n['destroyed']} / {n['cells']}")
    cols[1].metric("Fail-closed cells", n["fail_closed"])
    cols[2].metric("Fail-open cells", n["fail_open"])
    cols[3].metric("Both directions", n["both"])
    legend()
    st.plotly_chart(heatmap(fm), use_container_width=True, config={"displayModeBar": False})
    st.caption("Each cell: one detector under one disguise, attack and benign twin perturbed identically. Number: "
               "within-condition AUROC. Colour: failure mode at the detector's default threshold. Hover for details. "
               "* families held out from Study 2 training.")

    st.subheader("Study 2 · canonicalization versus augmentation (GuardShield, 5 seeds)")
    a, b, c = study2_charts()
    l, r = st.columns(2)
    l.plotly_chart(a, use_container_width=True, config={"displayModeBar": False})
    r.plotly_chart(b, use_container_width=True, config={"displayModeBar": False})
    st.plotly_chart(c, use_container_width=True, config={"displayModeBar": False})
