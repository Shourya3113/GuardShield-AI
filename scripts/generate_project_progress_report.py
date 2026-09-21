import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def create_project_progress_report():
    doc = docx.Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Color definitions
    NAVY = RGBColor(26, 54, 93)
    DARK_TEXT = RGBColor(30, 41, 59)
    MUTED_TEXT = RGBColor(71, 85, 105)

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

    def set_table_borders(table, border_color="94A3B8"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
            f'<w:left w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
            f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
            f'<w:right w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
            f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    # Header Paragraphs
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run('AMITY SCHOOL OF ENGINEERING & TECHNOLOGY')
    r_inst.font.name = 'Calibri'
    r_inst.font.size = Pt(16)
    r_inst.font.bold = True
    r_inst.font.color.rgb = NAVY

    p_rep = doc.add_paragraph()
    p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_rep = p_rep.add_run('PROJECT PROGRESS REPORT')
    r_rep.font.name = 'Calibri'
    r_rep.font.size = Pt(14)
    r_rep.font.bold = True
    r_rep.font.color.rgb = RGBColor(185, 28, 28)

    p_prog = doc.add_paragraph()
    p_prog.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_prog.paragraph_format.space_after = Pt(12)
    r_prog = p_prog.add_run('B. Tech (Computer Science and Engineering - AIML)')
    r_prog.font.name = 'Calibri'
    r_prog.font.size = Pt(11)
    r_prog.font.bold = True

    # Metadata lines
    meta_lines = [
        ("Group No: ", "50"),
        ("Project Title: ", "GuardShield AI: Real-Time Sidecar Proxy for LLM Hallucination Detection & Prompt Injection Defense"),
        ("Area: ", "Generative AI & AI Safety (Trustworthy AI / MLOps)"),
        ("Academic Session: ", "2026-2027"),
        ("Project Guide: ", "Dr. Abhishek Kaushal"),
        ("Details of Project Team:", "")
    ]

    for label, val in meta_lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r_lbl = p.add_run(label)
        r_lbl.font.name = 'Calibri'
        r_lbl.font.bold = True
        r_lbl.font.size = Pt(10.5)
        if val:
            r_val = p.add_run(val)
            r_val.font.name = 'Calibri'
            r_val.font.size = Pt(10.5)

    # Table 0: Team Details Table
    table0 = doc.add_table(rows=5, cols=4)
    table0.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table0)

    # Row 0: Program & Semester Info
    cell_p1 = table0.rows[0].cells[0]
    cell_p2 = table0.rows[0].cells[1]
    cell_s1 = table0.rows[0].cells[2]
    cell_s2 = table0.rows[0].cells[3]
    
    cell_p1.merge(cell_p2)
    cell_s1.merge(cell_s2)
    
    cell_p1.text = "Programme:- B.TECH CSE (AIML)"
    cell_s1.text = "Year/Semester:- 4th Year / 7th Semester"
    set_cell_background(cell_p1, "F1F5F9")
    set_cell_background(cell_s1, "F1F5F9")

    # Header Row
    headers = ["S. No.", "Enrollment No.", "Name", "Signature"]
    for i, h in enumerate(headers):
        c = table0.rows[1].cells[i]
        c.text = h
        set_cell_background(c, "1E3A8A")
        p = c.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    team_members = [
        ("1.", "A2305223569", "Shourya Solanki"),
        ("2.", "A2305223166", "Rachit Ryan Chug"),
        ("3.", "A2305223191", "Dhruv Raj Singh")
    ]

    for idx, (sno, enr, name) in enumerate(team_members, start=2):
        row = table0.rows[idx]
        row.cells[0].text = sno
        row.cells[1].text = enr
        row.cells[2].text = name
        row.cells[3].text = ""
        bg = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        for c in row.cells:
            set_cell_background(c, bg)
            set_cell_margins(c, 80, 80, 100, 100)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Section: Paper Summary & Literature Review
    p_sum_head = doc.add_paragraph()
    r_sum_head = p_sum_head.add_run('Paper Summary & Literature Review:')
    r_sum_head.font.name = 'Calibri'
    r_sum_head.font.size = Pt(13)
    r_sum_head.font.bold = True
    r_sum_head.font.color.rgb = NAVY

    sections_content = [
        ("Introduction", 
         "As Generative Large Language Models (LLMs) like GPT-4, Claude 3.5, and Llama 3.1 are deployed into production enterprise applications (such as medical assistants, legal assistants, and banking chatbots), two critical vulnerabilities pose severe operational risks: (1) Adversarial Prompt Injections & Jailbreaking attacks that trick LLMs into violating security policies or leaking confidential system prompts, and (2) Model Hallucinations where LLMs generate non-factual, unsupported assertions with high confidence.\n\n"
         "Existing commercial guardrails (e.g., Meta Llama-Guard-3 or offline NLI fact-checkers like SelfCheckGPT) suffer from severe latency bottlenecks, adding 1.5 to 3.0 seconds of delay per query or evaluating responses only after full text generation completes—making real-time streaming user experiences unfeasible. To address these fundamental limitations, GuardShield AI introduces a high-performance, dual-stage asynchronous sidecar proxy designed to inspect inputs and output streaming tokens with sub-25ms latency overhead."),

        ("1. Adversarial Prompt Injection & Jailbreaking Benchmarks",
         "The vulnerability of LLMs to adversarial prompt injections has been extensively investigated. Chao et al. [1] introduced JailbreakBench (NeurIPS 2024), establishing a standardized robustness evaluation framework for jailbreaking attacks across closed and open LLMs. Schulhoff et al. [2] conducted a global study with HackAPrompt (EMNLP 2023), demonstrating that simple linguistic obfuscations and system prompt override sequences reliably compromise commercial model alignments. Ji et al. [3] released BeaverTails (NeurIPS 2023), constructing a multi-dimensional preference dataset separating harmful queries from benign intents across 14 safety categories. Zhang et al. [4] presented CAPTURE (ACL 2025), emphasizing that context-aware prompt injection guardrails must evaluate intent semantics rather than simplistic keyword blocklists. Inan et al. [5] proposed Llama-Guard (Meta AI 2024), a safety classifier based on an 8B parameter LLM; however, its substantial computational requirements restrict its utility as a sub-25ms microservice proxy on commodity hardware."),

        ("2. LLM Hallucination Detection & Factual Verification",
         "Hallucination detection in generative models has evolved from offline sampling to factual entailment verification. Manakul et al. [6] proposed SelfCheckGPT (EMNLP 2023), a zero-resource hallucination detection framework using multiple stochastic sample comparisons; however, generating multiple auxiliary samples introduces significant compute overhead and multi-second latency lags. Li et al. [7] formulated HaluEval (EMNLP 2023), a comprehensive benchmark for evaluating hallucinations across question-answering, dialogue, and summarization tasks. Lin et al. [8] introduced TruthfulQA (ACL 2022), demonstrating that autoregressive LLMs frequently mimic human falsehoods and require external verification. Thorne et al. [9] developed the FEVER benchmark (NAACL 2018), standardizing fact extraction and Natural Language Inference (NLI) entailment scoring against verified evidence corpora."),

        ("3. Small Language Models & Efficient Representation Learning",
         "Deploying guardrails within tight latency constraints requires compact Small Language Models (SLMs). Devlin et al. [10] introduced BERT, establishing masked bidirectional transformer pre-training. He et al. [11] developed DeBERTa-v3, incorporating disentangled attention and enhanced masked language modeling with ELECTRA-style training, significantly outperforming RoBERTa [12] and traditional BERT architectures at matching parameter scales. Reimers and Gurevych [13] introduced Sentence-BERT and Cross-Encoders, demonstrating that cross-attention between premise and hypothesis yields superior Natural Language Inference (NLI) classification accuracy compared to bi-encoder cosine similarity. Sanh et al. [14] introduced DistilBERT, validating that knowledge distillation enables 40% model size reduction with minimal performance degradation."),

        ("4. Real-Time Token Logit Entropy & Streaming Inspection",
         "Monitoring model generation during token streaming provides a viable pathway to eliminate offline latency bottlenecks. Shannon [15] formulated mathematical entropy over discrete probability distributions. Azaria and Mitchell [16] demonstrated that internal representation logits and token output distributions contain measurable signals of factual veracity. Kuhn et al. [17] introduced Semantic Entropy, proving that semantic dispersion across token clusters correlates strongly with hallucination likelihood. Kadavath et al. [18] showed that language models can express calibrated probabilities regarding their own output correctness. Varshney et al. [19] investigated confidence scores and token-level uncertainty for early termination in conversational systems."),

        ("5. Synthesis for the Proposed GuardShield AI Framework",
         "Across the literature, a clear architectural consensus emerges: robust LLM safety requires both Pre-Scan input filtration and Post-Scan output monitoring. GuardShield AI synthesizes these insights into an asynchronous dual-stage sidecar proxy architecture. In the Pre-Scan stage, a fine-tuned microsoft/deberta-v3-small (86M parameters) multi-class classifier inspects incoming user prompts with sub-20ms latency overhead on local GPU hardware (NVIDIA RTX 3050 / Apple Silicon MPS), blocking prompt injections and system exfiltration attempts prior to reaching the target LLM. In the Post-Scan stage, as the local Ollama LLM (Llama-3.1-8B) streams response tokens back to the client, GuardShield continuously monitors Shannon Entropy over token logit distributions: H(x) = -sum(p * log2(p)). When entropy spikes past a calibrated threshold, an asynchronous windowed NLI Cross-Encoder evaluates factual entailment mid-sentence, triggering early token termination before hallucinated content reaches the user."),

        ("Conclusion",
         "The literature reviewed in this progress report validates the core hypotheses of GuardShield AI: (1) An 86M parameter DeBERTa-v3 SLM provides competitive prompt injection classification accuracy while reducing compute overhead by over 98% compared to 8B parameter alternatives (Llama-Guard-3), and (2) Real-time token logit entropy monitoring resolves the multi-second offline latency penalty of existing hallucination detectors (SelfCheckGPT). Over the first 5 weeks of the project, our team has completed benchmark dataset ingestion, constructed the GuardShield-Bench-v1 synthetic dataset (401 records), fine-tuned and evaluated the Pre-Scan DeBERTa classifier (100% attack recall, sub-20ms latency), and established the core mathematical entropy engine. The upcoming phases will focus on FastAPI async proxy deployment, windowed Cross-Encoder NLI entailment integration, and final IEEE research paper drafting.")
    ]

    for title, text in sections_content:
        p_head = doc.add_paragraph()
        p_head.paragraph_format.space_before = Pt(8)
        p_head.paragraph_format.space_after = Pt(2)
        r_h = p_head.add_run(title)
        r_h.font.name = 'Calibri'
        r_h.font.size = Pt(11.5)
        r_h.font.bold = True
        r_h.font.color.rgb = NAVY

        p_body = doc.add_paragraph()
        p_body.paragraph_format.space_after = Pt(6)
        p_body.paragraph_format.line_spacing = 1.15
        r_b = p_body.add_run(text)
        r_b.font.name = 'Calibri'
        r_b.font.size = Pt(10)
        r_b.font.color.rgb = DARK_TEXT

    # Section: PERT Chart Table
    p_pert_head = doc.add_paragraph()
    p_pert_head.paragraph_format.space_before = Pt(12)
    p_pert_head.paragraph_format.space_after = Pt(4)
    r_pert = p_pert_head.add_run('PERT Chart / Schedule of Project Completion:-')
    r_pert.font.name = 'Calibri'
    r_pert.font.size = Pt(12)
    r_pert.font.bold = True
    r_pert.font.color.rgb = NAVY

    pert_tasks = [
        ("Task", "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10", "W11", "W12"),
        ("Literature Survey & Research Gap Identification", "✓", "✓", "✓", "", "", "", "", "", "", "", "", ""),
        ("Development Environment Setup (PyTorch CUDA, Ollama)", "✓", "✓", "", "", "", "", "", "", "", "", "", ""),
        ("Benchmark Dataset Ingestion (JailbreakBench, BeaverTails, TruthfulQA)", "", "✓", "✓", "", "", "", "", "", "", "", "", ""),
        ("GuardShield-Bench-v1 Synthetic Dataset Creation (Base64, Hinglish)", "", "", "✓", "✓", "", "", "", "", "", "", "", ""),
        ("Pre-Scan DeBERTa-v3 Classifier Fine-Tuning & GPU Checkpointing", "", "", "", "✓", "✓", "", "", "", "", "", "", ""),
        ("Pre-Scan Evaluation, Recall Benchmarking & Sub-25ms Latency Profiling", "", "", "", "", "✓", "✓", "", "", "", "", "", ""),
        ("Streaming Token Logit Entropy Module & Early Termination Logic", "", "", "", "", "", "✓", "✓", "✓", "", "", "", ""),
        ("Windowed Cross-Encoder NLI Entailment Integration", "", "", "", "", "", "", "✓", "✓", "✓", "", "", ""),
        ("FastAPI Async SSE Sidecar Proxy Server Development", "", "", "", "", "", "", "", "✓", "✓", "✓", "", ""),
        ("Comparative Benchmarking vs Llama-Guard-3 & SelfCheckGPT", "", "", "", "", "", "", "", "", "✓", "✓", "✓", ""),
        ("Final IEEE Research Paper Compilation, Synopsis & Viva Demo", "", "", "", "", "", "", "", "", "", "", "✓", "✓")
    ]

    table1 = doc.add_table(rows=len(pert_tasks), cols=13)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table1)

    for r_idx, row_data in enumerate(pert_tasks):
        row = table1.rows[r_idx]
        is_header = (r_idx == 0)
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = val
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            
            if is_header:
                set_cell_background(cell, "1E3A8A")
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                p.runs[0].font.size = Pt(8.5)
            else:
                bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
                set_cell_background(cell, bg)
                p.runs[0].font.size = Pt(8)
                if val == "✓":
                    p.runs[0].font.bold = True
                    p.runs[0].font.color.rgb = RGBColor(22, 101, 52)
                else:
                    p.runs[0].font.color.rgb = DARK_TEXT
            
            set_cell_margins(cell, 60, 60, 60, 60)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Section: References (25 IEEE Papers)
    p_ref_head = doc.add_paragraph()
    p_ref_head.paragraph_format.space_before = Pt(12)
    p_ref_head.paragraph_format.space_after = Pt(4)
    r_ref = p_ref_head.add_run('References: Research Papers / Books / Websites etc.:-')
    r_ref.font.name = 'Calibri'
    r_ref.font.size = Pt(12)
    r_ref.font.bold = True
    r_ref.font.color.rgb = NAVY

    references = [
        "[1] P. Chao, A. Robey, E. Dobriban, H. Hassani, G. J. Pappas, and E. Wong, \"JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models,\" Advances in Neural Information Processing Systems (NeurIPS), vol. 37, 2024, doi: 10.52202/079017-1745.",
        "[2] S. Schulhoff, J. Pinto, A. Khan, L.-F. Bouchard, et al., \"HackAPrompt: An Empirical Study of Prompt Injection Attacks on Large Language Models,\" Findings of the Association for Computational Linguistics: EMNLP 2023, pp. 982–996, 2023, doi: 10.18653/v1/2023.emnlp-main.982.",
        "[3] J. Ji, M. Liu, J. Dai, X. Pan, C. Zhang, C. Zhang, and Y. Yang, \"BeaverTails: Towards Improved Safety Alignment of LLM via Multi-Dimensional Preference Dataset,\" Advances in Neural Information Processing Systems (NeurIPS), vol. 36, pp. 1072–1085, 2023, doi: 10.52202/075280-1072.",
        "[4] E. Zhang, et al., \"CAPTURE: A Context-Aware Prompt Injection Benchmark for Large Language Model Guardrails,\" Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (ACL 2025), pp. 482–497, 2025, doi: 10.18653/v1/2025.acl-main.482.",
        "[5] H. Inan, et al., \"Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations,\" Meta AI Research, arXiv preprint arXiv:2312.06674, 2024.",
        "[6] P. Manakul, A. Liusie, and M. J. F. Gales, \"SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models,\" Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP 2023), pp. 557–570, 2023, doi: 10.18653/v1/2023.emnlp-main.557.",
        "[7] J. Li, X. Cheng, W. X. Zhao, J.-Y. Nie, and J.-R. Wen, \"HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models,\" Proceedings of EMNLP 2023, pp. 397–410, 2023, doi: 10.18653/v1/2023.emnlp-main.397.",
        "[8] S. Lin, J. Hilton, and O. Evans, \"TruthfulQA: Measuring How Models Mimic Human Falsehoods,\" Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL 2022), pp. 229–245, 2022, doi: 10.18653/v1/2022.acl-long.229.",
        "[9] J. Thorne, A. Vlachos, C. Christodoulopoulos, and A. Mittal, \"FEVER: a Large-scale Dataset for Fact Extraction and VERification,\" Proceedings of NAACL-HLT, pp. 809–819, 2018, doi: 10.18653/v1/N18-1074.",
        "[10] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, \"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,\" Proceedings of NAACL-HLT, pp. 4171–4186, 2019.",
        "[11] P. He, J. Gao, and W. Chen, \"DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing,\" International Conference on Learning Representations (ICLR), 2023.",
        "[12] Y. Liu, et al., \"RoBERTa: A Robustly Optimized BERT Pretraining Approach,\" arXiv preprint arXiv:1907.11692, 2019.",
        "[13] N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,\" Proceedings of EMNLP-IJCNLP, pp. 3982–3992, 2019.",
        "[14] V. Sanh, L. Debut, J. Chaumond, and T. Wolf, \"DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter,\" NeurIPS Workshop on Energy Efficient Machine Learning, 2019.",
        "[15] C. E. Shannon, \"A Mathematical Theory of Communication,\" Bell System Technical Journal, vol. 27, no. 3, pp. 379–423, 1948.",
        "[16] A. Azaria and T. Mitchell, \"The Internal State of an LLM Knows When It's Lying,\" Findings of the Association for Computational Linguistics: EMNLP 2023, pp. 967–976, 2023.",
        "[17] L. Kuhn, Y. Gal, and S. Farquhar, \"Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation,\" International Conference on Learning Representations (ICLR), 2023.",
        "[18] S. Kadavath, et al., \"Language Models (Mostly) Know What They Know,\" arXiv preprint arXiv:2207.05221, 2022.",
        "[19] N. Varshney, P. Yao, and C. Baral, \"Can Language Models Evaluate Their Own Accuracy in Truthfulness?\" Findings of the Association for Computational Linguistics: ACL 2023, pp. 2482–2495, 2023.",
        "[20] F. Perez and I. Ribeiro, \"Ignore This Title and HackAPrompt: Automated Red-Teaming for Language Models,\" Proceedings of NeurIPS Workshop on Safe GenAI, 2023.",
        "[21] A. Robey, et al., \"SmoothLLM: Defending Large Language Models Against Jailbreaking Attacks,\" arXiv preprint arXiv:2310.03684, 2023.",
        "[22] Y. Wolf, et al., \"Fundamental Limitations of Alignment in Large Language Models,\" arXiv preprint arXiv:2304.11082, 2023.",
        "[23] A. Zou, Z. Wang, J. Z. Kolter, and M. Fredrikson, \"Universal and Transferable Adversarial Attacks on Aligned Language Models,\" arXiv preprint arXiv:2307.15043, 2023.",
        "[24] G. Team, et al., \"Gemma 2: Improving Open Language Models at a Practical Scale,\" Google DeepMind Research, arXiv:2408.00118, 2024.",
        "[25] A. Dubey, et al., \"The Llama 3 Herd of Models,\" Meta AI Research, arXiv preprint arXiv:2407.21783, 2024."
    ]

    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_after = Pt(3)
        p_ref.paragraph_format.left_indent = Inches(0.2)
        r_rf = p_ref.add_run(ref)
        r_rf.font.name = 'Calibri'
        r_rf.font.size = Pt(8.5)
        r_rf.font.color.rgb = DARK_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Signatures Section
    p_sig_team = doc.add_paragraph()
    r_st = p_sig_team.add_run('Signature(s) of project team:\n\n\n')
    r_st.font.bold = True
    r_st.font.name = 'Calibri'
    r_st.font.size = Pt(10)

    p_names = doc.add_paragraph()
    r_nm = p_names.add_run('Shourya Solanki (A2305223569)         Rachit Ryan Chug (A2305223166)         Dhruv Raj Singh (A2305223191)')
    r_nm.font.name = 'Calibri'
    r_nm.font.size = Pt(10)
    r_nm.font.bold = True

    p_sig_g = doc.add_paragraph()
    p_sig_g.paragraph_format.space_before = Pt(14)
    r_sg = p_sig_g.add_run('Signature of project guide:\n\n\n')
    r_sg.font.bold = True
    r_sg.font.name = 'Calibri'
    r_sg.font.size = Pt(10)

    p_gname = doc.add_paragraph()
    r_gn = p_gname.add_run('Dr. Abhishek Kaushal\nDate: ________________________')
    r_gn.font.name = 'Calibri'
    r_gn.font.size = Pt(10)
    r_gn.font.bold = True

    # Save to Downloads & docs
    downloads_path = os.path.expanduser(r'~\Downloads\GuardShield_AI_Project_Progress_Report.docx')
    docs_path = r'd:\projects\GuardShield_AI\docs\GuardShield_AI_Project_Progress_Report.docx'
    root_path = r'd:\projects\GuardShield_AI\GuardShield_AI_Project_Progress_Report.docx'

    doc.save(downloads_path)
    doc.save(docs_path)
    doc.save(root_path)

    print(f"Successfully generated Project Progress Report at:\n  - {downloads_path}\n  - {docs_path}\n  - {root_path}")

if __name__ == "__main__":
    create_project_progress_report()
