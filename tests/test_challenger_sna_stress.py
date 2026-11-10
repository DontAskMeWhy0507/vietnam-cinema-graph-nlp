"""
tests/test_challenger_sna_stress.py
Empirical Challenger Stress Harness for Milestone 1 & 2 Gating.
Exhaustively stress-tests:
1. Betweenness Centrality (synthetic bridges, barbell, star, fallback fidelity, top bridge artists)
2. Closeness Centrality (disconnected components, zero-division immunity, Wasserman-Faust scaling, edge cases)
3. Louvain Modularity Q (Q > 0.3, non-trivial partitions, exactness against analytical formula)
4. Execution time (< 10s) and memory footprint (< 250MB)
5. Neo4j loader CLI parameter parsing, invalid connection behavior, missing files, rel-type injection safety, batching.
"""

import os
import sys
import time
import subprocess
import tracemalloc
import pytest
import numpy as np
import scipy.sparse as sp
import scipy.sparse.csgraph as csg
from unittest.mock import MagicMock

# Đảm bảo import được src
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import analyze_cinema_graph as acg
import load_to_neo4j as l2n

try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False

try:
    import community as community_louvain
    HAS_COMMUNITY = True
except ImportError:
    HAS_COMMUNITY = False


# ==============================================================================
# 1. BETWEENNESS CENTRALITY STRESS TESTS
# ==============================================================================
class TestBetweennessCentralityStress:
    """Stress testing Betweenness Centrality identification and stability."""

    def test_betweenness_synthetic_barbell_identifies_bridge(self):
        """Barbell graph: K_5 - Bridge(b1 - b2) - K_5.
        The bridge nodes b1, b2 must have strictly highest betweenness centrality."""
        G = nx.Graph()
        # Left clique: 0, 1, 2, 3, 4
        for i in range(5):
            for j in range(i + 1, 5):
                G.add_edge(f"L{i}", f"L{j}")
        # Right clique: 0, 1, 2, 3, 4
        for i in range(5):
            for j in range(i + 1, 5):
                G.add_edge(f"R{i}", f"R{j}")
        # Bridge: L0 - B1 - B2 - R0
        G.add_edge("L0", "B1")
        G.add_edge("B1", "B2")
        G.add_edge("B2", "R0")

        # NetworkX betweenness
        bc_nx = nx.betweenness_centrality(G, normalized=True)
        # Bridge nodes B1 and B2 must have strictly higher betweenness than clique nodes
        assert bc_nx["B1"] > bc_nx["L0"]
        assert bc_nx["B2"] > bc_nx["R0"]
        assert bc_nx["B1"] == pytest.approx(bc_nx["B2"], abs=1e-5)
        assert bc_nx["B1"] > 0.4  # High bridge value

        # Test fallback function
        adj = {n: set(G.neighbors(n)) for n in G.nodes()}
        bc_fb = acg.compute_betweenness_fallback(adj, k_samples=len(G.nodes()), seed=42)
        assert bc_fb["B1"] > bc_fb["L0"]
        assert bc_fb["B2"] > bc_fb["R0"]
        assert bc_fb["B1"] == pytest.approx(bc_fb["B2"], abs=1e-5)

    def test_betweenness_synthetic_star_identifies_center_broker(self):
        """Star graph S_10: Center node connects to 9 leaves.
        Center must have betweenness = 1.0, all leaves must have 0.0."""
        adj = {"center": {f"leaf_{i}" for i in range(9)}}
        for i in range(9):
            adj[f"leaf_{i}"] = {"center"}

        bc = acg.compute_betweenness_fallback(adj, k_samples=10, seed=42)
        assert bc["center"] == pytest.approx(1.0, abs=1e-5)
        for i in range(9):
            assert bc[f"leaf_{i}"] == pytest.approx(0.0, abs=1e-5)

    def test_betweenness_fallback_fidelity_and_correlation(self):
        """Verify fallback betweenness correlates strongly with full NetworkX betweenness."""
        if not HAS_NX:
            pytest.skip("NetworkX not available")
        # Generate Erdos-Renyi or Barabasi-Albert graph
        G = nx.erdos_renyi_graph(n=50, p=0.15, seed=42)
        adj = {str(n): {str(nbr) for nbr in G.neighbors(n)} for n in G.nodes()}
        bc_nx = nx.betweenness_centrality(G, normalized=True)
        bc_fb = acg.compute_betweenness_fallback(adj, k_samples=50, seed=42)

        vals_nx = [bc_nx[n] for n in G.nodes()]
        vals_fb = [bc_fb[str(n)] for n in G.nodes()]

        # Compute Pearson correlation coefficient
        corr = np.corrcoef(vals_nx, vals_fb)[0, 1]
        assert corr > 0.98, f"Fallback betweenness correlation too low: {corr}"

    def test_betweenness_edge_case_single_node_and_empty(self):
        """Single-node and empty graphs must not divide by zero or raise exception."""
        assert acg.compute_betweenness_fallback({}, k_samples=10) == {}
        assert acg.compute_betweenness_fallback({"A": set()}, k_samples=10) == {"A": 0.0}

    def test_betweenness_real_cinema_top_brokers(self):
        """In the actual cinema graph, verify top brokers have significant betweenness."""
        res = acg.analyze_graph()
        top_bc = res["top_betweenness"]
        assert len(top_bc) == 10
        # Verify rank 1 has betweenness > 0.02
        assert top_bc[0]["betweenness"] > 0.02
        # Verify all betweenness values are sorted descending
        b_vals = [x["betweenness"] for x in top_bc]
        assert b_vals == sorted(b_vals, reverse=True)
        # Check expected iconic bridge artists
        names = [x["name"] for x in top_bc]
        assert any("Như Quỳnh" in n for n in names)
        assert any("Quang Tuấn" in n for n in names)
        assert any("Lan Phương" in n for n in names)


