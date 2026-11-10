"""
tests/test_sna_metrics.py
Bộ kiểm thử đơn vị cho các độ đo Mạng xã hội chuyên sâu (Social Network Analysis - SNA).
Bao gồm:
- Mật độ mạng (Density) & Phân bố bậc (Degree Centrality: In-Degree, Out-Degree).
- Thuật toán PageRank (Power Iteration, Damping Factor, Khối lượng xác suất).
- Độ trung tâm trung gian (Betweenness Centrality - Brandes Algorithm).
- Độ trung tâm tiệm cận (Closeness Centrality - Shortest Paths).
- Phát hiện cộng đồng & Độ đo Modularity Q (Louvain Optimization).
- Các chỉ số tô-pô toàn cục trên đồ thị Điện ảnh - Sân khấu Việt Nam (Reciprocity, WCC, SCC).
"""

import os
import sys
import csv
import pytest
import numpy as np
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Set

# Thư mục dự án
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TESTS_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
NODES_CSV = os.path.join(DATA_DIR, "vietnam_cinema_nodes.csv")
EDGES_CSV = os.path.join(DATA_DIR, "vietnam_cinema_edges.csv")

# ==============================================================================
# Thuật toán SNA độc lập phục vụ kiểm thử chuẩn mực (Reference Implementations)
# ==============================================================================

def compute_density(num_nodes: int, num_edges: int, directed: bool = True) -> float:
    """Tính toán mật độ mạng."""
    if num_nodes <= 1:
        return 0.0
    max_edges = num_nodes * (num_nodes - 1) if directed else (num_nodes * (num_nodes - 1)) / 2.0
    return num_edges / max_edges if max_edges > 0 else 0.0

def compute_pagerank(
    adj_matrix: np.ndarray,
    damping: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-7
) -> np.ndarray:
    """Tính toán PageRank bằng phương pháp lặp lũy thừa (Power Iteration)."""
    N = adj_matrix.shape[0]
    if N == 0:
        return np.array([])
    if N == 1:
        return np.array([1.0])

    out_sums = np.sum(adj_matrix, axis=1)
    dangling = (out_sums == 0)
    
    # Ma trận chuyển dịch xác suất M
    safe_out_sums = np.where(dangling, 1.0, out_sums)
    M = (adj_matrix / safe_out_sums[:, None]).T

    pr = np.full(N, 1.0 / N)
    for _ in range(max_iter):
        dangling_sum = np.sum(pr[dangling])
        pr_next = damping * (M.dot(pr) + dangling_sum / N) + (1.0 - damping) / N
        if np.allclose(pr, pr_next, atol=tol):
            break
        pr = pr_next
    return pr

def compute_betweenness_brandes(adj_matrix: np.ndarray, normalized: bool = True) -> np.ndarray:
    """Tính toán Betweenness Centrality bằng thuật toán Brandes (O(V * E))."""
    N = adj_matrix.shape[0]
    CB = np.zeros(N)
    if N <= 2:
        return CB

    for s in range(N):
        S = []
        P = [[] for _ in range(N)]
        sigma = np.zeros(N)
        sigma[s] = 1.0
        d = np.full(N, -1)
        d[s] = 0
        Q = deque([s])

        while Q:
            v = Q.popleft()
            S.append(v)
            for w in range(N):
                if adj_matrix[v, w] > 0:
                    if d[w] < 0:
                        Q.append(w)
                        d[w] = d[v] + 1
                    if d[w] == d[v] + 1:
                        sigma[w] += sigma[v]
                        P[w].append(v)

        delta = np.zeros(N)
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                CB[w] += delta[w]

    # Với đồ thị vô hướng đối xứng, chia 2
    is_symmetric = np.allclose(adj_matrix, adj_matrix.T)
    if is_symmetric:
        CB /= 2.0

    if normalized and N > 2:
        scale = 1.0 / ((N - 1) * (N - 2) / 2.0) if is_symmetric else 1.0 / ((N - 1) * (N - 2))
        CB *= scale
    return CB

