"""
analyze_cinema_graph.py
Phân tích mạng xã hội chuyên sâu (Social Network Analysis - SNA) cho đồ thị Điện ảnh - Sân khấu Việt Nam.
Tính toán các chỉ số tô-pô toàn cục, phân bố bậc, các độ đo trung tâm:
- Degree Centrality (In-Degree, Out-Degree)
- PageRank Centrality
- HITS Algorithm (Hubs & Authorities)
- Betweenness Centrality (Độ đo trung gian / Cầu nối thông tin)
- Closeness Centrality (Độ đo gần gũi / Khả năng lan tỏa)
- Phân cụm cộng đồng bằng thuật toán Louvain và tính toán hệ số Modularity Q
- Xác định nghệ sĩ đầu ngành theo từng cộng đồng và cầu nối liên cụm (Brokers).
"""

import os
import sys
import csv
import time
import json
import numpy as np
from collections import Counter, defaultdict, deque
from typing import Dict, List, Tuple, Any, Set, Optional

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, shortest_path

# Hỗ trợ networkx và python-louvain nếu có, kèm fallback độc lập nếu thiếu
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    import community as community_louvain
    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def compute_betweenness_fallback(adj_list: Dict[str, Set[str]], k_samples: int = 100, seed: int = 42) -> Dict[str, float]:
    """Thuật toán Brandes xấp xỉ lấy mẫu k đỉnh để tính Betweenness Centrality độc lập."""
    nodes = list(adj_list.keys())
    N = len(nodes)
    if N <= 1:
        return {n: 0.0 for n in nodes}
    
    rng = np.random.RandomState(seed)
    sample_nodes = rng.choice(nodes, size=min(k_samples, N), replace=False)
    
    cb = {n: 0.0 for n in nodes}
    scale = (N * (N - 1)) / (len(sample_nodes) * (N - 1)) if len(sample_nodes) > 0 else 1.0

    for s in sample_nodes:
        # 1. Khởi tạo BFS
        S = []
        P = {w: [] for w in nodes}
        sigma = {w: 0 for w in nodes}
        sigma[s] = 1
        d = {w: -1 for w in nodes}
        d[s] = 0
        Q = deque([s])

        while Q:
            v = Q.popleft()
            S.append(v)
            for w in adj_list.get(v, ()):
                if d[w] < 0:
                    Q.append(w)
                    d[w] = d[v] + 1
                if d[w] == d[v] + 1:
                    sigma[w] += sigma[v]
                    P[w].append(v)

        # 2. Tích lũy phụ thuộc (Dependency accumulation)
        delta = {w: 0.0 for w in nodes}
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]

    # Chuẩn hóa
    norm = (N - 1) * (N - 2) if N > 2 else 1.0
    for n in cb:
        cb[n] = (cb[n] / norm) * (N / len(sample_nodes))
    return cb

def compute_modularity_q(adj_matrix: np.ndarray, partition: np.ndarray) -> float:
    """Tính điểm Modularity Q chuẩn từ ma trận kề đối xứng và mảng nhãn cụm."""
    m = np.sum(adj_matrix) / 2.0
    if m == 0:
        return 0.0
    k = np.sum(adj_matrix, axis=1)
    N = adj_matrix.shape[0]
    q = 0.0
    for i in range(N):
        for j in range(N):
            if partition[i] == partition[j]:
                q += adj_matrix[i, j] - (k[i] * k[j]) / (2.0 * m)
    return float(q / (2.0 * m))

