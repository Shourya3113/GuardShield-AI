"""
================================================================================
  GuardShield AI — Automated Presentation Deck Generator
  Generates a high-impact, academic & technical 16:9 Widescreen Presentation
  Format: PowerPoint (.pptx) and High-Resolution PDF (.pdf)
================================================================================
"""

import os
import sys
import shutil
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ------------------------------------------------------------------------------
# Color Palette & Typography
# ------------------------------------------------------------------------------
COLOR_NAVY_DARK = RGBColor(11, 25, 44)       # #0B192C
COLOR_NAVY_CARD = RGBColor(20, 36, 61)       # #14243D
COLOR_SLATE_BG  = RGBColor(248, 250, 252)    # #F8FAFC
COLOR_WHITE     = RGBColor(255, 255, 255)    # #FFFFFF
COLOR_BORDER    = RGBColor(226, 232, 240)    # #E2E8F0
COLOR_TEXT_MAIN = RGBColor(15, 23, 42)       # #0F172A
COLOR_TEXT_MUTED= RGBColor(100, 116, 139)    # #64748B
COLOR_BLUE_TECH = RGBColor(37, 99, 235)      # #2563EB
COLOR_BLUE_DARK = RGBColor(29, 78, 216)      # #1D4ED8
COLOR_GREEN     = RGBColor(5, 150, 105)      # #059669
COLOR_RED       = RGBColor(220, 38, 38)      # #DC2626
COLOR_AMBER     = RGBColor(217, 119, 6)      # #D97706
COLOR_CARD_FILL = RGBColor(255, 255, 255)    # #FFFFFF

FONT_HEADING = "Segoe UI"
FONT_BODY    = "Calibri"

def set_slide_background(slide, color):
    """Fills slide background with a solid color."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, section_tag: str, title: str, subtitle: str, dark: bool = False):
    """Adds a standard structured header with section badge, title, and subtitle."""
    # Section Tag / Badge
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = section_tag.upper()
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = RGBColor(96, 165, 250) if dark else COLOR_BLUE_TECH

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.55))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    p_title = tf_title.paragraphs[0]
    p_title.text = title
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE if dark else COLOR_TEXT_MAIN

    # Subtitle / Takeaway
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(0.4))
    tf_sub = sub_box.text_frame
    tf_sub.word_wrap = True
    tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = subtitle
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = RGBColor(203, 213, 225) if dark else COLOR_TEXT_MUTED

def add_card(slide, left, top, width, height, bg_color=COLOR_WHITE, border_color=COLOR_BORDER):
    """Creates a rounded rectangle container card."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

# ------------------------------------------------------------------------------
# Slide Builders
# ------------------------------------------------------------------------------