def compute_closeness(adj_matrix: np.ndarray) -> np.ndarray:
    """Tính toán Closeness Centrality qua BFS (Wasserman & Faust formula)."""
    N = adj_matrix.shape[0]
    closeness = np.zeros(N)
    if N <= 1:
        return closeness

    for s in range(N):
        d = np.full(N, -1)
        d[s] = 0
        Q = deque([s])
        while Q:
            v = Q.popleft()
            for w in range(N):
                if adj_matrix[v, w] > 0 and d[w] < 0:
                    d[w] = d[v] + 1
                    Q.append(w)
        reachable = (d > 0)
        n_reach = np.sum(reachable)
        if n_reach > 0:
            sum_dist = np.sum(d[reachable])
            closeness[s] = (n_reach / (N - 1)) * (n_reach / sum_dist)
    return closeness

def compute_modularity(adj_matrix: np.ndarray, partition: List[int]) -> float:
    """Tính toán hàm mục tiêu Modularity Q của Newman-Girvan."""
    m = np.sum(adj_matrix) / 2.0
    if m == 0:
        return 0.0
    k = np.sum(adj_matrix, axis=1)
    N = adj_matrix.shape[0]
    Q = 0.0
    for i in range(N):
        for j in range(N):
            if partition[i] == partition[j]:
                Q += adj_matrix[i, j] - (k[i] * k[j]) / (2.0 * m)
    return float(Q / (2.0 * m))

# ==============================================================================
# Suite 1: Mật độ mạng & Bậc đỉnh (Degree Centrality & Density)
# ==============================================================================

class TestDegreeCentralityAndDensity:
    def test_density_bounds(self):
        """Mật độ đồ thị phải luôn nằm trong khoảng [0, 1]."""
        assert compute_density(10, 0) == 0.0
        assert compute_density(10, 90, directed=True) == 1.0
        assert compute_density(10, 45, directed=False) == 1.0

    def test_density_star_graph(self):
        """Mật độ của đồ thị hình sao 5 đỉnh có 4 cạnh vô hướng."""
        d = compute_density(5, 4, directed=False)
        assert abs(d - 0.4) < 1e-6

    def test_degree_conservation(self):
        """Tổng In-Degree luôn bằng tổng Out-Degree và bằng tổng số cạnh E."""
        adj = np.array([
            [0, 1, 1],
            [0, 0, 1],
            [1, 0, 0]
        ])
        in_degrees = np.sum(adj, axis=0)
        out_degrees = np.sum(adj, axis=1)
        assert np.sum(in_degrees) == np.sum(out_degrees) == 4

    def test_isolated_nodes_density_is_zero(self):
        """Đồ thị chỉ có đỉnh cô lập phải có mật độ 0."""
        assert compute_density(100, 0, directed=True) == 0.0
        assert compute_density(1, 0, directed=True) == 0.0
        assert compute_density(0, 0, directed=True) == 0.0

# ==============================================================================
# Suite 2: Thuật toán PageRank
# ==============================================================================