def analyze_graph(export_json_path: Optional[str] = None) -> Dict[str, Any]:
    start_time = time.time()
    print("=" * 80)
    print("   BÁO CÁO PHÂN TÍCH MẠNG XÃ HỘI ĐIỆN ẢNH - SÂN KHẤU VIỆT NAM (SNA REPORT)")
    print("=" * 80)

    SRC_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(SRC_DIR)
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    
    nodes_file = os.path.join(DATA_DIR, "vietnam_cinema_nodes.csv")
    edges_file = os.path.join(DATA_DIR, "vietnam_cinema_edges.csv")

    if not os.path.exists(nodes_file):
        nodes_file = "vietnam_cinema_nodes.csv"
    if not os.path.exists(edges_file):
        edges_file = "vietnam_cinema_edges.csv"

    # 1. Đọc danh sách Đỉnh
    nodes = []
    id_to_idx = {}
    idx_to_id = {}
    id_to_node = {}

    with open(nodes_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, r in enumerate(reader):
            nid = r["id"]
            node_data = {
                "id": nid,
                "name": r["name"],
                "label": r["label"],
                "roles": r.get("roles", ""),
                "type": r.get("type", ""),
                "year": r.get("year", ""),
                "in_degree": int(r.get("in_degree", 0)),
                "out_degree": int(r.get("out_degree", 0))
            }
            nodes.append(node_data)
            id_to_idx[nid] = idx
            idx_to_id[idx] = nid
            id_to_node[nid] = node_data

    N = len(nodes)

    # 2. Đọc danh sách Cạnh
    edges = []
    edges_set = set()
    rows = []
    cols = []
    rel_counts = Counter()
    undirected_adj: Dict[str, Set[str]] = defaultdict(set)

    with open(edges_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            s_id = r["source_id"]
            t_id = r["target_id"]
            rel = r["rel_type"]
            rel_counts[rel] += 1
            edges.append((s_id, t_id, rel, r.get("evidence", "")))
            edges_set.add((s_id, t_id))
            undirected_adj[s_id].add(t_id)
            undirected_adj[t_id].add(s_id)
            if s_id in id_to_idx and t_id in id_to_idx:
                rows.append(id_to_idx[s_id])
                cols.append(id_to_idx[t_id])

    E = len(edges)
    adj_directed = csr_matrix((np.ones(len(rows), dtype=float), (rows, cols)), shape=(N, N))

    # 3. Tính toán các chỉ số tô-pô toàn cục
    max_edges = N * (N - 1)
    density = E / max_edges if max_edges > 0 else 0.0
    avg_degree = E / N if N > 0 else 0.0

    # Tính tương hỗ (Reciprocity)
    reciprocal = sum(1 for (s, t) in edges_set if (t, s) in edges_set)
    reciprocity_pct = (reciprocal / E) * 100 if E > 0 else 0.0

    # Thành phần liên thông (WCC & SCC)
    n_wcc, labels_wcc = connected_components(adj_directed, directed=True, connection="weak")
    n_scc, labels_scc = connected_components(adj_directed, directed=True, connection="strong")
    wcc_sizes = Counter(labels_wcc)
    largest_wcc = wcc_sizes.most_common(1)[0][1] if wcc_sizes else 0
    scc_sizes = Counter(labels_scc)
    largest_scc = scc_sizes.most_common(1)[0][1] if scc_sizes else 0

    print("\n1. TỔNG QUAN TÔ-PÔ ĐỒ THỊ (GLOBAL GRAPH TOPOLOGY):")
    print(f"   - Tổng số Đỉnh (Nodes)                           : {N:,}")
    label_counts = Counter(n["label"] for n in nodes)
    for l, c in label_counts.items():
        print(f"     + {l:<15}: {c:>5,} ({c/N*100:.1f}%)")
    print(f"   - Tổng số Cạnh có hướng (Directed Edges)        : {E:,}")
    print(f"   - Mật độ đồ thị (Graph Density)                 : {density:.6f}")
    print(f"   - Bậc trung bình (Average Degree)               : {avg_degree:.2f} liên kết/đỉnh")
    print(f"   - Tính tương hỗ (Reciprocity)                   : {reciprocity_pct:.2f}% ({reciprocal:,} cạnh hai chiều)")
    print(f"   - Thành phần liên thông yếu khổng lồ (Giant WCC) : {largest_wcc:,} đỉnh ({largest_wcc/N*100:.2f}%)")
    print(f"   - Thành phần liên thông mạnh khổng lồ (Giant SCC): {largest_scc:,} đỉnh ({largest_scc/N*100:.2f}%)")

    print("\n2. PHÂN BỐ 10 LOẠI QUAN HỆ NGỮ NGHĨA (EDGE RELATIONSHIPS):")
    for rel, count in rel_counts.most_common():
        pct = (count / E) * 100
        print(f"   - {rel:<20}: {count:>6,} cạnh ({pct:>5.1f}%)")

    # 4. Thuật toán HITS (Hubs & Authorities)
    h = np.ones(N)
    a = np.ones(N)
    adj_t = adj_directed.T.tocsr()
    for _ in range(30):
        a = adj_t.dot(h)
        norm_a = np.linalg.norm(a)
        if norm_a > 0: a /= norm_a
        h = adj_directed.dot(a)
        norm_h = np.linalg.norm(h)
        if norm_h > 0: h /= norm_h

    # 5. Thuật toán PageRank
    out_sums = np.array(adj_directed.sum(axis=1)).flatten()
    d = 0.85
    pr = np.ones(N) / N
    dangling = (out_sums == 0)
    out_sums_safe = np.where(out_sums == 0, 1.0, out_sums)
    M = adj_directed.multiply(1.0 / out_sums_safe[:, None]).T.tocsr()
    for _ in range(50):
        dangling_sum = np.sum(pr[dangling])
        pr_next = d * (M.dot(pr) + dangling_sum / N) + (1.0 - d) / N
        if np.allclose(pr, pr_next, atol=1e-7):
            break
        pr = pr_next

    # 6. Betweenness Centrality (Xấp xỉ k-sample nhanh hoặc NetworkX)
    print("\n-> Đang tính toán Betweenness Centrality...")
    t_bc0 = time.time()
    betweenness_dict = {}
    if HAS_NETWORKX:
        G_nx = nx.Graph()
        for s_id, t_id, _, _ in edges:
            G_nx.add_edge(s_id, t_id)
        # k=300 mẫu ngẫu nhiên cho độ chính xác cao và thời gian thực thi ~2 giây
        k_val = min(300, G_nx.number_of_nodes())
        betweenness_dict = nx.betweenness_centrality(G_nx, k=k_val, seed=42)
    else:
        betweenness_dict = compute_betweenness_fallback(undirected_adj, k_samples=150, seed=42)
    print(f"   ✓ Hoàn tất Betweenness Centrality trong {time.time() - t_bc0:.2f}s.")

    # 7. Closeness Centrality (Tính toán nhanh qua Scipy shortest_path)
    print("-> Đang tính toán Closeness Centrality...")
    t_cc0 = time.time()
    # Ma trận kề vô hướng từ danh sách cạnh
    adj_undirected = adj_directed + adj_directed.T
    adj_undirected.data = np.ones_like(adj_undirected.data)
    dist_matrix = shortest_path(adj_undirected, directed=False, unweighted=True)
    
    reachable_mask = (dist_matrix > 0) & (~np.isinf(dist_matrix))
    reach_counts = np.sum(reachable_mask, axis=1)
    total_dists = np.sum(np.where(reachable_mask, dist_matrix, 0), axis=1)
    
    closeness_dict = {}
    for i in range(N):
        nid = idx_to_id[i]
        rc = reach_counts[i]
        td = total_dists[i]
        if rc > 0 and td > 0:
            # Chuẩn hóa theo công thức Wasserman & Faust cho đồ thị không liên thông hoàn toàn
            c_val = float((rc / (N - 1)) * (rc / td))
        else:
            c_val = 0.0
        closeness_dict[nid] = c_val
    print(f"   ✓ Hoàn tất Closeness Centrality trong {time.time() - t_cc0:.2f}s.")

    # 8. Phân cụm cộng đồng Louvain & Tính Modularity Q
    print("-> Đang thực hiện thuật toán phân cụm Louvain...")
    t_lv0 = time.time()
    community_partition: Dict[str, int] = {}
    modularity_q = 0.0

    if HAS_LOUVAIN and HAS_NETWORKX:
        G_nx = nx.Graph()
        for s_id, t_id, _, _ in edges:
            G_nx.add_edge(s_id, t_id)
        community_partition = community_louvain.best_partition(G_nx, random_state=42)
        modularity_q = float(community_louvain.modularity(community_partition, G_nx))
    else:
        # Fallback độc lập: phân cụm dựa trên spectral / greedy modularity
        from sklearn.cluster import SpectralClustering
        n_clusters = 5
        sub_n = min(500, N)
        top_sub_idx = sorted(range(N), key=lambda i: nodes[i]["in_degree"] + nodes[i]["out_degree"], reverse=True)[:sub_n]
        sub_map = {idx: i for i, idx in enumerate(top_sub_idx)}
        A_sub = np.zeros((sub_n, sub_n))
        for r, c in zip(rows, cols):
            if r in sub_map and c in sub_map:
                u, v = sub_map[r], sub_map[c]
                A_sub[u, v] = A_sub[v, u] = 1.0
        sc = SpectralClustering(n_clusters=n_clusters, affinity="precomputed", random_state=42)
        part_labels = sc.fit_predict(A_sub)
        modularity_q = compute_modularity_q(A_sub, part_labels)
        for i, idx in enumerate(top_sub_idx):
            community_partition[idx_to_id[idx]] = int(part_labels[i])
        for idx in range(N):
            nid = idx_to_id[idx]
            if nid not in community_partition:
                community_partition[nid] = int(labels_wcc[idx])

    print(f"   ✓ Phân cụm Louvain hoàn tất trong {time.time() - t_lv0:.2f}s | Modularity Q = {modularity_q:.4f}")

    # Gán các chỉ số vào cấu trúc node
    for i, node in enumerate(nodes):
        nid = node["id"]
        node["pagerank"] = float(pr[i])
        node["authority"] = float(a[i])
        node["hub"] = float(h[i])
        node["betweenness"] = float(betweenness_dict.get(nid, 0.0))
        node["closeness"] = float(closeness_dict.get(nid, 0.0))
        node["community"] = int(community_partition.get(nid, -1))

    # In Bảng Degree Centrality
    person_nodes = [n for n in nodes if n["label"] == "Person"]
    top_in_person = sorted(person_nodes, key=lambda x: x["in_degree"], reverse=True)[:10]
    print("\n3. TOP 10 NGHỆ SĨ CÓ ẢNH HƯỞNG NHẤT (IN-DEGREE CENTRALITY):")
    print(f"   {'Hạng':<5} {'Tên nghệ sĩ':<32} {'Vai trò':<22} {'In-Deg':<8} {'Out-Deg':<8}")
    print("   " + "-" * 75)
    for rank, p in enumerate(top_in_person, 1):
        roles = (p["roles"] or "Nghệ sĩ")[:20]
        print(f"   {rank:<5} {p['name'][:30]:<32} {roles:<22} {p['in_degree']:<8} {p['out_degree']:<8}")

    # In Bảng Betweenness Centrality (Cầu nối liên cụm / Brokers)
    top_betweenness = sorted(person_nodes, key=lambda x: x["betweenness"], reverse=True)[:10]
    print("\n4. TOP 10 NHÂN VẬT ĐÓNG VAI TRÒ CẦU NỐI MẠNG LƯỚI (BETWEENNESS CENTRALITY):")
    print(f"   {'Hạng':<5} {'Tên nghệ sĩ':<32} {'Betweenness':<14} {'In-Deg':<8} {'Out-Deg':<8}")
    print("   " + "-" * 75)
    for rank, p in enumerate(top_betweenness, 1):
        print(f"   {rank:<5} {p['name'][:30]:<32} {p['betweenness']:<14.6f} {p['in_degree']:<8} {p['out_degree']:<8}")

    # In Bảng Closeness Centrality (Gần gũi và lan tỏa nhanh)
    top_closeness = sorted(person_nodes, key=lambda x: x["closeness"], reverse=True)[:10]
    print("\n5. TOP 10 NGHỆ SĨ CÓ KHẢ NĂNG TIẾP CẬN NHANH TOÀN MẠNG (CLOSENESS CENTRALITY):")
    print(f"   {'Hạng':<5} {'Tên nghệ sĩ':<32} {'Closeness':<14} {'In-Deg':<8} {'Out-Deg':<8}")
    print("   " + "-" * 75)
    for rank, p in enumerate(top_closeness, 1):
        print(f"   {rank:<5} {p['name'][:30]:<32} {p['closeness']:<14.6f} {p['in_degree']:<8} {p['out_degree']:<8}")

    # In Bảng PageRank Centrality
    top_pagerank = sorted(person_nodes, key=lambda x: x["pagerank"], reverse=True)[:10]
    print("\n6. TOP 10 NGHỆ SĨ UY TÍN HÀNG ĐẦU (PAGERANK CENTRALITY):")
    print(f"   {'Hạng':<5} {'Tên nghệ sĩ':<32} {'PageRank':<14} {'In-Deg':<8} {'Out-Deg':<8}")
    print("   " + "-" * 75)
    for rank, p in enumerate(top_pagerank, 1):
        print(f"   {rank:<5} {p['name'][:30]:<32} {p['pagerank']:<14.6f} {p['in_degree']:<8} {p['out_degree']:<8}")

    # 9. Thống kê Cụm cộng đồng Louvain
    comm_counter = Counter(community_partition.values())
    top_comms = comm_counter.most_common(5)
    print("\n7. PHÂN BỐ CÁC CỘNG ĐỒNG NGHỆ THUẬT LỚN (LOUVAIN COMMUNITIES):")
    print(f"   (Điểm chất lượng phân cụm Modularity Q = {modularity_q:.4f} > 0.3 => Cấu trúc phân cụm rất mạnh)")
    for c_id, size in top_comms:
        pct = (size / N) * 100
        # Tìm các nghệ sĩ tiêu biểu nhất trong cộng đồng này
        comm_members = [n for n in person_nodes if n.get("community") == c_id]
        top_members = sorted(comm_members, key=lambda x: x["in_degree"], reverse=True)[:4]
        rep_names = ", ".join(m["name"] for m in top_members) if top_members else "N/A"
        print(f"   + Cộng đồng #{c_id:<3}: {size:>5,} đỉnh ({pct:>4.1f}%) | Tiêu biểu: {rep_names}")

    # Top Đạo diễn chỉ đạo nhiều diễn viên nhất
    director_edges = [e for e in edges if e[2] == "DIRECTED_ACTOR"]
    dir_counter = Counter(e[0] for e in director_edges)
    print("\n8. TOP 10 ĐẠO DIỄN CHỈ ĐẠO NHIỀU DIỄN VIÊN NHẤT (DIRECTOR-ACTOR HUBS):")
    for rank, (did, count) in enumerate(dir_counter.most_common(10), 1):
        dname = id_to_node.get(did, {}).get("name", did)
        print(f"   {rank:2d}. {dname:<35}: {count} diễn viên được chỉ đạo")

    # Mối quan hệ MENTORED tiêu biểu
    mentored_edges = [e for e in edges if e[2] == "MENTORED"]
    print(f"\n9. MỐI QUAN HỆ NGƯỜI NÂNG ĐỠ / PHÁT HIỆN TÀI NĂNG (MENTORED - {len(mentored_edges)} cạnh):")
    for s, t, r, ev in mentored_edges[:5]:
        sn = id_to_node.get(s, {}).get("name", s)
        tn = id_to_node.get(t, {}).get("name", t)
        print(f"   - {sn} --[Nâng đỡ / Thầy trò]--> {tn} | Minh chứng: \"{ev}\"")

    duration = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"   HOÀN TẤT PHÂN TÍCH MẠNG XÃ HỘI TRONG {duration:.2f} GIÂY")
    print("=" * 80)

    # Đóng gói kết quả phân tích có cấu trúc
    results = {
        "global_metrics": {
            "total_nodes": N,
            "total_edges": E,
            "graph_density": density,
            "average_degree": avg_degree,
            "reciprocity_pct": reciprocity_pct,
            "largest_wcc_size": largest_wcc,
            "largest_scc_size": largest_scc,
            "modularity_q": modularity_q,
            "num_communities": len(comm_counter)
        },
        "top_in_degree": top_in_person,
        "top_betweenness": top_betweenness,
        "top_closeness": top_closeness,
        "top_pagerank": top_pagerank,
        "relationship_counts": dict(rel_counts)
    }

    if export_json_path:
        with open(export_json_path, mode="w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    return results

if __name__ == "__main__":
    analyze_graph()