def build_slide_1_title(prs):
    """Slide 1: Title & Academic Identity."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_NAVY_DARK)

    # Accent Top Line
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.7), Inches(2.5), Inches(0.06))
    accent.fill.solid()
    accent.fill.fore_color.rgb = COLOR_BLUE_TECH
    accent.line.fill.background()

    # University Badge
    u_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.9), Inches(11.5), Inches(0.4))
    tf_u = u_box.text_frame
    tf_u.word_wrap = True
    p_u = tf_u.paragraphs[0]
    p_u.text = "AMITY SCHOOL OF ENGINEERING & TECHNOLOGY (ASET) | B.TECH MINOR PROJECT REVIEW 2"
    p_u.font.name = FONT_HEADING
    p_u.font.size = Pt(11)
    p_u.font.bold = True
    p_u.font.color.rgb = RGBColor(147, 197, 253)

    # Big Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(1.2))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = "GuardShield AI"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(44)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

    # Subtitle
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.6), Inches(11.7), Inches(0.8))
    tf_sub = sub_box.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "A Real-Time Asymmetric Sidecar Proxy for LLM Hallucination Detection & Ingress Prompt Injection Defense"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = RGBColor(226, 232, 240)

    # Info Cards Layout
    card_w = Inches(3.6)
    card_h = Inches(3.0)
    top_pos = Inches(3.7)

    # Card 1: Project Metadata
    add_card(slide, Inches(0.8), top_pos, card_w, card_h, COLOR_NAVY_CARD, RGBColor(30, 58, 95))
    tb1 = slide.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "PROJECT METADATA"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(147, 197, 253)
    
    details1 = [
        ("Group No.:", "Group 50"),
        ("Programme:", "B.Tech CSE (AIML)"),
        ("Semester:", "7th Semester (4th Year)"),
        ("Academic Year:", "2026 – 2027"),
        ("Project Area:", "Generative AI & AI Safety (MLOps)")
    ]
    for lbl, val in details1:
        p = tf1.add_paragraph()
        p.text = f"{lbl} {val}"
        p.font.name = FONT_BODY
        p.font.size = Pt(11)
        p.font.color.rgb = RGBColor(203, 213, 225)

    # Card 2: Student Team
    add_card(slide, Inches(4.8), top_pos, card_w, card_h, COLOR_NAVY_CARD, RGBColor(30, 58, 95))
    tb2 = slide.shapes.add_textbox(Inches(5.0), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "STUDENT TEAM (GROUP 50)"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(12)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(147, 197, 253)

    team = [
        ("Shourya Solanki", "A2305223569", "Lead Architect (Pipeline & Benchmarking)"),
        ("Rachit Ryan Chug", "A2305223166", "Research Analyst (Literature & NLI)"),
        ("Dhruv Raj Singh", "A2305223191", "Data Engineer (Corpus Curation)")
    ]
    for name, roll, role in team:
        p_n = tf2.add_paragraph()
        p_n.text = f"• {name} ({roll})"
        p_n.font.name = FONT_BODY
        p_n.font.size = Pt(11)
        p_n.font.bold = True
        p_n.font.color.rgb = COLOR_WHITE
        p_r = tf2.add_paragraph()
        p_r.text = f"   Role: {role}"
        p_r.font.name = FONT_BODY
        p_r.font.size = Pt(9.5)
        p_r.font.color.rgb = RGBColor(148, 163, 184)

    # Card 3: Faculty Guidance
    add_card(slide, Inches(8.8), top_pos, card_w, card_h, COLOR_NAVY_CARD, RGBColor(30, 58, 95))
    tb3 = slide.shapes.add_textbox(Inches(9.0), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.text = "FACULTY SUPERVISION"
    p3.font.name = FONT_HEADING
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(147, 197, 253)

    p_guide = tf3.add_paragraph()
    p_guide.text = "\nDr. Abhishek Kaushal"
    p_guide.font.name = FONT_HEADING
    p_guide.font.size = Pt(13)
    p_guide.font.bold = True
    p_guide.font.color.rgb = COLOR_WHITE

    p_dept = tf3.add_paragraph()
    p_dept.text = "Faculty Guide & Assistant Professor\nDepartment of Computer Science & Engineering\nAmity School of Engineering & Technology\nAmity University Uttar Pradesh"
    p_dept.font.name = FONT_BODY
    p_dept.font.size = Pt(10.5)
    p_dept.font.color.rgb = RGBColor(203, 213, 225)


def build_slide_2_intro(prs):
    """Slide 2: 1) Introduction — The Dual Threat in Enterprise LLMs."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_SLATE_BG)

    add_header(
        slide,
        "1. INTRODUCTION & MOTIVATION",
        "The Dual Vulnerability Crisis in Enterprise LLM Deployment",
        "Production AI applications face two compounding failure modes that undermine safety, trust, and operational efficiency."
    )

    card_w = Inches(3.7)
    card_h = Inches(4.0)
    top_pos = Inches(1.85)

    # Card 1: Adversarial Ingress
    add_card(slide, Inches(0.8), top_pos, card_w, card_h)
    tb1 = slide.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.25), card_w - Inches(0.4), card_h - Inches(0.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "THREAT 1: ADVERSARIAL INGRESS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    points1 = [
        ("Prompt Injection Attacks:", "Malicious input instructions deliberately override developer guardrails and system system prompts."),
        ("Cognitive Jailbreaks (DAN):", "Adversarial personas and roleplay frameworks bypass foundational safety filters."),
        ("Token Smuggling & Delimiters:", "Obfuscated encodings (Base64, Unicode) slip past static keyword blocklists."),
        ("Operational Risk:", "Data leakage, unauthorized backend API calls, and severe compliance violations.")
    ]
    for h, b in points1:
        p = tf1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Card 2: Hallucinatory Egress
    add_card(slide, Inches(4.8), top_pos, card_w, card_h)
    tb2 = slide.shapes.add_textbox(Inches(5.0), top_pos + Inches(0.25), card_w - Inches(0.4), card_h - Inches(0.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "THREAT 2: FACTUAL EGRESS HALLUCINATION"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER

    points2 = [
        ("Ungrounded Generations:", "Autoregressive generation fabricates plausible-sounding yet false factual assertions."),
        ("Uncalibrated Confidence:", "Models output fabricated facts with high probability mass, misleading end users."),
        ("High-Stakes Liability:", "Catastrophic failure in medical diagnostics, legal discovery, and automated trading."),
        ("Erosion of Trust:", "Enterprise adoption stalls when non-deterministic outputs cannot be verified in real time.")
    ]
    for h, b in points2:
        p = tf2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Card 3: The Operational Dilemma
    add_card(slide, Inches(8.8), top_pos, card_w, card_h)
    tb3 = slide.shapes.add_textbox(Inches(9.0), top_pos + Inches(0.25), card_w - Inches(0.4), card_h - Inches(0.5))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    p = tf3.paragraphs[0]
    p.text = "THE OPERATIONAL DILEMMA"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_TECH

    points3 = [
        ("Heavy Monolithic LLMs:", "Guardrails like Meta Llama-Guard-3 (8B) add 1,500 – 3,500 ms latency per query."),
        ("Multi-Sample Fact Checks:", "SelfCheckGPT requires 5x–10x multi-sample generation, exploding cloud GPU billing."),
        ("Static Regex Inadequacy:", "Basic rule filters fail against trivial obfuscations and paraphrased attacks."),
        ("The Need for GuardShield:", "Real-time microservices demand sub-50 ms verification with zero primary model retraining.")
    ]
    for h, b in points3:
        p = tf3.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Bottom Banner
    bot_card = add_card(slide, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.9), RGBColor(238, 242, 255), RGBColor(199, 210, 254))
    bot_tb = slide.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.8))
    bot_tf = bot_tb.text_frame
    bot_tf.word_wrap = True
    p_bot = bot_tf.paragraphs[0]
    p_bot.text = "CORE RESEARCH OBJECTIVE:"
    p_bot.font.name = FONT_HEADING
    p_bot.font.size = Pt(11)
    p_bot.font.bold = True
    p_bot.font.color.rgb = COLOR_BLUE_DARK
    p_bot_desc = bot_tf.add_paragraph()
    p_bot_desc.text = "Design, benchmark, and deploy an ultra-low-latency (<50 ms E2E) asymmetric sidecar proxy that intercepts ingress prompt attacks before generative computation and validates factual consistency via streaming entropy and declarative NLI."
    p_bot_desc.font.name = FONT_BODY
    p_bot_desc.font.size = Pt(11.5)
    p_bot_desc.font.color.rgb = COLOR_TEXT_MAIN


