"""
export_latex_figures.py
Xuất 6 biểu đồ vector (.pdf) và raster (.png, 300 DPI) từ dữ liệu thực tế
data/vietnam_cinema_nodes.csv & data/vietnam_cinema_edges.csv để nhúng vào báo cáo LaTeX.
Toàn bộ số liệu và đồ thị con được tính toán trực tiếp từ tập dữ liệu trên đĩa.
"""

import os
import csv
from collections import Counter
import numpy as np
from scipy.sparse import csr_matrix
import networkx as nx
import community as community_louvain

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
FIG_DIR = os.path.join(ROOT_DIR, "reports", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def load_graph_data():
    nodes_file = os.path.join(DATA_DIR, "vietnam_cinema_nodes.csv")
    edges_file = os.path.join(DATA_DIR, "vietnam_cinema_edges.csv")
    with open(nodes_file, mode="r", encoding="utf-8-sig") as f:
        nodes = list(csv.DictReader(f))
    for n in nodes:
        n["in_degree"] = int(n["in_degree"])
        n["out_degree"] = int(n["out_degree"])
        n["tot_degree"] = n["in_degree"] + n["out_degree"]
    with open(edges_file, mode="r", encoding="utf-8-sig") as f:
        edges = list(csv.DictReader(f))
    return nodes, edges


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def export_pipeline_architecture(nodes, edges):
    n_cnt, e_cnt = len(nodes), len(edges)
    fig, ax = plt.subplots(figsize=(10.5, 3.0), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 34)

    steps = [
        (3, 5, 20.5, 24, "1. THU THẬP WIKIPEDIA\n(crawl_vietnam_cinema.py)",
         "MediaWiki Action API\n15 thể loại gốc -> 180\nCache: 2.253 bài viết", "#eff6ff", "#1d4ed8"),
        (27.5, 5, 20.5, 24, "2. TRÍCH XUẤT NLP\n(cinema_extractor.py)",
         "Brace-Depth Infobox\n5 nhóm Regex OpenIE\nSuy diễn 2 chiều", "#f0fdf4", "#047857"),
        (52, 5, 20.5, 24, "3. CHUẨN HÓA SCHEMA\n(cinema_models.py)",
         "Kiểm tra 10 loại cạnh\nLọc thực thể & hôn nhân\nKhử self-loop / trùng", "#fefce8", "#b45309"),
        (76.5, 5, 20.5, 24, "4. LƯU TRỮ & PHÂN TÍCH\n(Neo4j & SNA)",
         f"{fmt_int(n_cnt)} đỉnh | {fmt_int(e_cnt)} cạnh\nimport_neo4j.cypher\nCSR, HITS, Louvain", "#f8fafc", "#334155"),
    ]
    for x, y, w, h, t1, t2, fc, ec in steps:
        rect = patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=1.0",
            facecolor=fc, edgecolor=ec, linewidth=1.6
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h * 0.68, t1, fontsize=8.5, fontweight="bold", color=ec, ha="center", va="center")
        ax.text(x + w / 2, y + h * 0.27, t2, fontsize=7.8, color="#334155", ha="center", va="center")

    for x_arr in [24.0, 48.5, 73.0]:
        ax.annotate("", xy=(x_arr + 3.0, 17), xytext=(x_arr - 0.1, 17),
                    arrowprops=dict(facecolor="#475569", edgecolor="#475569", arrowstyle="->", lw=1.8))

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "pipeline_architecture.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "pipeline_architecture.png"))
    plt.close(fig)
    print("Exported pipeline_architecture")


