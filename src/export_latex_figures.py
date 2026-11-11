import os
import csv
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
FIG_DIR = os.path.join(ROOT_DIR, "reports", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def export_pipeline_architecture():
    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 35)

    steps = [
        (4, 5, 20, 24, "1. CRAWLER\n(Category Traversal)", "MediaWiki API\nQuét 342 thể loại\n2.253 wikitexts", "#eff6ff", "#2563eb"),
        (28, 5, 20, 24, "2. TRÍCH XUẤT\n(Infobox & NLP)", "Regex Brace Parser\nEntity Linking\nOpenIE văn bản", "#f0fdf4", "#059669"),
        (52, 5, 20, 24, "3. CHUẨN HÓA\n(Schema Filter)", "Khử 296 hôn nhân rác\nKhử 148 đỉnh ma\nOntology Checking", "#fefce8", "#d97706"),
        (76, 5, 20, 24, "4. ĐẦU RA &\nCSDL ĐỒ THỊ", "CSV: 2.928 N, 21.383 E\nCypher & Python Loader\nPDF Báo cáo Học thuật", "#faf5ff", "#7c3aed")
    ]
    for x, y, w, h, t1, t2, fc, ec in steps:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.5", facecolor=fc, edgecolor=ec, linewidth=1.8)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.68, t1, fontsize=9.5, fontweight='bold', color=ec, ha='center', va='center')
        ax.text(x + w/2, y + h*0.28, t2, fontsize=8.2, color='#475569', ha='center', va='center')

    for x_arr in [24.5, 48.5, 72.5]:
        ax.annotate('', xy=(x_arr + 3.2, 17), xytext=(x_arr - 0.2, 17),
                    arrowprops=dict(facecolor='#64748b', edgecolor='#64748b', arrowstyle="->", lw=2.2))

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "pipeline_architecture.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "pipeline_architecture.png"))
    plt.close(fig)
    print("Exported pipeline_architecture")

def export_edge_distribution():
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
    r_labels = ["CO_STARRED", "ACTED_IN", "DIRECTED_ACTOR", "DIRECTED", "PRODUCED_BY",
                "MARRIED_TO", "PRODUCED", "AFFILIATED", "FOUNDED", "MENTORED"][::-1]
    r_vals = [12912, 4761, 2224, 711, 345, 200, 136, 67, 16, 11][::-1]
    colors = ['#38bdf8', '#38bdf8', '#38bdf8', '#38bdf8', '#fbbf24',
              '#f87171', '#4ade80', '#818cf8', '#a78bfa', '#2563eb'][::-1]

    bars = ax.barh(r_labels, r_vals, color=colors, edgecolor='#64748b', height=0.62)
    ax.set_xscale('log')
    ax.set_xlim(5, 55000)
    ax.set_xlabel("Số lượng cạnh có hướng (Thang đo Logarit)", fontsize=9.5, fontweight='bold', color='#1e293b')
    ax.set_title("Phân Bổ Quy Mô 10 Loại Quan Hệ Ngữ Nghĩa (Tổng cộng 21.383 Cạnh)", fontsize=11, fontweight='bold', color='#1e293b')
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for i, v in enumerate(r_vals):
        ax.text(v * 1.15, i, f"{v:,} cạnh", va='center', fontsize=8.5, fontweight='bold', color='#1e293b')

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "edge_distribution.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "edge_distribution.png"))
    plt.close(fig)
    print("Exported edge_distribution")

