import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_wpr_docx():
    doc = docx.Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    TITLE_COLOR = RGBColor(15, 32, 67)
    SUB_COLOR = RGBColor(70, 80, 95)
    BORDER_COLOR_HEX = '4A5568'
    HEADER_BG_HEX = '1A365D'

    def set_cell_background(cell, fill_color):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def set_table_borders(table):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR_HEX}"/>'
            f'<w:left w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR_HEX}"/>'
            f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR_HEX}"/>'
            f'<w:right w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR_HEX}"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
            f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    # Title Header
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_inst = p_inst.add_run('AMITY SCHOOL OF ENGINEERING & TECHNOLOGY')
    run_inst.font.name = 'Calibri'
    run_inst.font.size = Pt(16)
    run_inst.font.bold = True
    run_inst.font.color.rgb = TITLE_COLOR

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run('B.Tech (CSE - AIML) VII Semester | Session: 2026–2027\nGroup No.: 50 | Project Area: Generative AI & AI Safety (Trustworthy AI / MLOps)')
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(11)
    run_sub.font.color.rgb = SUB_COLOR

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(12)
    run_t = p_title.add_run('STUDENTS WEEKLY PROGRESS REPORT (WPR — WEEK 1)')
    run_t.font.name = 'Calibri'
    run_t.font.size = Pt(14)
    run_t.font.bold = True
    run_t.font.color.rgb = TITLE_COLOR

    # Table 0: Student Fill Section
    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    rows_data = [
        ('To be filled by Students', 'DETAILS & WEEK 1 PROGRESS'),
        ('Students Name', '1. Shourya Solanki\n2. Rachit Ryan Chug\n3. Dhruv Raj Singh'),
        ('Roll no.', '1. 01\n2. 02\n3. 03'),
        ('Enrollment no.', '1. A2305223569\n2. A2305223166\n3. A2305223191'),
        ('Project Title finalized, if Yes, give name, if NO, give reason', 'YES.\n"GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense"'),
        ('Synopsis submitted', 'YES. (Submitted for Group No. 50 under Project Guide: Dr. Abhishek Kaushal)'),
        ('Literature review', 
         'COMPLETED (6 Peer-Reviewed Key Benchmark Papers Analyzed):\n'
         '1. Manakul et al. (EMNLP 2023) — SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection. (Identified Gap: 1-3s offline sampling delay; unfeasible for live streaming).\n'
         '2. Chao et al. (NeurIPS 2024) — JailbreakBench: Open Robustness Benchmark for LLMs.\n'
         '3. Inan et al. (Meta AI 2024) — Llama Guard: Input-Output Safeguard for Human-AI Conversations. (Identified Gap: 8B parameter model is too heavy for sub-25ms sidecar proxy deployment).\n'
         '4. Li et al. (EMNLP 2023) — HaluEval: Large-Scale Hallucination Evaluation Benchmark.\n'
         '5. Zhang et al. (ACL 2025) — CAPTURE: Context-Aware Prompt Injection Benchmark.\n'
         '6. Lin et al. (ACL 2022) — TruthfulQA: Measuring How Models Mimic Human Falsehoods.\n\n'
         'Research Gap Solved: GuardShield AI introduces mid-sentence token logit entropy monitoring with an 86M DeBERTa-v3 model to achieve sub-25ms pre-scan and post-scan streaming defense.'),
        ('Technical & Economical Feasibility',
         'TECHNICAL FEASIBILITY: HIGH.\n'
         '• Uses PyTorch (MPS/CUDA GPU acceleration), Hugging Face Transformers, DeBERTa-v3-small (86M SLM), and Ollama (Llama-3.1-8B) with FastAPI async SSE streaming.\n\n'
         'ECONOMICAL FEASIBILITY: 100% ZERO-COST (₹0).\n'
         '• Software-only stack; runs locally on existing developer hardware (MacBook M4 Pro / RTX 3050). No cloud API or hardware purchases required.'),
        ('Bill of Material', '₹0.00 (Fully open-source software stack and local developer environment)'),
        ('Project Progress Schedule (PERT Chart)',
         'PERFORMANCE & MILESTONE ROADMAP (Weeks 1 – 30):\n'
         '• Weeks 1–3 (Sem 7): Literature Survey, Environment Setup, Ollama & PyTorch MPS/CUDA Configuration [IN PROGRESS / ON SCHEDULE]\n'
         '• Weeks 4–7 (Sem 7): Dataset Concatenation & GuardShield-Bench-v1 Creation [TARGET]\n'
         '• Weeks 8–12 (Sem 7): DeBERTa-v3 Fine-Tuning & Token Logit Entropy Implementation [TARGET]\n'
         '• Weeks 13–16 (Sem 7): Benchmarking Evaluation & IEEE Research Paper Submission [TARGET]\n'
         '• Weeks 17–30 (Sem 8): FastAPI Async Proxy, Red-Agent, Streamlit Dashboard & Docker Demo [TARGET SEM 8]'),
        ('Design of critical components',
         '1. Pre-Scan Filter: Context-aware DeBERTa-v3 multi-class classifier (<25ms latency) detecting prompt injections, jailbreaks, and secret exfiltration.\n'
         '2. Streaming Logit Entropy Inspector: Real-time Shannon Entropy computation H(x) = -sum(p * log(p)) over streaming token distributions.\n'
         '3. Post-Scan Windowed NLI Entailment: Mid-sentence factual validation triggering early token-termination when entropy spikes.\n'
         '4. FastAPI Sidecar Proxy: Async HTTP SSE streaming proxy intercepting LLM traffic.'),
        ('Fabrication work (give %)', 'N/A (Software Project: 0%)'),
        ('Experimental work (give %)', '15% (Environment setup, local LLM integration via Ollama, baseline logit entropy calculation testing)'),
        ('Result and Analysis', 'Literature survey synthesized; hardware benchmarking verified sub-25ms DeBERTa-v3 inference capability on local Apple Silicon MPS & CUDA GPUs.'),
        ('Report writing', 'Project Synopsis submitted. WPR Week 1 drafted.'),
        ('Signature of students', '1. Shourya Solanki              2. Rachit Ryan Chug              3. Dhruv Raj Singh')
    ]

    for idx, (label, val) in enumerate(rows_data):
        row = table.add_row()
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.8)
        set_cell_margins(c0, 100, 100, 150, 150)
        set_cell_margins(c1, 100, 100, 150, 150)
        
        if idx == 0:
            set_cell_background(c0, HEADER_BG_HEX)
            set_cell_background(c1, HEADER_BG_HEX)
            p0 = c0.paragraphs[0]
            r0 = p0.add_run(label)
            r0.font.name = 'Calibri'
            r0.font.bold = True
            r0.font.color.rgb = RGBColor(255, 255, 255)
            p1 = c1.paragraphs[0]
            r1 = p1.add_run(val)
            r1.font.name = 'Calibri'
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(255, 255, 255)
        else:
            if idx % 2 == 1:
                set_cell_background(c0, 'F8FAFC')
                set_cell_background(c1, 'F8FAFC')
            else:
                set_cell_background(c0, 'FFFFFF')
                set_cell_background(c1, 'FFFFFF')
                
            p0 = c0.paragraphs[0]
            r0 = p0.add_run(label)
            r0.font.name = 'Calibri'
            r0.font.bold = True
            r0.font.size = Pt(10)
            r0.font.color.rgb = TITLE_COLOR
            
            p1 = c1.paragraphs[0]
            r1 = p1.add_run(val)
            r1.font.name = 'Calibri'
            r1.font.size = Pt(9.5)
            r1.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Section: Work Done In This Week
    p_w_head = doc.add_paragraph()
    r_w_head = p_w_head.add_run('WORK DONE IN THIS WEEK (WEEK 1):')
    r_w_head.font.name = 'Calibri'
    r_w_head.font.bold = True
    r_w_head.font.size = Pt(11)
    r_w_head.font.color.rgb = TITLE_COLOR

    work_items = [
        '1. Development Environment Setup: Installed Python 3.11+, PyTorch (MPS/CUDA), Hugging Face Transformers, Datasets, FastAPI, and configured local Ollama with Llama-3.1-8B.',
        '2. Title & Domain Finalization: Finalized project title "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense" in the domain of Generative AI & AI Safety.',
        '3. Literature Review & Gap Identification: Completed in-depth review of 6 key research papers (SelfCheckGPT, JailbreakBench, Llama Guard, HaluEval, CAPTURE, TruthfulQA), identifying the sub-25ms latency gap in streaming guardrails.',
        '4. Architectural Design & PERT Schedule: Formulated the dual-stage proxy architecture (Pre-Scan DeBERTa classifier + Post-Scan Token Logit Entropy NLI) and 30-week project schedule across Sem 7 and Sem 8.',
        '5. Synopsis Submission: Prepared and formally submitted the Project Synopsis for Group No. 50 to project guide Dr. Abhishek Kaushal.'
    ]

    for item in work_items:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.left_indent = Inches(0.2)
        p_item.paragraph_format.space_after = Pt(3)
        r_item = p_item.add_run(item)
        r_item.font.name = 'Calibri'
        r_item.font.size = Pt(9.5)
        r_item.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Table 1: Guide Section
    table_g = doc.add_table(rows=0, cols=1)
    table_g.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_g)

    guide_rows = [
        ('To be filled by Guide (strike off whichever is not applicable)', True),
        ('Performance of students is satisfactory', False),
        ('Performance of students is unsatisfactory', False),
        ('A warning to be issued to student(s) (Name): ____________________________________', False),
        ('Student was not well (Name): ____________________________________', False),
        ('Date: ________________________                            Signature of Guide: ________________________', False)
    ]

    for g_label, is_head in guide_rows:
        row = table_g.add_row()
        cell = row.cells[0]
        cell.width = Inches(7.0)
        set_cell_margins(cell, 100, 100, 150, 150)
        if is_head:
            set_cell_background(cell, HEADER_BG_HEX)
            p = cell.paragraphs[0]
            r = p.add_run(g_label)
            r.font.name = 'Calibri'
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            p = cell.paragraphs[0]
            r = p.add_run(g_label)
            r.font.name = 'Calibri'
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(30, 41, 59)

    out_path = r'd:\projects\GuardShield_AI\GuardShield_AI_WPR_Week_1.docx'
    doc.save(out_path)
    print(f'Successfully generated {out_path}')

if __name__ == '__main__':
    create_wpr_docx()