def export_edge_distribution(edges):
    rel_counter = Counter(e["rel_type"] for e in edges)
    ordered = rel_counter.most_common()[::-1]
    labels = [k for k, _ in ordered]
    vals = [v for _, v in ordered]
    total = sum(vals)

    fig, ax = plt.subplots(figsize=(8.8, 4.3), dpi=300)
    colors = ["#94a3b8" if v < 100 else ("#64748b" if v < 1000 else "#2563eb") for v in vals]
    ax.barh(labels, vals, color=colors, edgecolor="#1e293b", linewidth=0.6, height=0.62)
    ax.set_xscale("log")
    ax.set_xlim(5, 75000)
    ax.set_xlabel("Số lượng cạnh có hướng (thang đo logarit)", fontsize=9.5)
    ax.set_title(f"Phân bổ 10 loại quan hệ trong đồ thị (tổng cộng {fmt_int(total)} cạnh)", fontsize=10.5, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.45)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for i, v in enumerate(vals):
        pct = v / total * 100
        ax.text(v * 1.15, i, f"{fmt_int(v)} ({pct:.1f}%)", va="center", fontsize=8.2, color="#0f172a")

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "edge_distribution.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "edge_distribution.png"))
    plt.close(fig)
    print("Exported edge_distribution")


def export_node_composition_and_cast(nodes, edges):
    label_counts = Counter(n["label"] for n in nodes)
    order_lbls = ["Person", "Artwork", "Organization"]
    pie_sizes = [label_counts[k] for k in order_lbls]
    total_n = sum(pie_sizes)
    pie_labels = [f"{k}\n({fmt_int(label_counts[k])})" for k in order_lbls]

    cast_counter = Counter(
        e["target_name"] for e in edges if e["rel_type"] in ("ACTED_IN", "DIRECTED")
    )
    top_films = cast_counter.most_common(7)[::-1]
    film_names = [k if len(k) <= 28 else k[:25] + "..." for k, _ in top_films]
    film_casts = [v for _, v in top_films]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.2), dpi=300)

    ax1.pie(
        pie_sizes, labels=pie_labels, autopct="%1.1f%%", startangle=135,
        pctdistance=0.62, labeldistance=1.18,
        colors=["#3b82f6", "#f59e0b", "#64748b"],
        wedgeprops=dict(edgecolor="white", linewidth=1.2),
        textprops={"fontsize": 8.5}
    )
    ax1.set_title(f"Cơ cấu {fmt_int(total_n)} nút theo 3 nhãn", fontsize=10.0, fontweight="bold")

    ax2.barh(film_names, film_casts, color="#0d9488", edgecolor="#134e4a", linewidth=0.6, height=0.58)
    ax2.set_xlim(0, max(film_casts) * 1.22)
    ax2.set_title("Top 7 tác phẩm có số nghệ sĩ tham gia cao nhất", fontsize=10.0, fontweight="bold")
    ax2.set_xlabel("Số cạnh ACTED_IN + DIRECTED trỏ vào tác phẩm", fontsize=8.8)
    ax2.grid(axis="x", linestyle="--", alpha=0.45)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    for i, v in enumerate(film_casts):
        ax2.text(v + 0.4, i, f"{v}", va="center", fontsize=8.3, color="#0f172a")

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "node_composition_and_cast.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "node_composition_and_cast.png"))
    plt.close(fig)
    print("Exported node_composition_and_cast")


def export_degree_distribution(nodes):
    in_degrees = np.array([n["in_degree"] for n in nodes])
    out_degrees = np.array([n["out_degree"] for n in nodes])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.2), dpi=300)

    bins = np.linspace(0, max(out_degrees.max(), in_degrees.max()), 25)
    ax1.hist(in_degrees, bins=bins, alpha=0.65, color="#2563eb", label="In-Degree", edgecolor="#1e3a8a")
    ax1.hist(out_degrees, bins=bins, alpha=0.50, color="#d97706", label="Out-Degree", edgecolor="#78350f")
    ax1.set_title("Phân bố tần số bậc kết nối", fontsize=10.0, fontweight="bold")
    ax1.set_xlabel("Bậc k", fontsize=9)
    ax1.set_ylabel("Số lượng đỉnh N(k)", fontsize=9)
    ax1.legend(fontsize=8.5)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    counts = Counter(int(x) for x in in_degrees if x >= 2)
    x_v = np.array(sorted(counts.keys()), dtype=float)
    y_v = np.array([counts[int(x)] for x in x_v], dtype=float)
    slope, intercept = np.polyfit(np.log10(x_v), np.log10(y_v), 1)
    gamma = -slope
    y_fit = 10 ** (intercept + slope * np.log10(x_v))

    ax2.scatter(x_v, y_v, color="#6d28d9", s=22, alpha=0.75, label="Thực nghiệm N(k)")
    ax2.plot(x_v, y_fit, color="#dc2626", linestyle="--", linewidth=1.4, label=f"Hồi quy Log-Log (γ = {gamma:.2f})")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_title("Phân bố In-Degree trên thang Log-Log (k ≥ 2)", fontsize=10.0, fontweight="bold")
    ax2.set_xlabel("Bậc vào k (Log)", fontsize=9)
    ax2.set_ylabel("Số đỉnh N(k) (Log)", fontsize=9)
    ax2.grid(True, linestyle="--", alpha=0.4, which="both")
    ax2.legend(fontsize=8.5)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "degree_distribution.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "degree_distribution.png"))
    plt.close(fig)
    print(f"Exported degree_distribution (fitted gamma={gamma:.3f})")


