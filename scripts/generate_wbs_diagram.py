import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_wbs_diagram():
    # Setup Figure
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')
    
    # Colors matching reference image
    COLOR_PINK = "#D8005A"
    COLOR_LINE = "#D8005A"
    COLOR_DARK_GRAY = "#4A4A4A"
    COLOR_GREEN = "#4CAF50"
    COLOR_YELLOW = "#FFC107"
    COLOR_BG = "#F9F9FB"
    
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)
    
    # 1. Main Project Title Box (Top Center)
    title_box = patches.FancyBboxPatch(
        (3.0, 7.8), 10.0, 0.8,
        boxstyle="round,pad=0.1,rounding_size=0.2",
        linewidth=1, edgecolor=COLOR_PINK, facecolor=COLOR_PINK
    )
    ax.add_patch(title_box)
    ax.text(8.0, 8.2, "Project: GuardShield AI (Minor Project WBS)", 
            color="white", weight="bold", fontsize=16, ha="center", va="center")
    
    # Connector lines from title to level 1 columns
    col_x_centers = [2.1, 6.0, 9.9, 13.8]
    
    # Line from Title down to horizontal spine
    ax.plot([8.0, 8.0], [7.8, 7.2], color=COLOR_LINE, lw=1.5)
    # Horizontal spine connecting 4 columns
    ax.plot([col_x_centers[0], col_x_centers[-1]], [7.2, 7.2], color=COLOR_LINE, lw=1.5)
    
    # Vertical lines down to level 1 boxes
    for cx in col_x_centers:
        ax.plot([cx, cx], [7.2, 6.8], color=COLOR_LINE, lw=1.5)
        
    # Level 1 Column Specifications
    columns_data = [
        {
            "title": "1. Research & Design",
            "x": 0.6, "width": 3.0,
            "items": [
                "1.1 Dual-Stage Proxy Arch",
                "1.2 Threat Model & Policy",
                "1.3 Latency Spec (<25ms)",
                "1.4 Literature Survey"
            ]
        },
        {
            "title": "2. Data Engineering",
            "x": 4.5, "width": 3.0,
            "items": [
                "2.1 Ingest Benchmark Data",
                "2.2 Schema Normalization",
                "2.3 Synthetic Obfuscation",
                "2.4 GuardShield-Bench-v1",
                "2.5 80/10/10 Data Splitting"
            ]
        },
        {
            "title": "3. Core Development",
            "x": 8.4, "width": 3.0,
            "items": [
                "3.1 DeBERTa-v3 SLM (86M)",
                "3.2 Token Logit Entropy",
                "3.3 Windowed NLI Entailment",
                "3.4 Model Fine-Tuning",
                "3.5 FastAPI SSE Proxy"
            ]
        },
        {
            "title": "4. Test & Delivery",
            "x": 12.3, "width": 3.0,
            "items": [
                "4.1 Injection Defense Test",
                "4.2 Hallucination Early Term",
                "4.3 Latency Benchmarking",
                "4.4 WPR & IEEE Report",
                "4.5 Jury Presentation & Viva"
            ]
        }
    ]
    
    # Render Columns
    for col_idx, col in enumerate(columns_data):
        cx = col_x_centers[col_idx]
        x_left = col["x"]
        w = col["width"]
        
        # Level 1 Header Box (Dark Gray)
        h1_box = patches.FancyBboxPatch(
            (x_left, 6.0), w, 0.7,
            boxstyle="round,pad=0.08,rounding_size=0.15",
            linewidth=1, edgecolor=COLOR_DARK_GRAY, facecolor=COLOR_DARK_GRAY
        )
        ax.add_patch(h1_box)
        ax.text(cx, 6.35, col["title"], color="white", weight="bold", fontsize=11, ha="center", va="center")
        
        # Vertical spine connecting header to work package items
        num_items = len(col["items"])
        spine_bottom_y = 6.0 - (num_items * 0.95) + 0.35
        ax.plot([x_left - 0.2, x_left - 0.2], [6.35, spine_bottom_y], color=COLOR_LINE, lw=1.2)
        # Horizontal connecting line from Level 1 header to vertical spine
        ax.plot([x_left, x_left - 0.2], [6.35, 6.35], color=COLOR_LINE, lw=1.2)
        
        # Level 2 Work Package Boxes (Green)
        for item_idx, item_text in enumerate(col["items"]):
            item_y = 5.1 - (item_idx * 0.95)
            
            # Horizontal connector from vertical spine to item box
            ax.plot([x_left - 0.2, x_left], [item_y + 0.3, item_y + 0.3], color=COLOR_LINE, lw=1.2)
            
            wp_box = patches.FancyBboxPatch(
                (x_left, item_y), w, 0.6,
                boxstyle="round,pad=0.08,rounding_size=0.12",
                linewidth=0.8, edgecolor="#388E3C", facecolor=COLOR_GREEN
            )
            ax.add_patch(wp_box)
            ax.text(x_left + (w / 2.0), item_y + 0.3, item_text, 
                    color="white", weight="bold", fontsize=9.5, ha="center", va="center")
            
    # Legend Box at Bottom Right (Yellow/Orange)
    legend_box = patches.FancyBboxPatch(
        (13.2, 0.4), 2.2, 0.7,
        boxstyle="square,pad=0.1",
        linewidth=1, edgecolor="#FFA000", facecolor=COLOR_YELLOW
    )
    ax.add_patch(legend_box)
    ax.text(14.3, 0.7, "Work packages", color="#212121", weight="bold", fontsize=10, ha="center", va="center")
    
    # Save Image to Downloads & Artifacts
    downloads_path = os.path.expanduser(r"~\Downloads\GuardShield_AI_WBS_Diagram.png")
    project_path = r"d:\projects\GuardShield_AI\docs\GuardShield_AI_WBS_Diagram.png"
    
    plt.tight_layout()
    plt.savefig(downloads_path, format="png", bbox_inches="tight", facecolor=COLOR_BG)
    plt.savefig(project_path, format="png", bbox_inches="tight", facecolor=COLOR_BG)
    plt.close()
    
    print(f"Successfully saved WBS Diagram to:\n  - {downloads_path}\n  - {project_path}")

if __name__ == "__main__":
    create_wbs_diagram()