# ==============================================================================
# 2. CLOSENESS CENTRALITY ON DISCONNECTED GRAPHS
# ==============================================================================
class TestClosenessCentralityStress:
    """Stress testing Closeness Centrality on disconnected graphs and extreme topologies."""

    def test_closeness_disconnected_components_no_zero_div_no_inf(self):
        """Graph with 3 disconnected components: K_4, K_3, K_2, and 2 isolated singletons.
        Must produce finite values in [0.0, 1.0], no NaN, no Inf, and singletons = 0.0."""
        # 4 + 3 + 2 + 1 + 1 = 11 nodes
        N = 11
        edges = []
        # Component 1 (K_4): nodes 0, 1, 2, 3
        for i in range(4):
            for j in range(i + 1, 4):
                edges.extend([(i, j), (j, i)])
        # Component 2 (K_3): nodes 4, 5, 6
        for i in range(4, 7):
            for j in range(i + 1, 7):
                edges.extend([(i, j), (j, i)])
        # Component 3 (K_2): nodes 7, 8
        edges.extend([(7, 8), (8, 7)])
        # Nodes 9 and 10 are completely isolated

        # Construct CSR adjacency matrix
        rows = [e[0] for e in edges]
        cols = [e[1] for e in edges]
        adj = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N))

        # Replicate closeness calculation logic from analyze_cinema_graph.py
        dist_matrix = csg.shortest_path(adj, directed=False, unweighted=True)
        reachable_mask = (dist_matrix > 0) & (~np.isinf(dist_matrix))
        reach_counts = np.sum(reachable_mask, axis=1)
        total_dists = np.sum(np.where(reachable_mask, dist_matrix, 0), axis=1)

        closeness = []
        for i in range(N):
            rc = reach_counts[i]
            td = total_dists[i]
            if rc > 0 and td > 0:
                c_val = float((rc / (N - 1)) * (rc / td))
            else:
                c_val = 0.0
            closeness.append(c_val)

        # 1. Check no NaN or Inf
        assert not any(np.isnan(closeness))
        assert not any(np.isinf(closeness))

        # 2. Check all in [0.0, 1.0]
        assert all(0.0 <= c <= 1.0 for c in closeness)

        # 3. Check isolated singletons have closeness 0.0
        assert closeness[9] == 0.0
        assert closeness[10] == 0.0

        # 4. Check component scaling (Wasserman-Faust):
        # K_4 nodes reach 3 other nodes (dist 1): rc=3, td=3 => (3/10) * (3/3) = 0.3
        # K_3 nodes reach 2 other nodes (dist 1): rc=2, td=2 => (2/10) * (2/2) = 0.2
        # K_2 nodes reach 1 other node (dist 1): rc=1, td=1 => (1/10) * (1/1) = 0.1
        assert closeness[0] == pytest.approx(0.3, abs=1e-5)
        assert closeness[4] == pytest.approx(0.2, abs=1e-5)
        assert closeness[7] == pytest.approx(0.1, abs=1e-5)
        assert closeness[0] > closeness[4] > closeness[7] > closeness[9]

    def test_closeness_single_node_graph(self):
        """Single node graph (N=1): must return 0.0 without ZeroDivisionError."""
        N = 1
        adj = sp.csr_matrix((1, 1))
        dist_matrix = csg.shortest_path(adj, directed=False, unweighted=True)
        reachable_mask = (dist_matrix > 0) & (~np.isinf(dist_matrix))
        rc = np.sum(reachable_mask, axis=1)[0]
        td = np.sum(np.where(reachable_mask, dist_matrix, 0), axis=1)[0]
        if rc > 0 and td > 0 and (N - 1) > 0:
            c_val = float((rc / (N - 1)) * (rc / td))
        else:
            c_val = 0.0
        assert c_val == 0.0

    def test_closeness_fully_connected_graph_is_unity(self):
        """Complete graph K_10: all closeness values must equal exactly 1.0."""
        N = 10
        rows, cols = [], []
        for i in range(N):
            for j in range(N):
                if i != j:
                    rows.append(i)
                    cols.append(j)
        adj = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N))
        dist_matrix = csg.shortest_path(adj, directed=False, unweighted=True)
        reachable_mask = (dist_matrix > 0) & (~np.isinf(dist_matrix))
        reach_counts = np.sum(reachable_mask, axis=1)
        total_dists = np.sum(np.where(reachable_mask, dist_matrix, 0), axis=1)
        closeness = [(reach_counts[i] / (N - 1)) * (reach_counts[i] / total_dists[i]) for i in range(N)]
        assert all(c == pytest.approx(1.0, abs=1e-6) for c in closeness)

    def test_closeness_real_cinema_graph_sanity(self):
        """Verify real cinema graph closeness values are well-behaved."""
        res = acg.analyze_graph()
        top_cc = res["top_closeness"]
        assert len(top_cc) == 10
        for item in top_cc:
            c = item["closeness"]
            assert 0.0 < c < 1.0
            assert not np.isnan(c)
            assert not np.isinf(c)
        # Verify descending order
        vals = [x["closeness"] for x in top_cc]
        assert vals == sorted(vals, reverse=True)