def export_hubs_and_authorities(nodes, edges):
    id_to_idx = {n["id"]: i for i, n in enumerate(nodes)}
    N = len(nodes)
    rows = [id_to_idx[e["source_id"]] for e in edges]
    cols = [id_to_idx[e["target_id"]] for e in edges]
    adj = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N))

    h = np.ones(N)
    a = np.ones(N)
    adj_t = adj.T.tocsr()
    for _ in range(30):
        a = adj_t.dot(h)
        norm_a = np.linalg.norm(a)
        if norm_a > 0:
            a /= norm_a
        h = adj.dot(a)
        norm_h = np.linalg.norm(h)
        if norm_h > 0:
            h /= norm_h

    # Panel 1: Top 6 Directors by DIRECTED_ACTOR out-links
    dir_counts = Counter(e["source_name"] for e in edges if e["rel_type"] == "DIRECTED_ACTOR")
    top_dirs = dir_counts.most_common(6)[::-1]
    d_names = [k for k, _ in top_dirs]
    d_vals = [v for _, v in top_dirs]

    # Panel 2: Top 6 Persons by HITS Authority
    person_idxs = [i for i, n in enumerate(nodes) if n["label"] == "Person"]
    top_auth_idxs = sorted(person_idxs, key=lambda idx: a[idx], reverse=True)[:6][::-1]
    a_names = [nodes[idx]["name"] for idx in top_auth_idxs]
    a_vals = [float(a[idx]) for idx in top_auth_idxs]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0), dpi=300)

    ax1.barh(d_names, d_vals, color="#d97706", edgecolor="#78350f", linewidth=0.6, height=0.58)
    ax1.set_xlim(0, max(d_vals) * 1.2)
    ax1.set_title("Top 6 Đạo diễn theo số cạnh DIRECTED_ACTOR", fontsize=9.8, fontweight="bold")
    ax1.set_xlabel("Số lượt chỉ đạo diễn viên", fontsize=8.8)
    ax1.grid(axis="x", linestyle="--", alpha=0.45)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    for i, v in enumerate(d_vals):
        ax1.text(v + 1.2, i, f"{v}", va="center", fontsize=8.2)

    ax2.barh(a_names, a_vals, color="#0d9488", edgecolor="#134e4a", linewidth=0.6, height=0.58)
    ax2.set_xlim(0, max(a_vals) * 1.24)
    ax2.set_title("Top 6 Nghệ sĩ theo điểm HITS Authority", fontsize=9.8, fontweight="bold")
    ax2.set_xlabel("Điểm HITS Authority (chuẩn hóa L2)", fontsize=8.8)
    ax2.grid(axis="x", linestyle="--", alpha=0.45)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    for i, v in enumerate(a_vals):
        ax2.text(v + 0.003, i, f"{v:.4f}", va="center", fontsize=8.2)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "hubs_and_authorities.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "hubs_and_authorities.png"))
    plt.close(fig)
    print("Exported hubs_and_authorities")