def build_slide_3_problem_solution(prs):
    """Slide 3: 2) Problem Statement and Our Solution."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_SLATE_BG)

    add_header(
        slide,
        "2. PROBLEM STATEMENT & OUR SOLUTION",
        "Asymmetric Architecture: Decoupled Defense without Computational Drag",
        "Separating safety validation from primary text generation provides deterministic, ultra-fast protection."
    )

    top_pos = Inches(1.85)
    col_w = Inches(5.65)
    col_h = Inches(5.15)

    # Left Column: Problem Formulation
    add_card(slide, Inches(0.8), top_pos, col_w, col_h)
    tb_l = slide.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.3), col_w - Inches(0.4), col_h - Inches(0.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "THE PROBLEM: INEFFICIENCY OF MONOLITHIC GUARDRAILS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    prob_items = [
        ("Excessive Ingress Latency Overhead", "Deploying 7B–8B parameter guardrails introduces a 1.5s to 3.5s delay before the user prompt even reaches the target LLM."),
        ("Wasted Generative Compute", "Unprotected LLMs execute 50–120 decoding iterations on jailbreaks before downstream post-filters catch the violation."),
        ("Black-Box Factual Unreliability", "Standard LLM output decoding provides zero visibility into whether the model is reciting factual knowledge or hallucinatory tokens."),
        ("Tight Architectural Coupling", "Modifying prompt prefixes or fine-tuning weights introduces catastrophic forgetting and degrades general reasoning capability.")
    ]
    for title, desc in prob_items:
        p_t = tf_l.add_paragraph()
        p_t.text = f"\n⚠️  {title}"
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_TEXT_MAIN
        p_d = tf_l.add_paragraph()
        p_d.text = f"    {desc}"
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    # Right Column: Our Solution (GuardShield AI)
    add_card(slide, Inches(6.8), top_pos, col_w, col_h, RGBColor(255, 255, 255), COLOR_BLUE_TECH)
    tb_r = slide.shapes.add_textbox(Inches(7.0), top_pos + Inches(0.3), col_w - Inches(0.4), col_h - Inches(0.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "OUR SOLUTION: GUARDSHIELD ASYMMETRIC SIDECAR PROXY"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_DARK

    sol_items = [
        ("Stage 1 Pre-Scan Gatekeeper (<15 ms)", "Fine-tuned DeBERTa-v3 encoder classifies ingress prompts. Blocks injections and jailbreaks before the generative model wakes up."),
        ("Dynamic Streaming Shannon Entropy Engine", "Live mathematical tracking of token uncertainty H(x) during decoding. Catches hallucination spikes at the exact token origin."),
        ("Early Termination Circuit Breaker", "Automatically halts autoregressive generation when sustained entropy spikes exceed calibrated thresholds (1.35 bits)."),
        ("Stage 2 Declarative NLI Fact Grounding", "Cross-encoder verifies factual claims against reference contexts, yielding definitive Entailment vs. Contradiction scoring."),
        ("Zero Primary Model Modification", "Acts as a standalone proxy compatible with any LLM (Qwen, Llama, Mistral, OpenAI, Claude).")
    ]
    for title, desc in sol_items:
        p_t = tf_r.add_paragraph()
        p_t.text = f"\n✅  {title}"
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_GREEN
        p_d = tf_r.add_paragraph()
        p_d.text = f"    {desc}"
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_TEXT_MUTED


def build_slide_4_models_pipeline(prs):
    """Slide 4: 3) Models Used and Pipeline."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_SLATE_BG)

    add_header(
        slide,
        "3. ARCHITECTURE & MODELS USED",
        "The Complete GuardShield Defensive Pipeline",
        "A modular, multi-tier sidecar architecture combining bidirectional encoders, streaming entropy, and NLI fact verifiers."
    )

    card_w = Inches(3.7)
    card_h = Inches(5.15)
    top_pos = Inches(1.85)

    # Tier 1: Stage 1 Ingress Pre-Scan
    add_card(slide, Inches(0.8), top_pos, card_w, card_h)
    tb1 = slide.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "STAGE 1: PRE-SCAN GATEKEEPER"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_TECH

    t1_specs = [
        ("Base Model:", "microsoft/deberta-v3-small"),
        ("Parameters:", "44.3M backbone (142.6M total)"),
        ("Latency Profile:", "13.09 ms (p50) on CUDA"),
        ("Input Processing:", "Sliding-window chunking (256-token window, 128 stride)"),
        ("Mechanics:", "Disentangled self-attention represents content & relative position vectors separately."),
        ("Function:", "Performs binary classification (Attack vs. Safe) in a single fast forward pass."),
        ("Action:", "Blocks adversarial prompts immediately, saving 100% of generative decoding compute.")
    ]
    for lbl, val in t1_specs:
        p = tf1.add_paragraph()
        p.text = f"• {lbl} {val}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Tier 2: Real-time Entropy Stream
    add_card(slide, Inches(4.8), top_pos, card_w, card_h)
    tb2 = slide.shapes.add_textbox(Inches(5.0), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "CORE: STREAMING ENTROPY ENGINE"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    t2_specs = [
        ("Generative LLMs:", "Qwen2.5-3B, Qwen2.5-7B, Phi-3.5-mini"),
        ("Entropy Formula:", "H(x) = -Σ p_i log2(p_i) over vocabulary V"),
        ("Real-time Stream:", "Hooked directly to autoregressive next-token softmax logits."),
        ("Calibrated Threshold:", "1.35 bits empirically separates factual recall from confabulation."),
        ("Detection Logic:", "Rolling window alert buffer detects sustained uncertainty spikes."),
        ("Action:", "Triggers EARLY_TERMINATION to abort generation before fabricated tokens stream to user."),
        ("Zero Overhead:", "Computed in parallel during token sampling with negligible latency.")
    ]
    for lbl, val in t2_specs:
        p = tf2.add_paragraph()
        p.text = f"• {lbl} {val}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Tier 3: Stage 2 Declarative NLI Fact Grounding
    add_card(slide, Inches(8.8), top_pos, card_w, card_h)
    tb3 = slide.shapes.add_textbox(Inches(9.0), top_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    p = tf3.paragraphs[0]
    p.text = "STAGE 2: DECLARATIVE NLI VERIFIER"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER

    t3_specs = [
        ("Base Model:", "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"),
        ("Parameters:", "86M parameters"),
        ("Latency Profile:", "13.89 ms (p50) on CUDA"),
        ("Premise-Hypothesis:", "Pairs reference facts (Premise) with generated statements (Hypothesis)."),
        ("Decomposition:", "Breaks multi-sentence outputs into discrete declarative factual claims."),
        ("Classification:", "Outputs 3-way distribution: Entailment, Neutral, Contradiction."),
        ("Grounding Decision:", "Flags contradictions (FPR: 3.4%) and verifies factual consistency.")
    ]
    for lbl, val in t3_specs:
        p = tf3.add_paragraph()
        p.text = f"• {lbl} {val}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_MAIN


def build_slide_5_datasets(prs):
    """Slide 5: 5) Datasets and Multi-Corpus Curation."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_SLATE_BG)

    add_header(
        slide,
        "5. DATASETS & CURATION METHODOLOGY",
        "Rigorous Evaluation across 5,948 Benchmark Samples",
        "Curated multi-domain evaluation suite designed to eliminate length confounders and test true generalization."
    )

    card_w = Inches(5.65)
    card_h = Inches(2.35)
    top_r1 = Inches(1.85)
    top_r2 = Inches(4.35)

    # Box 1: Deepset Prompt Injections
    add_card(slide, Inches(0.8), top_r1, card_w, card_h)
    tb1 = slide.shapes.add_textbox(Inches(1.0), top_r1 + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.3))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "1. IN-DISTRIBUTION INGRESS: DEEPSET (662 SAMPLES)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_TECH
    items1 = [
        "Composition: 355 adversarial injection attacks, 343 benign control queries.",
        "Attack Variations: Direct system prompt overrides, instruction hijackers, and delimiter insertions.",
        "Role in Pipeline: Calibrates baseline discrimination threshold (0.50) for Stage 1 DeBERTa-v3.",
        "Validation Split: Unseen held-out split of 698 evaluation samples (V3 Mega Suite)."
    ]
    for it in items1:
        p = tf1.add_paragraph()
        p.text = f"• {it}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Box 2: JailbreakBench OOD
    add_card(slide, Inches(6.8), top_r1, card_w, card_h)
    tb2 = slide.shapes.add_textbox(Inches(7.0), top_r1 + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.3))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "2. OUT-OF-DISTRIBUTION: JAILBREAKBENCH & SYNTHETIC OOD (250 SAMPLES)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED
    items2 = [
        "Composition: 76 real-world human-engineered DAN jailbreaks + 174 synthetic templates.",
        "Attack Complexity: Multi-turn persona adoption, role-play framing, hypothetical ethical dilemmas.",
        "Honest Benchmark: Reports exact subset breakdown (92.1% recall on real DAN, 100% on templates).",
        "Significance: Tests zero-shot transfer without in-domain fine-tuning exposure."
    ]
    for it in items2:
        p = tf2.add_paragraph()
        p.text = f"• {it}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Box 3: FEVER Fact Verification
    add_card(slide, Inches(0.8), top_r2, card_w, card_h)
    tb3 = slide.shapes.add_textbox(Inches(1.0), top_r2 + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.3))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "3. EGRESS GROUNDING: FEVER (1,000 SAMPLES)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    items3 = [
        "Composition: 500 Supported (Entailed) claims and 500 Refuted (Contradicted) claims.",
        "Benchmark Characteristics: Human-verified Wikipedia evidence paired with declarative factual claims.",
        "Evaluation Metric: Stage 2 NLI achieves 86.5% accuracy and 0.950 AUROC on FEVER.",
        "Role in Pipeline: Verifies high-confidence declarative assertions against external retrieved context."
    ]
    for it in items3:
        p = tf3.add_paragraph()
        p.text = f"• {it}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Box 4: HaluEval with Length Controls
    add_card(slide, Inches(6.8), top_r2, card_w, card_h)
    tb4 = slide.shapes.add_textbox(Inches(7.0), top_r2 + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.3))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    p = tf4.paragraphs[0]
    p.text = "4. EGRESS GROUNDING: HALUEVAL QA & SUMMARIZATION (2,000 SAMPLES)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER
    items4 = [
        "Composition: 1,000 QA fact-grounded pairs and 1,000 Dialogue/Summarization pairs.",
        "Crucial Methodological Fix: Raw HaluEval exhibits character-length confounders (12.5 vs 58 chars).",
        "Declarative Statement Restructuring: Transformed bare entities into full declarative statements.",
        "Significance: Ensures NLI models judge factual consistency rather than token length shortcuts."
    ]
    for it in items4:
        p = tf4.add_paragraph()
        p.text = f"• {it}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Bottom Footer note
    lbl_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(11.7), Inches(0.3))
    tf_lbl = lbl_box.text_frame
    p_l = tf_lbl.paragraphs[0]
    p_l.text = "All reported splits utilize rigorous 95% Wilson Score confidence intervals and strict seed isolation to prevent data leakage."
    p_l.font.name = FONT_BODY
    p_l.font.size = Pt(10)
    p_l.font.italic = True
    p_l.font.color.rgb = COLOR_TEXT_MUTED


def build_slide_6_results_prescan(prs, assets_dir):
    """Slide 6: 4) Results — Quantitative Pre-Scan Performance (V3 Mega Suite)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_SLATE_BG)

    add_header(
        slide,
        "4. RESULTS | STAGE 1 PRE-SCAN EVALUATION",
        "Empirical Pre-Scan Ingress Performance (V3 Mega Suite)",
        "698 Unseen Test Samples | 98.42% Accuracy | 13.09 ms Median Latency on CUDA"
    )

    # Left Container: Confusion Matrix Image
    add_card(slide, Inches(0.8), Inches(1.85), Inches(5.8), Inches(5.15))
    cm_path = os.path.join(assets_dir, "confusion_matrix_698.png")
    if os.path.exists(cm_path):
        slide.shapes.add_picture(cm_path, Inches(0.95), Inches(2.1), width=Inches(5.5))
    
    # Label under image
    lbl_b = slide.shapes.add_textbox(Inches(0.95), Inches(6.3), Inches(5.5), Inches(0.6))
    tf_lbl = lbl_b.text_frame
    tf_lbl.word_wrap = True
    p = tf_lbl.paragraphs[0]
    p.text = "Exact Log Verification: 347 TP, 340 TN, 3 FP, 8 FN. FPR is constrained to 0.87% (3 false alarms in 343 safe prompts)."
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MUTED

    # Right Container: KPI Metric Grid
    right_left = Inches(6.8)
    right_w = Inches(5.7)

    # 4 Stat Cards (2x2 Grid)
    kpis = [
        ("98.42%", "Overall Accuracy", "687 of 698 correct", COLOR_BLUE_TECH),
        ("99.14%", "Precision (Reliability)", "347 / (347 + 3)", COLOR_GREEN),
        ("97.75%", "Recall (Attack Coverage)", "Catches 347 of 355", COLOR_BLUE_DARK),
        ("0.87%", "False Positive Rate", "Only 3 false alarms", COLOR_AMBER)
    ]
    for idx, (val, title, sub, col) in enumerate(kpis):
        r = idx // 2
        c = idx % 2
        c_left = right_left + c * Inches(2.9)
        c_top = Inches(1.85) + r * Inches(1.3)
        add_card(slide, c_left, c_top, Inches(2.8), Inches(1.2))
        
        tb = slide.shapes.add_textbox(c_left + Inches(0.15), c_top + Inches(0.1), Inches(2.5), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.name = FONT_HEADING
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = col

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_TEXT_MAIN

        p_s = tf.add_paragraph()
        p_s.text = sub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(9)
        p_s.font.color.rgb = COLOR_TEXT_MUTED

    # Analytical Summary Card
    add_card(slide, right_left, Inches(4.6), right_w, Inches(2.4))
    tb_sum = slide.shapes.add_textbox(right_left + Inches(0.2), Inches(4.7), right_w - Inches(0.4), Inches(2.2))
    tf_sum = tb_sum.text_frame
    tf_sum.word_wrap = True
    
    p = tf_sum.paragraphs[0]
    p.text = "KEY ANALYTICAL TAKEAWAYS:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_DARK

    takeaways = [
        "Negligible False Alarms: 99.13% Specificity ensures normal user traffic is never hindered by false rejections.",
        "Sub-15ms Latency: Median latency of 13.09 ms (p50) enables transparent inline integration in sub-second microservices.",
        "Sliding Window Robustness: 256-token chunking with 128 stride detects long-context obfuscated payload injections.",
        "Rigorous Confidence Intervals: 98.42% accuracy holds a tight 95% Wilson score interval of [97.18%, 99.17%]."
    ]
    for tk in takeaways:
        p = tf_sum.add_paragraph()
        p.text = f"• {tk}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN


def build_slide_7_results_entropy(prs, assets_dir):
    """Slide 7: 4) Results — Live Dynamic Token Entropy Stream."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_SLATE_BG)

    add_header(
        slide,
        "4. RESULTS | LIVE TOKEN ENTROPY STREAMING",
        "Dynamic Uncertainty Profiling During Autoregressive Decoding",
        "Empirical Token Stream on Qwen2.5-3B-Instruct | Real-Time Shannon Entropy H(x) Calculation"
    )

    # Top Half: Embedded Chart
    add_card(slide, Inches(0.8), Inches(1.85), Inches(11.7), Inches(2.45))
    ent_path = os.path.join(assets_dir, "entropy_stream_qwen.png")
    if os.path.exists(ent_path):
        slide.shapes.add_picture(ent_path, Inches(1.0), Inches(1.95), width=Inches(11.3))

    # Bottom Half: Two Columns
    # Left: Empirical Token Table
    add_card(slide, Inches(0.8), Inches(4.45), Inches(6.8), Inches(2.55))
    tb_tbl = slide.shapes.add_textbox(Inches(1.0), Inches(4.55), Inches(6.4), Inches(2.35))
    tf_tbl = tb_tbl.text_frame
    tf_tbl.word_wrap = True

    p = tf_tbl.paragraphs[0]
    p.text = "EMPIRICAL STREAM LOG: Prompt: 'What is the capital of India?'"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_TECH

    stream_rows = [
        ("Token", "Top-3 Probabilities", "Entropy H(x)", "Status"),
        ("'The'", "[1.0000, 0.0000, 0.0000]", "0.0000 bits", "OK (Deterministic)"),
        ("' capital'", "[1.0000, 0.0000, 0.0000]", "0.0000 bits", "OK (Deterministic)"),
        ("' of India is'", "[1.0000, 0.0000, 0.0000]", "0.0000 bits", "OK (Deterministic)"),
        ("' New'", "[0.9481, 0.0518, 0.0001]", "0.2955 bits", "OK (High Confidence)"),
        ("' Delhi.'", "[0.9996, 0.0002, 0.0002]", "0.0055 bits", "OK (Factual Grounded)"),
        ("'<|im_end|>'", "[0.9994, 0.0005, 0.0001]", "0.0000 bits", "COMPLETE")
    ]
    for row in stream_rows:
        p = tf_tbl.add_paragraph()
        if row[0] == "Token":
            p.text = f"{row[0]:<14} {row[1]:<24} {row[2]:<14} {row[3]}"
            p.font.name = "Consolas"
            p.font.size = Pt(9)
            p.font.bold = True
            p.font.color.rgb = COLOR_TEXT_MAIN
        else:
            p.text = f"{row[0]:<14} {row[1]:<24} {row[2]:<14} {row[3]}"
            p.font.name = "Consolas"
            p.font.size = Pt(8.5)
            p.font.color.rgb = COLOR_GREEN if "OK" in row[3] or "COMPLETE" in row[3] else COLOR_TEXT_MAIN

    # Right: Mechanics & Early Termination Card
    add_card(slide, Inches(7.8), Inches(4.45), Inches(4.7), Inches(2.55))
    tb_m = slide.shapes.add_textbox(Inches(8.0), Inches(4.55), Inches(4.3), Inches(2.35))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True

    p = tf_m.paragraphs[0]
    p.text = "DYNAMIC ENTROPY CIRCUIT BREAKER"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    points_m = [
        ("Mathematical Formulation:", "Entropy H(x) = -Σ p_i log2(p_i) computed in real-time from next-token logits."),
        ("Calibrated Threshold:", "A 1.35-bit threshold separates factual recall from speculative confabulation."),
        ("Factual Grounding Baseline:", "Grounded facts produce tight distributions (H < 0.3 bits)."),
        ("Proactive Circuit Breaker:", "If sustained entropy exceeds 1.35 bits across a 3-token buffer, EARLY_TERMINATION triggers instantly."),
        ("Bandwidth & Compute Savings:", "Stops streaming immediately, preventing hallucinations from reaching user.")
    ]
    for h, b in points_m:
        p = tf_m.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MAIN


def build_slide_8_results_latency(prs, assets_dir):
    """Slide 8: 4) Results — Hardware Latency Profiling & Compute Savings."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_SLATE_BG)

    add_header(
        slide,
        "4. RESULTS | HARDWARE LATENCY & COMPUTE SAVINGS",
        "Benchmarking Compute Avoidance Across Generative Backbones",
        "Up to 99.62% Latency Reduction on Adversarial Queries | 100% GPU Decoding Compute Saved"
    )

    # Left Half: Chart
    add_card(slide, Inches(0.8), Inches(1.85), Inches(5.8), Inches(5.15))
    lat_path = os.path.join(assets_dir, "latency_compute_savings.png")
    if os.path.exists(lat_path):
        slide.shapes.add_picture(lat_path, Inches(0.95), Inches(2.1), width=Inches(5.5))
    
    lbl_b = slide.shapes.add_textbox(Inches(0.95), Inches(6.1), Inches(5.5), Inches(0.8))
    tf_lbl = lbl_b.text_frame
    tf_lbl.word_wrap = True
    p = tf_lbl.paragraphs[0]
    p.text = "Inference Latency Profile (Log Scale): While unprotected generation scales exponentially with model size (175 ms to 3,420 ms), GuardShield intercepts ingress in a flat 12.87 ms pass."
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_MUTED

    # Right Half: Table + Takeaways
    right_left = Inches(6.8)
    right_w = Inches(5.7)

    # Structured Table
    add_card(slide, right_left, Inches(1.85), right_w, Inches(2.75))
    
    # Add PowerPoint Table
    table_shape = slide.shapes.add_table(5, 5, right_left + Inches(0.1), Inches(1.95), right_w - Inches(0.2), Inches(2.55))
    table = table_shape.table
    table.columns[0].width = Inches(1.4)
    table.columns[1].width = Inches(0.9)
    table.columns[2].width = Inches(1.1)
    table.columns[3].width = Inches(1.0)
    table.columns[4].width = Inches(1.1)

    headers = ["Model", "Params", "Unprotected", "GuardShield", "Latency Red."]
    for col_idx, h_text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h_text
        p = cell.text_frame.paragraphs[0]
        p.font.name = FONT_HEADING
        p.font.size = Pt(9)
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY_DARK
        p.font.color.rgb = COLOR_WHITE

    rows_data = [
        ("GPT-2 Base", "124M", "175.4 ms", "12.87 ms", "92.66%"),
        ("TinyLlama", "1.1B", "740.2 ms", "12.87 ms", "98.26%"),
        ("Qwen2.5-3B", "3.0B", "1,850.6 ms", "12.87 ms", "99.30%"),
        ("Qwen2.5-7B", "7.6B", "3,420.0 ms", "12.87 ms", "99.62%")
    ]
    for row_idx, r_data in enumerate(rows_data):
        for col_idx, val in enumerate(r_data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_BODY
            p.font.size = Pt(8.5)
            p.alignment = PP_ALIGN.CENTER
            if col_idx == 4:
                p.font.bold = True
                p.font.color.rgb = COLOR_GREEN
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if row_idx % 2 == 1 else COLOR_WHITE

    # Key Takeaways Box
    add_card(slide, right_left, Inches(4.75), right_w, Inches(2.25))
    tb_t = slide.shapes.add_textbox(right_left + Inches(0.2), Inches(4.85), right_w - Inches(0.4), Inches(2.05))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True

    p = tf_t.paragraphs[0]
    p.text = "CRITICAL EFFICIENCY FINDINGS:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_DARK

    eff_points = [
        ("100% GPU Decoding Compute Saved:", "Zero autoregressive tokens are computed for blocked attacks, completely eliminating GPU memory bandwidth bottlenecks."),
        ("Constant Pre-Scan Complexity:", "Stage 1 operates in ~12.87 ms regardless of whether the downstream model is 124M or 70B parameters."),
        ("Token Waste Prevention:", "Stops 48 to 120 wasted tokens per adversarial query that would otherwise consume server clusters."),
        ("Production Scalability:", "Enables 10x higher concurrent user capacity per server node by shedding malicious traffic at ingress.")
    ]
    for h, b in eff_points:
        p = tf_t.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN


def build_slide_9_research_literature(prs):
    """Slide 9: 6) Research Foundation & Literature Survey."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_SLATE_BG)

    add_header(
        slide,
        "6. RESEARCH FOUNDATION & LITERATURE SURVEY",
        "Comparative Analysis against Existing Guardrail Paradigms",
        "Synthesized from 18+ Peer-Reviewed Publications across 5 Specialized Research Axes"
    )

    top_pos = Inches(1.85)
    col_w = Inches(5.65)
    col_h = Inches(5.15)

    # Left Column: The 5 Research Axes
    add_card(slide, Inches(0.8), top_pos, col_w, col_h)
    tb_l = slide.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.25), col_w - Inches(0.4), col_h - Inches(0.5))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "THEORETICAL FOUNDATION: 5 RESEARCH AXES"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_DARK

    lit_axes = [
        ("1. Ingress Injection & Jailbreaking", "Perez & Ribeiro (2022), Chao et al. (JailbreakBench, 2024), Wallace et al. (Universal Adversarial Triggers). Identifies prompt leaking and delimiter evasion."),
        ("2. Factual Hallucination Detection", "Manakul et al. (SelfCheckGPT, 2023), Min et al. (FActScore, EMNLP 2023). Demonstrates limitations of stochastic sampling and prompt scoring."),
        ("3. Token Uncertainty & Entropy", "Malinin & Gales (Predictive Uncertainty, 2021), Kuhn et al. (Semantic Entropy, 2023). Establishes token distribution dispersion as a proxy for confabulation."),
        ("4. Commercial Guardrail Frameworks", "Inan et al. (Meta Llama Guard, 2023), Rebedea et al. (NVIDIA NeMo Guardrails, 2023). Demonstrates high computational and latency overheads."),
        ("5. Sidecar Microservices MLOps", "Burns et al. (Design Patterns for Containerized Microservices, ACM 2018). Provides foundation for decoupled, non-invasive proxy inspection.")
    ]
    for h, b in lit_axes:
        p = tf_l.add_paragraph()
        p.text = f"• {h}: {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Right Column: Comparative Matrix Table
    add_card(slide, Inches(6.8), top_pos, col_w, col_h)
    tb_r = slide.shapes.add_textbox(Inches(7.0), top_pos + Inches(0.25), col_w - Inches(0.4), col_h - Inches(0.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "COMPETITIVE BENCHMARK: GUARDSHIELD VS. SOTA"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_TECH

    # Add Table
    t_shape = slide.shapes.add_table(5, 4, Inches(6.9), top_pos + Inches(0.7), col_w - Inches(0.2), Inches(2.2))
    tbl = t_shape.table
    tbl.columns[0].width = Inches(1.6)
    tbl.columns[1].width = Inches(1.1)
    tbl.columns[2].width = Inches(1.3)
    tbl.columns[3].width = Inches(1.4)

    sota_headers = ["Paradigm", "Latency", "Compute Cost", "Architectural Fit"]
    for c_i, h in enumerate(sota_headers):
        cell = tbl.cell(0, c_i)
        cell.text = h
        p = cell.text_frame.paragraphs[0]
        p.font.name = FONT_HEADING
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY_DARK

    sota_rows = [
        ("Llama Guard 3 (8B)", "1,500 – 3,500 ms", "16 GB VRAM", "Heavy In-Line Model"),
        ("NeMo Guardrails", "200 – 800 ms", "Moderate", "Colang Configs"),
        ("SelfCheckGPT", "2,000 – 5,000 ms", "5x-10x Multi-sample", "Offline Evaluation"),
        ("GuardShield AI (Ours)", "13.09 ms (p50)", "< 2 GB VRAM", "Asymmetric Sidecar")
    ]
    for r_i, row in enumerate(sota_rows):
        for c_i, val in enumerate(row):
            cell = tbl.cell(r_i + 1, c_i)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_BODY
            p.font.size = Pt(8.5)
            p.alignment = PP_ALIGN.CENTER
            if r_i == 3: # Ours
                p.font.bold = True
                p.font.color.rgb = COLOR_GREEN
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(236, 253, 245)
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if r_i % 2 == 1 else COLOR_WHITE

    # Key Differentiation
    tb_diff = slide.shapes.add_textbox(Inches(7.0), top_pos + Inches(3.1), col_w - Inches(0.4), Inches(1.8))
    tf_diff = tb_diff.text_frame
    tf_diff.word_wrap = True

    p = tf_diff.paragraphs[0]
    p.text = "CORE ARCHITECTURAL DIFFERENTIATION:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    diffs = [
        "Zero Decoding Overhead: Intercepts malicious inputs before any generative tokens are computed.",
        "Non-Invasive Deployment: Compatible with existing LangChain, LlamaIndex, and vLLM infrastructures without changing prompts.",
        "Hardware-Agnostic: Runs efficiently on commodity GPUs, Cloud TPUs (v5e-1), or CPU microservices."
    ]
    for d in diffs:
        p = tf_diff.add_paragraph()
        p.text = f"• {d}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN


def build_slide_10_conclusion_roadmap(prs):
    """Slide 10: Conclusion & Milestone Execution Roadmap."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide, COLOR_SLATE_BG)

    add_header(
        slide,
        "CONCLUSION & ROADMAP",
        "Project Milestones, Deliverables & Next Steps",
        "Progressive Execution of Amity ASET B.Tech Minor Project (Weeks 1 through 12)"
    )

    top_pos = Inches(1.85)
    col_w = Inches(5.65)
    col_h = Inches(4.3)

    # Left Column: Completed Milestones (W1 - W10)
    add_card(slide, Inches(0.8), top_pos, col_w, col_h)
    tb_l = slide.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.25), col_w - Inches(0.4), col_h - Inches(0.5))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "COMPLETED MILESTONES (WEEKS 1 – 10)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    completed = [
        ("W1–W3 (Problem Formulation & Literature):", "Completed 18-paper survey, defined threat taxonomy, and formalized dual-stage architecture."),
        ("W4–W5 (Dataset Engineering & Curation):", "Curated 5,948 samples across Deepset, JailbreakBench, FEVER, and length-controlled HaluEval."),
        ("W6–W7 (Stage 1 Classifier Fine-Tuning):", "Trained DeBERTa-v3 with sliding window chunking; attained 98.42% accuracy and 13.09 ms latency."),
        ("W8–W9 (Dynamic Entropy & Stage 2 NLI):", "Integrated live Shannon entropy streaming on Qwen2.5-3B; verified declarative NLI fact checking."),
        ("W10 (Mega Evaluation & Progress Reporting):", "Compiled empirical metrics, Wilson CIs, hardware latency profilers, and formal Amity reports.")
    ]
    for h, b in completed:
        p = tf_l.add_paragraph()
        p.text = f"✅  {h} {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Right Column: Upcoming Roadmap (W11 - W12)
    add_card(slide, Inches(6.8), top_pos, col_w, col_h)
    tb_r = slide.shapes.add_textbox(Inches(7.0), top_pos + Inches(0.25), col_w - Inches(0.4), col_h - Inches(0.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "UPCOMING WORK & PRODUCTION ROADMAP (WEEKS 11 – 12)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE_TECH

    upcoming = [
        ("W11: Async FastAPI Microservice & Sidecar Dockerization", "Package Stage 1 and Stage 2 as an asynchronous Docker sidecar container with non-blocking streaming response queues."),
        ("W11: ONNX Runtime & TensorRT-LLM Acceleration", "Quantize Stage 1 to INT8/FP8 to push pre-scan classification latency below 5.0 ms on edge and enterprise nodes."),
        ("W12: Multi-Agent & Enterprise Gateway Demo", "Integrate GuardShield with multi-agent orchestration frameworks (LangChain, AutoGen) and deploy live interactive demo."),
        ("W12: Final Dissertation & Academic Publication", "Finalize Minor Project dissertation, open-source model weights, and prepare manuscript for peer-reviewed conference submission.")
    ]
    for h, b in upcoming:
        p = tf_r.add_paragraph()
        p.text = f"⏳  {h} {b}"
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_MAIN

    # Bottom Sign-Off Banner
    add_card(slide, Inches(0.8), Inches(6.3), Inches(11.7), Inches(0.75), COLOR_NAVY_DARK, COLOR_BLUE_TECH)
    tb_sign = slide.shapes.add_textbox(Inches(1.0), Inches(6.35), Inches(11.3), Inches(0.65))
    tf_sign = tb_sign.text_frame
    tf_sign.word_wrap = True
    p_sign = tf_sign.paragraphs[0]
    p_sign.text = "GuardShield AI — Project Review 2 | Amity School of Engineering & Technology (ASET)"
    p_sign.font.name = FONT_HEADING
    p_sign.font.size = Pt(11)
    p_sign.font.bold = True
    p_sign.font.color.rgb = COLOR_WHITE
    p_sub = tf_sign.add_paragraph()
    p_sub.text = "Thank You. Questions & Discussion. | Team: Shourya Solanki, Rachit Ryan Chug, Dhruv Raj Singh | Guide: Dr. Abhishek Kaushal"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(10)
    p_sub.font.color.rgb = RGBColor(147, 197, 253)


# ------------------------------------------------------------------------------
# Main Presentation Builder
# ------------------------------------------------------------------------------

def build_presentation():
    print("=" * 80)
    print("  [GuardShield AI] Generating High-Impact 16:9 Academic Presentation Deck")
    print("=" * 80)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    base_dir = Path(__file__).resolve().parent.parent
    assets_dir = base_dir / "docs" / "04 Diagrams" / "presentation"

    print("Building slides...")
    build_slide_1_title(prs)
    build_slide_2_intro(prs)
    build_slide_3_problem_solution(prs)
    build_slide_4_models_pipeline(prs)
    build_slide_5_datasets(prs)
    build_slide_6_results_prescan(prs, str(assets_dir))
    build_slide_7_results_entropy(prs, str(assets_dir))
    build_slide_8_results_latency(prs, str(assets_dir))
    build_slide_9_research_literature(prs)
    build_slide_10_conclusion_roadmap(prs)

    # Output paths
    docs_dir = base_dir / "docs" / "01 Reports"
    docs_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir = Path.home() / "Downloads"

    pptx_path_docs = docs_dir / "GuardShield_AI_Presentation.pptx"
    pdf_path_docs = docs_dir / "GuardShield_AI_Presentation.pdf"

    pptx_path_dl = downloads_dir / "GuardShield_AI_Presentation.pptx"
    pdf_path_dl = downloads_dir / "GuardShield_AI_Presentation.pdf"

    # Save PPTX
    prs.save(str(pptx_path_docs))
    if downloads_dir.exists():
        prs.save(str(pptx_path_dl))
    print(f"✅ Saved Presentation PPTX at:\n   - {pptx_path_docs}\n   - {pptx_path_dl}")

    # Export to PDF via PowerPoint COM Automation
    try:
        import win32com.client
        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        presentation = ppt_app.Presentations.Open(str(pptx_path_docs.resolve()), WithWindow=False)
        presentation.SaveAs(str(pdf_path_docs.resolve()), 32) # 32 = ppSaveAsPDF
        presentation.Close()
        ppt_app.Quit()

        if downloads_dir.exists():
            shutil.copy(str(pdf_path_docs), str(pdf_path_dl))
        print(f"✅ Successfully converted and saved Presentation PDF at:\n   - {pdf_path_docs}\n   - {pdf_path_dl}")
    except Exception as e:
        print(f"⚠️ Note during PowerPoint PDF conversion: {e}")

if __name__ == "__main__":
    build_presentation()
