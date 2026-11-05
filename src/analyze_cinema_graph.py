"""
analyze_cinema_graph.py
Phân tích mạng xã hội chuyên sâu (Social Network Analysis - SNA) cho đồ thị Điện ảnh - Sân khấu Việt Nam.
Tính toán các chỉ số tô-pô, bậc kết nối, độ trung tâm (Degree, PageRank, HITS Hubs & Authorities), 
phát hiện cụm cộng đồng nghệ thuật và xuất thống kê cho bài báo cáo học thuật.
"""

import sys
import csv
import numpy as np
from collections import Counter, defaultdict
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def analyze_graph():
    print("=" * 75)
    print("   BÁO CÁO PHÂN TÍCH MẠNG XÃ HỘI ĐIỆN ẢNH - SÂN KHẤU VIỆT NAM (SNA REPORT)")
    print("=" * 75)

    # 1. Đọc nodes.csv
    nodes = []
    id_to_idx = {}
    idx_to_id = {}
    id_to_node = {}

    import os
    SRC_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(SRC_DIR)
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    
    nodes_file = os.path.join(DATA_DIR, "vietnam_cinema_nodes.csv")
    if not os.path.exists(nodes_file):
        nodes_file = "vietnam_cinema_nodes.csv"
        
    edges_file = os.path.join(DATA_DIR, "vietnam_cinema_edges.csv")
    if not os.path.exists(edges_file):
        edges_file = "vietnam_cinema_edges.csv"

    with open(nodes_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, r in enumerate(reader):
            nid = r["id"]
            node_data = {
                "id": nid,
                "name": r["name"],
                "label": r["label"],
                "roles": r["roles"],
                "type": r["type"],
                "year": r["year"],
                "in_degree": int(r["in_degree"]),
                "out_degree": int(r["out_degree"])
            }
            nodes.append(node_data)
            id_to_idx[nid] = idx
            idx_to_id[idx] = nid
            id_to_node[nid] = node_data

    N = len(nodes)

    # 2. Đọc edges.csv
    edges = []
    edges_set = set()
    rows = []
    cols = []
    rel_counts = Counter()

    with open(edges_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            s_id = r["source_id"]
            t_id = r["target_id"]
            rel = r["rel_type"]
            rel_counts[rel] += 1
            edges.append((s_id, t_id, rel, r["evidence"]))
            edges_set.add((s_id, t_id))
            if s_id in id_to_idx and t_id in id_to_idx:
                rows.append(id_to_idx[s_id])
                cols.append(id_to_idx[t_id])

    E = len(edges)
    adj = csr_matrix((np.ones(len(rows), dtype=float), (rows, cols)), shape=(N, N))

    # 3. Tính toán các chỉ số tô-pô toàn cục
    max_edges = N * (N - 1)
    density = E / max_edges if max_edges > 0 else 0
    avg_degree = E / N if N > 0 else 0

    # Reciprocity
    reciprocal = sum(1 for (s, t) in edges_set if (t, s) in edges_set)
    reciprocity_pct = (reciprocal / E) * 100 if E > 0 else 0

    # Connected Components
    n_wcc, labels_wcc = connected_components(adj, directed=True, connection="weak")
    n_scc, labels_scc = connected_components(adj, directed=True, connection="strong")
    wcc_sizes = Counter(labels_wcc)
    largest_wcc = wcc_sizes.most_common(1)[0][1]
    scc_sizes = Counter(labels_scc)
    largest_scc = scc_sizes.most_common(1)[0][1]

    print("\n1. TỔNG QUAN TÔ-PÔ ĐỒ THỊ (GLOBAL GRAPH TOPOLOGY):")
    print(f"   - Tổng số Đỉnh (Nodes): {N:,}")
    label_counts = Counter(n["label"] for n in nodes)
    for l, c in label_counts.items():
        print(f"     + {l:<15}: {c:>5,} ({c/N*100:.1f}%)")
    print(f"   - Tổng số Cạnh (Directed Edges): {E:,}")
    print(f"   - Mật độ đồ thị (Graph Density): {density:.6f}")
    print(f"   - Bậc trung bình (Average Degree): {avg_degree:.2f} liên kết/đỉnh")
    print(f"   - Tính tương hỗ (Reciprocity): {reciprocity_pct:.2f}% ({reciprocal:,} cạnh hai chiều)")
    print(f"   - Thành phần liên thông yếu lớn nhất (Giant WCC): {largest_wcc:,} nodes ({largest_wcc/N*100:.2f}%)")
    print(f"   - Thành phần liên thông mạnh lớn nhất (Giant SCC): {largest_scc:,} nodes ({largest_scc/N*100:.2f}%)")

    print("\n2. THỐNG KÊ 10 LOẠI QUAN HỆ NGỮ NGHĨA (EDGE RELATIONSHIPS):")
    for rel, count in rel_counts.most_common():
        pct = (count / E) * 100
        print(f"   - {rel:<20}: {count:>6,} cạnh ({pct:>5.1f}%)")

    # 4. HITS Algorithm (Hubs & Authorities)
    h = np.ones(N)
    a = np.ones(N)
    adj_t = adj.T.tocsr()
    for _ in range(30):
        a = adj_t.dot(h)
        norm_a = np.linalg.norm(a)
        if norm_a > 0: a /= norm_a
        h = adj.dot(a)
        norm_h = np.linalg.norm(h)
        if norm_h > 0: h /= norm_h

    # PageRank
    out_sums = np.array(adj.sum(axis=1)).flatten()
    d = 0.85
    pr = np.ones(N) / N
    dangling = (out_sums == 0)
    out_sums[out_sums == 0] = 1.0
    M = adj.multiply(1.0 / out_sums[:, None]).T.tocsr()
    for _ in range(50):
        dangling_sum = np.sum(pr[dangling])
        pr_next = d * (M.dot(pr) + dangling_sum / N) + (1.0 - d) / N
        if np.allclose(pr, pr_next, atol=1e-7):
            break
        pr = pr_next

    # 5. Top Nhân vật trung tâm (Person Nodes)
    person_nodes = [n for n in nodes if n["label"] == "Person"]
    top_in_person = sorted(person_nodes, key=lambda x: x["in_degree"], reverse=True)[:15]
    print("\n3. TOP 15 NGHỆ SĨ CÓ ẢNH HƯỞNG NHẤT (IN-DEGREE CENTRALITY):")
    print(f"   {'Hạng':<5} {'Tên nghệ sĩ':<35} {'Vai trò':<25} {'In-Deg':<8} {'Out-Deg':<8}")
    print("   " + "-" * 75)
    for rank, p in enumerate(top_in_person, 1):
        roles = (p["roles"] or "Nghệ sĩ")[:23]
        print(f"   {rank:<5} {p['name'][:33]:<35} {roles:<25} {p['in_degree']:<8} {p['out_degree']:<8}")

    # Top Đạo diễn chỉ đạo nhiều diễn viên nhất
    director_edges = [e for e in edges if e[2] == "DIRECTED_ACTOR"]
    dir_counter = Counter(e[0] for e in director_edges)
    print("\n4. TOP 10 ĐẠO DIỄN CHỈ ĐẠO NHIỀU DIỄN VIÊN NHẤT (DIRECTOR-ACTOR HUBS):")
    for rank, (did, count) in enumerate(dir_counter.most_common(10), 1):
        dname = id_to_node.get(did, {}).get("name", did)
        print(f"   {rank:2d}. {dname:<35}: {count} diễn viên được chỉ đạo")

    # Top Tác phẩm có dàn cast lớn nhất (In-Degree của Artwork)
    artwork_nodes = [n for n in nodes if n["label"] == "Artwork"]
    top_artworks = sorted(artwork_nodes, key=lambda x: x["in_degree"], reverse=True)[:10]
    print("\n5. TOP 10 TÁC PHẨM CÓ QUY MÔ DÀN DIỄN VIÊN / Ê-KÍP LỚN NHẤT:")
    for rank, a_node in enumerate(top_artworks, 1):
        print(f"   {rank:2d}. {a_node['name'][:40]:<42} ({a_node['year'] or 'N/A'}): {a_node['in_degree']} diễn viên/đạo diễn")

    # Top Cặp đôi nghệ sĩ / Đóng cặp ăn ý nhất
    co_star_edges = [e for e in edges if e[2] == "CO_STARRED"]
    co_star_pairs = Counter()
    for s, t, r, ev in co_star_edges:
        if s < t:
            co_star_pairs[(s, t)] = ev
    print("\n6. MỘT SỐ CẶP ĐÔI BẠN DIỄN / ĐÓNG CẶP ĂN Ý TIÊU BIỂU:")
    for (s, t), ev in list(co_star_pairs.most_common(10)):
        sn = id_to_node.get(s, {}).get("name", s)
        tn = id_to_node.get(t, {}).get("name", t)
        print(f"   - {sn} ⇄ {tn} ({ev})")

    # Mối quan hệ MENTORED tiêu biểu
    mentored_edges = [e for e in edges if e[2] == "MENTORED"]
    print(f"\n7. MỐI QUAN HỆ NGƯỜI NÂNG ĐỠ / PHÁT HIỆN TÀI NĂNG (MENTORED - {len(mentored_edges)} cạnh):")
    for s, t, r, ev in mentored_edges[:8]:
        sn = id_to_node.get(s, {}).get("name", s)
        tn = id_to_node.get(t, {}).get("name", t)
        print(f"   - {sn} --[Nâng đỡ / Thầy trò]--> {tn}")
        print(f"     Minh chứng (Evidence): \"{ev}\"")

    print("\n" + "=" * 75)
    print("                         HOÀN TẤT BÁO CÁO")
    print("=" * 75)

if __name__ == "__main__":
    analyze_graph()