def export_degree_distribution():
    nodes_file = os.path.join(DATA_DIR, "vietnam_cinema_nodes.csv")
    with open(nodes_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        in_degrees = [int(r["in_degree"]) for r in reader]
    with open(nodes_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        out_degrees = [int(r["out_degree"]) for r in reader]

    in_arr = np.array(in_degrees)
    out_arr = np.array(out_degrees)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=300)

    bins = np.linspace(0, 120, 25)
    ax1.hist(in_arr, bins=bins, alpha=0.65, color='#2563eb', label='In-Degree (Bậc vào)', edgecolor='#1d4ed8')
    ax1.hist(out_arr, bins=bins, alpha=0.5, color='#d97706', label='Out-Degree (Bậc ra)', edgecolor='#b45309')
    ax1.set_title("Phân Bố Tần Số Bậc (Degree Histogram)", fontsize=10.5, fontweight='bold', color='#1e293b')
    ax1.set_xlabel("Bậc liên kết k", fontsize=9, fontweight='bold', color='#1e293b')
    ax1.set_ylabel("Số lượng đỉnh N(k)", fontsize=9, fontweight='bold', color='#1e293b')
    ax1.legend(fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.4)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    counts = Counter(in_degrees)
    x_v = sorted(list(counts.keys()))
    y_v = [counts[x] for x in x_v]
    ax2.scatter(x_v[1:], y_v[1:], color='#7c3aed', s=24, alpha=0.75, edgecolors='none', label='Thực nghiệm P(k)')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_title("Đồ Thị Log-Log (Scale-Free Power Law)", fontsize=10.5, fontweight='bold', color='#1e293b')
    ax2.set_xlabel("Bậc k (Log Scale)", fontsize=9, fontweight='bold', color='#1e293b')
    ax2.set_ylabel("Xác suất P(k) (Log Scale)", fontsize=9, fontweight='bold', color='#1e293b')
    ax2.grid(True, linestyle='--', alpha=0.4, which='both')
    ax2.legend(fontsize=8.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "degree_distribution.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "degree_distribution.png"))
    plt.close(fig)
    print("Exported degree_distribution")

def export_node_composition_and_cast():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=300)

    pie_labels = ['Person\n(1.899 - 64.9%)', 'Artwork\n(913 - 31.2%)', 'Organization\n(116 - 4.0%)']
    pie_sizes = [1899, 913, 116]
    ax1.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=140, pctdistance=0.65, labeldistance=1.15,
            colors=['#38bdf8', '#fbbf24', '#f87171'], textprops={'fontsize': 8.5, 'weight': 'bold'})
    ax1.set_title("Cơ Cấu Thành Phần 2.928 Đỉnh", fontsize=10.5, fontweight='bold', color='#1e293b')

    film_names = ["Chủ tịch giao hàng", "Gia đình phép thuật", "Bánh mì ông Màu", "Mùi ngò gai", "Thương ngày nắng về", "Mẹ ghẻ", "Độc đạo"][::-1]
    film_casts = [20, 18, 17, 16, 14, 14, 13][::-1]
    ax2.barh(film_names, film_casts, color='#10b981', edgecolor='#059669', height=0.6)
    ax2.set_xlim(0, 24)
    ax2.set_title("Top 7 Tác Phẩm Có Dàn Cast Lớn Nhất", fontsize=10.5, fontweight='bold', color='#1e293b')
    ax2.set_xlabel("Số lượng diễn viên & đạo diễn tham gia", fontsize=9, fontweight='bold', color='#1e293b')
    ax2.grid(axis='x', linestyle='--', alpha=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    for i, v in enumerate(film_casts):
        ax2.text(v + 0.4, i, f"{v} người", va='center', fontsize=8.5, fontweight='bold', color='#047857')

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "node_composition_and_cast.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "node_composition_and_cast.png"))
    plt.close(fig)
    print("Exported node_composition_and_cast")

def export_hubs_and_authorities():
    fig, ax = plt.subplots(figsize=(9, 3.8), dpi=300)
    h_names = ["Vũ Trường Khoa (Đạo diễn)", "Nguyễn Phương Điền (Đạo diễn)", "Nguyễn Danh Dũng (Đạo diễn)",
               "Kim Xuân (Diễn viên)", "Quang Tuấn (Diễn viên)"][::-1]
    h_scores = [77, 60, 60, 107, 105][::-1]
    h_colors = ['#f59e0b', '#f59e0b', '#f59e0b', '#10b981', '#10b981'][::-1]
    ax.barh(h_names, h_scores, color=h_colors, height=0.55, edgecolor='#475569')
    ax.set_xlim(0, 130)
    ax.set_title("So Sánh Nút Đầu Mối Điều Phối (Hubs Đạo Diễn) và Nút Trụ Cột Uy Tín (Authorities Diễn Viên)",
                 fontsize=10.5, fontweight='bold', color='#1e293b')
    ax.set_xlabel("Số lượng liên kết điều phối / trích dẫn tương ứng", fontsize=9, fontweight='bold', color='#1e293b')
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for i, v in enumerate(h_scores):
        ax.text(v + 1.8, i, f"{v} kết nối", va='center', fontsize=8.5, fontweight='bold', color='#1e293b')

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "hubs_and_authorities.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "hubs_and_authorities.png"))
    plt.close(fig)
    print("Exported hubs_and_authorities")

def export_core_network():
    fig, ax = plt.subplots(figsize=(8, 7.5), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    core_names = [
        "Trấn Thành", "Thu Trang", "Tiến Luật", "Hồng Ánh", "Kim Xuân",
        "Hứa Vĩ Văn", "Quang Tuấn", "Doãn Quốc Đam", "Trung Anh", "Việt Anh",
        "Vũ Trường Khoa", "Nguyễn Danh Dũng", "Victor Vũ", "Lý Hải", "Vũ Ngọc Đãng",
        "Ngô Thanh Vân", "Thành Lộc", "Hữu Châu", "Như Quỳnh", "Lan Phương"
    ]
    n_c = len(core_names)
    angles = np.linspace(0, 2*np.pi, n_c, endpoint=False)
    cx, cy = 0.5, 0.5
    rx, ry = 0.35, 0.32
    pos = {name: (cx + rx*np.cos(ang), cy + ry*np.sin(ang)) for name, ang in zip(core_names, angles)}

    connections = [
        ("Trấn Thành", "Thu Trang"), ("Trấn Thành", "Tiến Luật"), ("Thu Trang", "Tiến Luật"),
        ("Trấn Thành", "Vũ Ngọc Đãng"), ("Trấn Thành", "Hứa Vĩ Văn"), ("Hứa Vĩ Văn", "Hồng Ánh"),
        ("Doãn Quốc Đam", "Trung Anh"), ("Doãn Quốc Đam", "Việt Anh"), ("Trung Anh", "Việt Anh"),
        ("Vũ Trường Khoa", "Doãn Quốc Đam"), ("Vũ Trường Khoa", "Trung Anh"), ("Nguyễn Danh Dũng", "Trung Anh"),
        ("Victor Vũ", "Hứa Vĩ Văn"), ("Victor Vũ", "Quang Tuấn"), ("Quang Tuấn", "Kim Xuân"),
        ("Thành Lộc", "Hữu Châu"), ("Thành Lộc", "Kim Xuân"), ("Hữu Châu", "Hồng Ánh"),
        ("Lý Hải", "Hứa Vĩ Văn"), ("Như Quỳnh", "Lan Phương"), ("Lan Phương", "Doãn Quốc Đam")
    ]
    for s, t in connections:
        x1, y1 = pos[s]
        x2, y2 = pos[t]
        ax.plot([x1, x2], [y1, y2], color='#94a3b8', alpha=0.45, linewidth=1.5, zorder=1)

    for name, ang in zip(core_names, angles):
        x, y = pos[name]
        col = '#ef4444' if name in ["Vũ Trường Khoa", "Nguyễn Danh Dũng", "Victor Vũ", "Vũ Ngọc Đãng", "Lý Hải"] else (
            '#2563eb' if name in ["Doãn Quốc Đam", "Trung Anh", "Việt Anh", "Như Quỳnh"] else (
                '#10b981' if name in ["Thành Lộc", "Hữu Châu", "Lan Phương"] else '#8b5cf6'
            )
        )
        ax.scatter(x, y, s=280, color=col, alpha=0.95, edgecolors='#ffffff', linewidth=1.8, zorder=3)
        lx = cx + (rx + 0.065) * np.cos(ang)
        ly = cy + (ry + 0.050) * np.sin(ang)
        ax.text(lx, ly, name, fontsize=8.0, fontweight='bold', color='#0f172a', ha='center', va='center', zorder=4,
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#cbd5e1', alpha=0.92))

    ax.set_title("Bản Đồ Mạng Lưới Siêu Liên Kết 20 Nghệ Sĩ Hạt Nhân (Core Subgraph)", fontsize=11, fontweight='bold', color='#1e293b', y=0.98)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "core_network.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "core_network.png"))
    plt.close(fig)
    print("Exported core_network")

def main():
    export_pipeline_architecture()
    export_edge_distribution()
    export_degree_distribution()
    export_node_composition_and_cast()
    export_hubs_and_authorities()
    export_core_network()
    print("All figures exported successfully to:", FIG_DIR)

if __name__ == "__main__":
    main()