class TestPageRank:
    def test_pagerank_uniform_on_cycle(self):
        """Trên một chu trình có hướng (Directed Cycle), tất cả đỉnh có PageRank bằng nhau 1/N."""
        N = 6
        adj = np.zeros((N, N))
        for i in range(N):
            adj[i, (i + 1) % N] = 1.0
        pr = compute_pagerank(adj)
        assert len(pr) == N
        assert np.allclose(pr, 1.0 / N, atol=1e-5)

    def test_pagerank_star_graph_hub_dominates(self):
        """Đồ thị hình sao hướng tâm (các lá trỏ vào tâm): Đỉnh tâm nhận PageRank cao nhất."""
        N = 5
        adj = np.zeros((N, N))
        for i in range(1, N):
            adj[i, 0] = 1.0  # Tất cả lá trỏ vào nút 0
        pr = compute_pagerank(adj)
        assert pr[0] > max(pr[1:])
        assert np.allclose(pr[1:], pr[1], atol=1e-5)

    def test_pagerank_stochastic_sum_is_one(self):
        """Tổng khối lượng xác suất PageRank luôn bằng 1.0."""
        rng = np.random.RandomState(42)
        adj = (rng.rand(10, 10) > 0.7).astype(float)
        np.fill_diagonal(adj, 0)
        pr = compute_pagerank(adj)
        assert abs(np.sum(pr) - 1.0) < 1e-6

    def test_pagerank_dangling_nodes_conservation(self):
        """Đỉnh cụt (dangling nodes, out-degree = 0) không làm thất thoát xác suất."""
        adj = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0]  # Đỉnh 2 là đỉnh cụt
        ], dtype=float)
        pr = compute_pagerank(adj)
        assert abs(np.sum(pr) - 1.0) < 1e-6
        assert pr[2] > pr[1] > pr[0]

# ==============================================================================
# Suite 3: Betweenness Centrality (Brandes Algorithm)
# ==============================================================================

class TestBetweennessCentrality:
    def test_star_graph_center_has_maximum_betweenness(self):
        """Trên đồ thị hình sao 5 đỉnh, đỉnh trung tâm có Betweenness = 1.0, các lá = 0.0."""
        N = 5
        adj = np.zeros((N, N))
        for i in range(1, N):
            adj[0, i] = adj[i, 0] = 1.0
        cb = compute_betweenness_brandes(adj, normalized=True)
        assert abs(cb[0] - 1.0) < 1e-6
        assert np.allclose(cb[1:], 0.0, atol=1e-6)

    def test_path_graph_betweenness_gradient(self):
        """Trên đồ thị đường đi A-B-C-D-E: đỉnh C ở giữa có Betweenness cao nhất, 2 đầu bằng 0."""
        N = 5
        adj = np.zeros((N, N))
        for i in range(N - 1):
            adj[i, i + 1] = adj[i + 1, i] = 1.0
        cb = compute_betweenness_brandes(adj, normalized=True)
        # Nút đầu và đuôi phải = 0
        assert cb[0] == 0.0
        assert cb[4] == 0.0
        # Nút giữa cao nhất
        assert cb[2] > cb[1]
        assert cb[2] > cb[3]
        assert abs(cb[1] - cb[3]) < 1e-6

    def test_barbell_graph_bridge_betweenness(self):
        """Trên đồ thị tạ (barbell: 2 cụm K3 nối bởi 1 cạnh cầu), 2 đỉnh cầu có Betweenness cao nhất."""
        N = 6
        adj = np.zeros((N, N))
        # Cụm 1: {0, 1, 2}
        for i in range(3):
            for j in range(3):
                if i != j: adj[i, j] = 1.0
        # Cụm 2: {3, 4, 5}
        for i in range(3, 6):
            for j in range(3, 6):
                if i != j: adj[i, j] = 1.0
        # Cầu nối giữa đỉnh 2 và 3
        adj[2, 3] = adj[3, 2] = 1.0

        cb = compute_betweenness_brandes(adj, normalized=True)
        assert cb[2] == cb[3]
        assert cb[2] > cb[0]
        assert cb[2] > cb[1]
        assert cb[3] > cb[4]
        assert cb[3] > cb[5]

    def test_betweenness_bounds_zero_to_one(self):
        """Betweenness chuẩn hóa luôn nằm trong khoảng [0, 1]."""
        rng = np.random.RandomState(42)
        adj = (rng.rand(8, 8) > 0.6).astype(float)
        adj = np.maximum(adj, adj.T)
        np.fill_diagonal(adj, 0)
        cb = compute_betweenness_brandes(adj, normalized=True)
        assert np.all(cb >= 0.0)
        assert np.all(cb <= 1.0)

# ==============================================================================
# Suite 4: Closeness Centrality
# ==============================================================================