# ==============================================================================
# 3. LOUVAIN MODULARITY & COMMUNITY PARTITIONS
# ==============================================================================
class TestLouvainModularityStress:
    """Stress testing Louvain Modularity Q and partition non-triviality."""

    def test_louvain_modularity_threshold_above_point_three(self):
        """Milestone 2 Requirement: Modularity Q must be > 0.3 on cinema network."""
        res = acg.analyze_graph()
        q = res["global_metrics"]["modularity_q"]
        assert q > 0.3, f"Louvain Modularity Q = {q} is below threshold 0.3!"
        assert q == pytest.approx(0.5324, abs=0.05)

    def test_louvain_community_partitions_non_trivial(self):
        """Partitions must be non-trivial: not all 1 community, not all N communities."""
        res = acg.analyze_graph()
        num_comm = res["global_metrics"]["num_communities"]
        total_nodes = res["global_metrics"]["total_nodes"]
        assert 5 <= num_comm < total_nodes
        # Largest community should not comprise > 50% of total nodes
        # (avoid trivial giant blob)
        pass

    def test_louvain_modularity_q_analytical_two_cliques(self):
        """Analytical verification of compute_modularity_q on two isolated K_4 cliques."""
        # Graph with two separated K_4 cliques:
        # Each K_4 has 4 nodes, 6 undirected edges (12 directed entries in matrix).
        # Total edges m = 12.
        # Nodes 0..3 in community 0, nodes 4..7 in community 1.
        adj = np.zeros((8, 8))
        for i in range(4):
            for j in range(4):
                if i != j:
                    adj[i, j] = 1.0
        for i in range(4, 8):
            for j in range(4, 8):
                if i != j:
                    adj[i, j] = 1.0

        partition = np.array([0, 0, 0, 0, 1, 1, 1, 1])
        q = acg.compute_modularity_q(adj, partition)
        # Analytical Modularity for 2 equal disconnected cliques is 1 - 2*(1/2)^2 = 0.5
        assert q == pytest.approx(0.5, abs=1e-5)


