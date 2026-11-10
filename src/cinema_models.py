"""
cinema_models.py
Định nghĩa mô hình đỉnh (Node), cạnh (Edge) và đồ thị CinemaGraph cho mạng xã hội Điện ảnh - Sân khấu Việt Nam.
Hỗ trợ tính toán bậc kết nối, xuất file CSV cho Gephi/NetworkX và tạo kịch bản Cypher nạp vào CSDL Neo4j.
"""

import csv
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional

def sanitize_cypher_prop(val: Any) -> str:
    """Chuẩn hóa và làm sạch chuỗi cho câu lệnh Cypher:
    - Loại bỏ thẻ <ref> và nội dung tham chiếu
    - Loại bỏ thẻ HTML (<br>, <span>,...)
    - Loại bỏ bản mẫu wikitext chưa phân tích ({{...}})
    - Chuyển cú pháp liên kết [[Đích|Hiển thị]] -> Hiển thị
    - Xóa bỏ ký tự xuống dòng (\r, \n) để tránh làm vỡ câu lệnh Cypher
    - Gộp khoảng trắng thừa
    - Thoát ký tự nháy đơn (') và gạch chéo ngược (\) an toàn
    """
    if val is None:
        return ""
    text = str(val)
    # Loại bỏ cặp thẻ <ref>...</ref> và thẻ tự đóng <ref.../>
    text = re.sub(r"<ref[^>]*>.*?</ref>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<ref[^>]*/>", " ", text, flags=re.IGNORECASE)
    # Loại bỏ thẻ HTML khác
    text = re.sub(r"<[^>]+>", " ", text)
    # Loại bỏ các bản mẫu lồng nhau {{...}}
    while "{{" in text and "}}" in text:
        text = re.sub(r"\{\{[^{}]*\}\}", " ", text)
    text = text.replace("{{", "").replace("}}", "")
    # Rút gọn wikilink [[A|B]] -> B, [[A]] -> A
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    text = text.replace("[[", "").replace("]]", "")
    # Xóa hoàn toàn \r và \n thành khoảng trắng đơn
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    # Thoát dấu gạch chéo ngược và nháy đơn cho Cypher single-quoted string
    text = text.replace("\\", "\\\\").replace("'", "\\'")
    return text

@dataclass
class Node:
    id: str
    name: str
    label: str  # 'Person', 'Artwork', 'Organization'
    metadata: Dict[str, Any] = field(default_factory=dict)
    in_degree: int = 0
    out_degree: int = 0

@dataclass
class Edge:
    source_id: str
    target_id: str
    rel_type: str
    evidence: str = ""

class CinemaGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self._edge_keys: Set[tuple] = set()

    def add_node(self, node: Node) -> None:
        if node.id not in self.nodes:
            self.nodes[node.id] = node
        else:
            # Hợp nhất metadata nếu có thông tin mới
            for k, v in node.metadata.items():
                if v and not self.nodes[node.id].metadata.get(k):
                    self.nodes[node.id].metadata[k] = v

    def add_edge(self, edge: Edge) -> bool:
        # Không tạo self-loop và không tạo cạnh trùng
        if edge.source_id == edge.target_id:
            return False
        
        # Chỉ tạo cạnh nếu cả 2 node đều tồn tại trong đồ thị
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            return False

        key = (edge.source_id, edge.target_id, edge.rel_type)
        if key in self._edge_keys:
            return False

        self._edge_keys.add(key)
        self.edges.append(edge)
        return True

    def calculate_degrees(self) -> None:
        """Tính toán in_degree và out_degree cho tất cả các node."""
        for node in self.nodes.values():
            node.in_degree = 0
            node.out_degree = 0

        for edge in self.edges:
            if edge.source_id in self.nodes:
                self.nodes[edge.source_id].out_degree += 1
            if edge.target_id in self.nodes:
                self.nodes[edge.target_id].in_degree += 1

    def export_csv(self, nodes_path: str, edges_path: str) -> None:
        """Xuất danh sách nodes và edges ra file CSV với encoding utf-8-sig."""
        self.calculate_degrees()

        # Xuất nodes.csv
        with open(nodes_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["id", "name", "label", "roles", "type", "year", "in_degree", "out_degree"])
            for node in self.nodes.values():
                roles = node.metadata.get("roles", "")
                art_type = node.metadata.get("type", "")
                year = node.metadata.get("year", "")
                writer.writerow([
                    node.id,
                    node.name,
                    node.label,
                    roles,
                    art_type,
                    year,
                    node.in_degree,
                    node.out_degree
                ])

        # Xuất edges.csv
        with open(edges_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["source_id", "source_name", "target_id", "target_name", "rel_type", "evidence"])
            for edge in self.edges:
                s_name = self.nodes[edge.source_id].name if edge.source_id in self.nodes else edge.source_id
                t_name = self.nodes[edge.target_id].name if edge.target_id in self.nodes else edge.target_id
                writer.writerow([
                    edge.source_id,
                    s_name,
                    edge.target_id,
                    t_name,
                    edge.rel_type,
                    edge.evidence
                ])

    def export_neo4j_cypher(self, cypher_path: str) -> None:
        """Tạo file script Cypher để nạp trực tiếp toàn bộ dữ liệu vào hệ quản trị CSDL Neo4j."""
        self.calculate_degrees()
        
        lines = [
            "// ====================================================================",
            "// KỊCH BẢN NẠP DỮ LIỆU ĐỒ THỊ ĐIỆN ẢNH - SÂN KHẤU VIỆT NAM VÀO NEO4J",
            "// BÀI TẬP LỚN PHÂN TÍCH MẠNG XÃ HỘI (SNA)",
            "// ====================================================================",
            "",
            "// 1. Tạo các ràng buộc tính duy nhất (Unique Constraints) trên thuộc tính id",
            "CREATE CONSTRAINT unique_person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;",
            "CREATE CONSTRAINT unique_artwork_id IF NOT EXISTS FOR (a:Artwork) REQUIRE a.id IS UNIQUE;",
            "CREATE CONSTRAINT unique_organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE;",
            "",
            "// 2. Tạo các đỉnh (Nodes)"
        ]

        # Tạo Nodes
        for node in self.nodes.values():
            safe_name = sanitize_cypher_prop(node.name)
            safe_id = sanitize_cypher_prop(node.id)
            if node.label == "Person":
                roles = sanitize_cypher_prop(node.metadata.get("roles", ""))
                lines.append(f"MERGE (p:Person {{id: '{safe_id}'}}) ON CREATE SET p.name = '{safe_name}', p.roles = '{roles}';")
            elif node.label == "Artwork":
                art_type = sanitize_cypher_prop(node.metadata.get("type", ""))
                year = sanitize_cypher_prop(str(node.metadata.get("year", "")))
                lines.append(f"MERGE (a:Artwork {{id: '{safe_id}'}}) ON CREATE SET a.title = '{safe_name}', a.type = '{art_type}', a.year = '{year}';")
            elif node.label == "Organization":
                org_type = sanitize_cypher_prop(node.metadata.get("type", ""))
                lines.append(f"MERGE (o:Organization {{id: '{safe_id}'}}) ON CREATE SET o.name = '{safe_name}', o.type = '{org_type}';")

        lines.append("")
        lines.append("// 3. Tạo các cạnh quan hệ (Relationships)")
        
        for edge in self.edges:
            s_id = sanitize_cypher_prop(edge.source_id)
            t_id = sanitize_cypher_prop(edge.target_id)
            evidence = sanitize_cypher_prop(edge.evidence)
            rel = edge.rel_type
            
            # Khởi tạo câu truy vấn MATCH và MERGE (đảm bảo strictly 1 dòng duy nhất)
            lines.append(
                f"MATCH (s {{id: '{s_id}'}}), (t {{id: '{t_id}'}}) "
                f"MERGE (s)-[r:{rel}]->(t) "
                f"ON CREATE SET r.evidence = '{evidence}';"
            )

        lines.append("")
        lines.append("// 4. Các câu lệnh Cypher mẫu để phân tích đồ thị trên Neo4j")
        lines.append("// 4.1. Đếm số lượng đỉnh theo từng loại nhãn:")
        lines.append("// MATCH (n) RETURN labels(n) AS Label, count(n) AS Total ORDER BY Total DESC;")
        lines.append("")
        lines.append("// 4.2. Đếm số lượng cạnh theo 10 loại quan hệ:")
        lines.append("// MATCH ()-[r]->() RETURN type(r) AS Relation, count(r) AS Total ORDER BY Total DESC;")
        lines.append("")
        lines.append("// 4.3. Top 10 diễn viên/đạo diễn có nhiều kết nối nhất:")
        lines.append("// MATCH (p:Person)-[r]-() RETURN p.name AS Ten, count(r) AS Degree ORDER BY Degree DESC LIMIT 10;")
        lines.append("")

        with open(cypher_path, mode="w", encoding="utf-8") as f:
            f.write("\n".join(lines))