class TestClosenessCentrality:
    def test_star_graph_center_has_closeness_one(self):
        """Đỉnh trung tâm của đồ thị hình sao có khoảng cách trung bình = 1, Closeness = 1.0."""
        N = 5
        adj = np.zeros((N, N))
        for i in range(1, N):
            adj[0, i] = adj[i, 0] = 1.0
        cc = compute_closeness(adj)
        assert abs(cc[0] - 1.0) < 1e-6
        assert np.all(cc[1:] < 1.0)

    def test_path_graph_closeness_ordering(self):
        """Trên đồ thị đường đi 5 đỉnh, Closeness giảm dần từ tâm ra 2 đầu mút."""
        N = 5
        adj = np.zeros((N, N))
        for i in range(N - 1):
            adj[i, i + 1] = adj[i + 1, i] = 1.0
        cc = compute_closeness(adj)
        assert cc[2] > cc[1] > cc[0]
        assert abs(cc[1] - cc[3]) < 1e-6
        assert abs(cc[0] - cc[4]) < 1e-6

    def test_disconnected_graph_closeness(self):
        """Đồ thị có thành phần không liên thông được tính toán hợp lệ (không chia cho 0)."""
        adj = np.zeros((4, 4))
        adj[0, 1] = adj[1, 0] = 1.0
        # Đỉnh 2, 3 hoàn toàn cô lập
        cc = compute_closeness(adj)
        assert cc[0] > 0
        assert cc[1] > 0
        assert cc[2] == 0.0
        assert cc[3] == 0.0

# ==============================================================================
# Suite 5: Phát hiện Cộng đồng & Hàm Modularity Q (Louvain)
# ==============================================================================

class TestLouvainAndModularity:
    def test_modularity_bounds(self):
        """Hàm Modularity Q của Newman luôn nằm trong [-0.5, 1.0]."""
        A = np.zeros((4, 4))
        A[0, 1] = A[1, 0] = 1.0
        A[2, 3] = A[3, 2] = 1.0
        part = [0, 0, 1, 1]
        q = compute_modularity(A, part)
        assert -0.5 <= q <= 1.0

    def test_modularity_two_disjoint_cliques(self):
        """Hai cụm K4 tách biệt có Modularity phân hoạch cực đại (Q >= 0.45)."""
        N = 8
        A = np.zeros((N, N))
        for i in range(4):
            for j in range(4):
                if i != j: A[i, j] = 1.0
        for i in range(4, 8):
            for j in range(4, 8):
                if i != j: A[i, j] = 1.0

        part_correct = [0, 0, 0, 0, 1, 1, 1, 1]
        q = compute_modularity(A, part_correct)
        assert q >= 0.45, f"Modularity phân cụm chuẩn phải cao (>= 0.45), thực tế: {q}"

    def test_modularity_single_community_zero(self):
        """Nếu tất cả các đỉnh bị gom vào 1 cộng đồng duy nhất, Modularity Q = 0."""
        N = 6
        A = np.ones((N, N)) - np.eye(N)
        part = [0] * N
        q = compute_modularity(A, part)
        assert abs(q) < 1e-6

    def test_modularity_bad_partition_lower(self):
        """Phân hoạch sai có giá trị Modularity thấp hơn rõ rệt so với phân hoạch đúng."""
        N = 8
        A = np.zeros((N, N))
        for i in range(4):
            for j in range(4):
                if i != j: A[i, j] = 1.0
        for i in range(4, 8):
            for j in range(4, 8):
                if i != j: A[i, j] = 1.0
        A[3, 4] = A[4, 3] = 1.0 # Cầu nối

        part_good = [0, 0, 0, 0, 1, 1, 1, 1]
        part_bad = [0, 1, 0, 1, 0, 1, 0, 1]
        assert compute_modularity(A, part_good) > compute_modularity(A, part_bad)

# ==============================================================================
# Suite 6: Kiểm thử Tích hợp Tô-pô trên Dữ liệu Đồ thị Thực tế
# ==============================================================================