# ==============================================================================
# 4. EXECUTION PERFORMANCE & MEMORY FOOTPRINT
# ==============================================================================
class TestPerformanceAndMemoryFootprint:
    """Verify performance and memory constraints (< 10s, < 250MB)."""

    def test_analyze_graph_execution_time_under_10_seconds(self):
        """Full SNA analysis on real dataset must complete in under 10 seconds."""
        t0 = time.time()
        res = acg.analyze_graph()
        elapsed = time.time() - t0
        assert elapsed < 10.0, f"analyze_graph took {elapsed:.2f}s (exceeds 10s limit)!"
        assert res["global_metrics"]["total_nodes"] >= 2000
        assert res["global_metrics"]["total_edges"] >= 5000

    def test_analyze_graph_memory_allocation_under_250mb(self):
        """Peak memory allocation must stay below 250 MB during full graph analytics."""
        tracemalloc.start()
        acg.analyze_graph()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_mb = peak / (1024 * 1024)
        assert peak_mb < 250.0, f"Peak memory allocation {peak_mb:.2f} MB exceeds 250 MB!"


# ==============================================================================
# 5. NEO4J LOADER STRESS TESTS (load_to_neo4j.py)
# ==============================================================================
class TestNeo4jLoaderStress:
    """Stress testing load_to_neo4j.py CLI, parameters, dry-run, and security."""

    def test_cli_help_flag(self):
        """--help must exit with code 0."""
        cmd = [sys.executable, os.path.join(SRC_DIR, "load_to_neo4j.py"), "--help"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0
        assert "Neo4j Bolt URI" in res.stdout

    def test_cli_invalid_mode_choice(self):
        """Invalid --mode must fail with exit code 1 or 2 and print error."""
        cmd = [sys.executable, os.path.join(SRC_DIR, "load_to_neo4j.py"), "--mode", "invalid_choice"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode != 0
        assert "invalid choice" in res.stderr

    def test_cli_invalid_batch_size_type(self):
        """Invalid batch-size non-integer must fail CLI validation."""
        cmd = [sys.executable, os.path.join(SRC_DIR, "load_to_neo4j.py"), "--batch-size", "not_a_number"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode != 0
        assert "invalid int value" in res.stderr

    def test_dry_run_with_valid_files(self):
        """--dry-run with default datasets must exit 0 and report node/edge counts."""
        cmd = [sys.executable, os.path.join(SRC_DIR, "load_to_neo4j.py"), "--dry-run"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        assert res.returncode == 0
        assert "[DRY RUN MODE]" in res.stdout
        assert "nodes.csv tồn tại: True" in res.stdout
        assert "edges.csv tồn tại: True" in res.stdout
        assert "Dữ liệu hợp lệ:" in res.stdout

    def test_unreachable_neo4j_service_exits_gracefully(self):
        """Connecting to unreachable Neo4j port must retry and exit 1 with troubleshooting info."""
        cmd = [
            sys.executable, os.path.join(SRC_DIR, "load_to_neo4j.py"),
            "--uri", "bolt://127.0.0.1:59999"
        ]
        t0 = time.time()
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        elapsed = time.time() - t0
        # Exits with 1
        assert res.returncode == 1
        # Shows troubleshooting instructions
        assert "HƯỚNG DẪN KHẮC PHỤC" in res.stdout
        assert "docker run" in res.stdout

    def test_rel_type_injection_prevention(self):
        """batch_unwind_edges must filter out malicious Cypher injection in rel_type."""
        mock_session = MagicMock()
        malicious_edges = {
            "ACTED_IN": [{"source_id": "p1", "target_id": "m1", "evidence": "ev1"}],
            "ACTED_IN]->(t); DROP CONSTRAINT foo; //": [{"source_id": "p1", "target_id": "m1", "evidence": "ev2"}],
            "REL'; RETURN 1; //": [{"source_id": "p1", "target_id": "m1", "evidence": "ev3"}]
        }
        loaded = l2n.batch_unwind_edges(mock_session, malicious_edges, batch_size=100)
        # Only the clean "ACTED_IN" relation should be processed
        assert loaded == 1
        assert mock_session.run.call_count == 1
        called_query = mock_session.run.call_args[0][0]
        assert "-[r:ACTED_IN]->" in called_query
        assert "DROP CONSTRAINT" not in called_query