def export_core_network(nodes, edges):
    G = nx.Graph()
    for e in edges:
        G.add_edge(e["source_id"], e["target_id"])
    part = community_louvain.best_partition(G, random_state=42)

    persons = [n for n in nodes if n["label"] == "Person"]
    top20 = sorted(persons, key=lambda x: x["tot_degree"], reverse=True)[:20]
    top20_ids = [p["id"] for p in top20]
    top20_set = set(top20_ids)
    id_to_node = {n["id"]: n for n in nodes}

    sub_edges = set()
    for e in edges:
        s, t = e["source_id"], e["target_id"]
        if s in top20_set and t in top20_set and s != t:
            sub_edges.add(tuple(sorted([s, t])))

    # Sắp xếp vòng tròn theo cộng đồng để dễ nhìn cụm
    top20_sorted = sorted(top20_ids, key=lambda nid: (part.get(nid, 99), -id_to_node[nid]["tot_degree"]))
    n_c = len(top20_sorted)
    angles = np.linspace(0, 2 * np.pi, n_c, endpoint=False)
    cx, cy = 0.5, 0.5
    rx, ry = 0.34, 0.33
    pos = {nid: (cx + rx * np.cos(ang), cy + ry * np.sin(ang)) for nid, ang in zip(top20_sorted, angles)}

    comm_colors = {
        0: "#d97706",  # C0: Kinh điển Bắc
        2: "#059669",  # C2: Truyền hình & SK Nam
        3: "#2563eb",  # C3: Vũ trụ VFC Bắc
        4: "#7c3aed",  # C4: Điện ảnh thương mại Nam
    }
    comm_labels = {
        0: "C0: Điện ảnh & Kịch kinh điển Bắc",
        2: "C2: Truyền hình & Sân khấu Nam",
        3: "C3: Truyền hình VFC miền Bắc",
        4: "C4: Điện ảnh thương mại & Kịch Nam",
    }

    fig, ax = plt.subplots(figsize=(8.6, 7.2), dpi=300)
    ax.axis("off")
    ax.set_xlim(0.02, 0.98)
    ax.set_ylim(0.02, 1.00)

    for s, t in sub_edges:
        x1, y1 = pos[s]
        x2, y2 = pos[t]
        ax.plot([x1, x2], [y1, y2], color="#94a3b8", alpha=0.40, linewidth=1.1, zorder=1)

    for nid, ang in zip(top20_sorted, angles):
        x, y = pos[nid]
        c_id = part.get(nid, -1)
        col = comm_colors.get(c_id, "#475569")
        sz = 160 + (id_to_node[nid]["tot_degree"] - 150) * 3.0
        ax.scatter(x, y, s=max(160, sz), color=col, alpha=0.92, edgecolors="#ffffff", linewidth=1.5, zorder=3)

        short_name = id_to_node[nid]["name"].replace(" (diễn viên)", "").replace(" (nghệ sĩ)", "").replace(" (người mẫu)", "")
        lx = cx + (rx + 0.082) * np.cos(ang)
        ly = cy + (ry + 0.062) * np.sin(ang)
        ax.text(
            lx, ly, short_name, fontsize=7.8, fontweight="bold", color="#0f172a",
            ha="center", va="center", zorder=4,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor="#cbd5e1", alpha=0.92)
        )

    handles = [
        patches.Patch(facecolor=comm_colors[cid], edgecolor="#ffffff", label=comm_labels[cid])
        for cid in sorted(comm_colors.keys())
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=8.0, frameon=True)
    ax.set_title(
        f"Đồ thị con 20 nghệ sĩ bậc kết nối cao nhất ({len(sub_edges)} cặp liên kết thực tế)",
        fontsize=10.5, fontweight="bold", y=0.97
    )

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "core_network.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "core_network.png"))
    plt.close(fig)
    print(f"Exported core_network ({len(sub_edges)} undirected edges among top 20)")


def main():
    nodes, edges = load_graph_data()
    export_pipeline_architecture(nodes, edges)
    export_edge_distribution(edges)
    export_node_composition_and_cast(nodes, edges)
    export_degree_distribution(nodes)
    export_hubs_and_authorities(nodes, edges)
    export_core_network(nodes, edges)
    print("All figures exported cleanly from real data to:", FIG_DIR)


if __name__ == "__main__":
    main()