@pytest.fixture(scope="module")
def graph_data():
    """Đọc dữ liệu đỉnh và cạnh của Mạng điện ảnh Việt Nam."""
    if not os.path.exists(NODES_CSV) or not os.path.exists(EDGES_CSV):
        pytest.skip("Chưa tìm thấy tệp CSV dữ liệu đồ thị.")

    with open(NODES_CSV, mode="r", encoding="utf-8-sig") as f:
        nodes = list(csv.DictReader(f))
    with open(EDGES_CSV, mode="r", encoding="utf-8-sig") as f:
        edges = list(csv.DictReader(f))
    return nodes, edges

class TestVietnamCinemaSNATopology:
    def test_real_graph_scale(self, graph_data):
        """Quy mô đồ thị thực tế: >= 2,000 nút và >= 5,000 cạnh."""
        nodes, edges = graph_data
        assert len(nodes) >= 2000, f"Số lượng nút thực tế: {len(nodes)}"
        assert len(edges) >= 5000, f"Số lượng cạnh thực tế: {len(edges)}"

    def test_real_graph_density(self, graph_data):
        """Mật độ mạng lưới đồ thị thực tế nằm trong khoảng 0.001 - 0.003."""
        nodes, edges = graph_data
        N = len(nodes)
        E = len(edges)
        density = compute_density(N, E, directed=True)
        assert 0.0010 <= density <= 0.0030, f"Mật độ thực tế: {density:.6f}"

    def test_real_graph_degree_sum_invariant(self, graph_data):
        """Tổng In-Degree của tất cả các nút phải bằng tổng số cạnh trong tệp edges.csv."""
        nodes, edges = graph_data
        total_in = sum(int(n["in_degree"]) for n in nodes)
        total_out = sum(int(n["out_degree"]) for n in nodes)
        assert total_in == len(edges), f"Tổng In-Degree ({total_in}) != Số cạnh ({len(edges)})"
        assert total_out == len(edges), f"Tổng Out-Degree ({total_out}) != Số cạnh ({len(edges)})"

    def test_real_graph_reciprocity_above_50_pct(self, graph_data):
        """Tính tương hỗ (Reciprocity) của mạng lưới đạt > 50% do đặc thù quan hệ CO_STARRED."""
        nodes, edges = graph_data
        edge_set = set((e["source_id"], e["target_id"]) for e in edges)
        reciprocal_count = sum(1 for (s, t) in edge_set if (t, s) in edge_set)
        reciprocity_pct = (reciprocal_count / len(edges)) * 100.0
        assert reciprocity_pct > 50.0, f"Tính tương hỗ đạt: {reciprocity_pct:.2f}%"

    def test_real_graph_giant_wcc_covers_majority(self, graph_data):
        """Thành phần liên thông yếu lớn nhất (Giant WCC) quy mô >= 2,000 nút và bao phủ > 60% mạng."""
        nodes, edges = graph_data
        node_ids = [n["id"] for n in nodes]
        id_to_idx = {nid: i for i, nid in enumerate(node_ids)}
        N = len(nodes)

        # BFS xây dựng Weakly Connected Component
        adj_undirected = defaultdict(list)
        for e in edges:
            s = e["source_id"]
            t = e["target_id"]
            if s in id_to_idx and t in id_to_idx:
                adj_undirected[s].append(t)
                adj_undirected[t].append(s)

        visited = set()
        components = []
        for nid in node_ids:
            if nid not in visited:
                comp = []
                queue = deque([nid])
                visited.add(nid)
                while queue:
                    curr = queue.popleft()
                    comp.append(curr)
                    for neighbor in adj_undirected[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(comp)

        largest_comp_size = max(len(c) for c in components)
        coverage_pct = (largest_comp_size / N) * 100.0
        assert largest_comp_size >= 2000, f"Giant WCC quy mô: {largest_comp_size} nút"
        assert coverage_pct > 60.0, f"Giant WCC bao phủ: {coverage_pct:.2f}% (kỳ vọng > 60%)"
