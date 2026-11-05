import os
import sys
from pathlib import Path
import csv
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from cinema_models import Node, Edge, CinemaGraph

def test_cinema_models_and_graph(tmp_path):
    graph = CinemaGraph()

    # Thêm các Node mẫu
    n1 = Node(id="tran_thanh", name="Trấn Thành", label="Person", metadata={"roles": "Diễn viên, Đạo diễn"})
    n2 = Node(id="vu_ngoc_dang", name="Vũ Ngọc Đãng", label="Person", metadata={"roles": "Đạo diễn"})
    n3 = Node(id="bo_gia", name="Bố già (phim 2021)", label="Artwork", metadata={"type": "Phim điện ảnh", "year": "2021"})
    n4 = Node(id="galaxy_studio", name="Galaxy Studio", label="Organization", metadata={"type": "Hãng phim"})

    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)
    graph.add_node(n4)

    assert len(graph.nodes) == 4

    # Thêm các Edge mẫu
    e1 = Edge(source_id="tran_thanh", target_id="bo_gia", rel_type="DIRECTED", evidence="Đạo diễn phim Bố già")
    e2 = Edge(source_id="vu_ngoc_dang", target_id="bo_gia", rel_type="DIRECTED", evidence="Đạo diễn phim Bố già")
    e3 = Edge(source_id="tran_thanh", target_id="bo_gia", rel_type="ACTED_IN", evidence="Vai Ba Sang")
    e4 = Edge(source_id="vu_ngoc_dang", target_id="tran_thanh", rel_type="DIRECTED_ACTOR", evidence="Chỉ đạo diễn xuất")
    e5 = Edge(source_id="bo_gia", target_id="galaxy_studio", rel_type="PRODUCED_BY", evidence="Galaxy phát hành/sản xuất")

    graph.add_edge(e1)
    graph.add_edge(e2)
    graph.add_edge(e3)
    graph.add_edge(e4)
    graph.add_edge(e5)

    assert len(graph.edges) == 5

    # Test xuất CSV
    nodes_csv = tmp_path / "test_nodes.csv"
    edges_csv = tmp_path / "test_edges.csv"
    graph.export_csv(str(nodes_csv), str(edges_csv))

    with open(nodes_csv, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
        assert rows[0] == ["id", "name", "label", "roles", "type", "year", "in_degree", "out_degree"]
        assert len(rows) == 5  # 1 header + 4 nodes

    with open(edges_csv, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
        assert rows[0] == ["source_id", "source_name", "target_id", "target_name", "rel_type", "evidence"]
        assert len(rows) == 6  # 1 header + 5 edges

    # Test xuất Neo4j Cypher
    cypher_file = tmp_path / "import_neo4j.cypher"
    graph.export_neo4j_cypher(str(cypher_file))
    content = cypher_file.read_text(encoding="utf-8")
    assert "CREATE CONSTRAINT" in content
    assert "MERGE (p:Person {id: 'tran_thanh'})" in content
    assert "MERGE (a:Artwork {id: 'bo_gia'})" in content
    assert "[r:DIRECTED]" in content
