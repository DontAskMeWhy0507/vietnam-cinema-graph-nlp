"""
load_to_neo4j.py
Kịch bản nạp dữ liệu đồ thị tri thức Điện ảnh - Sân khấu Việt Nam vào hệ quản trị cơ sở dữ liệu Neo4j.
Sử dụng thư viện chính thức neo4j Python driver với kỹ thuật batching UNWIND và quản lý giao dịch an toàn.

===================================================================================
HƯỚNG DẪN TRIỂN KHAI VÀ TÁI HIỆN BẰNG DOCKER & CYPHER-SHELL
===================================================================================
1. Khởi chạy cụm Neo4j 5 Community Edition bằng Docker:
   - Linux / macOS:
     docker run -d --name neo4j-cinema \
       -p 7474:7474 -p 7687:7687 \
       -e NEO4J_AUTH=neo4j/password \
       -v $(pwd)/data:/var/lib/neo4j/import \
       neo4j:5-community

   - Windows PowerShell:
     docker run -d --name neo4j-cinema `
       -p 7474:7474 -p 7687:7687 `
       -e NEO4J_AUTH=neo4j/password `
       -v ${PWD}/data:/var/lib/neo4j/import `
       neo4j:5-community

2. Nạp dữ liệu qua cypher-shell trực tiếp:
   - Từ máy host:
     cypher-shell -a bolt://localhost:7687 -u neo4j -p password -f data/import_neo4j.cypher
   - Qua docker exec:
     docker exec -i neo4j-cinema cypher-shell -u neo4j -p password < data/import_neo4j.cypher

3. Nạp dữ liệu tự động bằng Python script này:
   python src/load_to_neo4j.py --uri bolt://localhost:7687 --user neo4j --password password
===================================================================================
"""

import os
import sys
import csv
import time
import argparse
from typing import List, Dict, Any, Optional

try:
    from neo4j import GraphDatabase, exceptions as neo4j_exceptions
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False

# Đường dẫn mặc định
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")

DEFAULT_NODES_CSV = os.path.join(DATA_DIR, "vietnam_cinema_nodes.csv")
DEFAULT_EDGES_CSV = os.path.join(DATA_DIR, "vietnam_cinema_edges.csv")
DEFAULT_CYPHER_FILE = os.path.join(DATA_DIR, "import_neo4j.cypher")

CONSTRAINTS = [
    "CREATE CONSTRAINT unique_person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;",
    "CREATE CONSTRAINT unique_artwork_id IF NOT EXISTS FOR (a:Artwork) REQUIRE a.id IS UNIQUE;",
    "CREATE CONSTRAINT unique_organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE;"
]

def check_connectivity(driver, database: str = "neo4j", max_retries: int = 3, retry_delay: float = 2.0) -> bool:
    """Kiểm tra kết nối tới Neo4j với cơ chế thử lại."""
    for attempt in range(1, max_retries + 1):
        try:
            driver.verify_connectivity()
            return True
        except Exception as e:
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
            else:
                print(f"[ERROR] Không thể kết nối tới Neo4j sau {max_retries} lần thử: {e}")
                return False
    return False

def apply_constraints(session) -> None:
    """Tạo các ràng buộc duy nhất (Unique Constraints) cho các nhãn đỉnh."""
    print("-> Đang thiết lập ràng buộc duy nhất (Unique Constraints)...")
    for q in CONSTRAINTS:
        session.run(q)
    print("   ✓ Đã tạo thành công các ràng buộc trên Person, Artwork, Organization.")

def batch_unwind_nodes(session, nodes_by_label: Dict[str, List[Dict[str, Any]]], batch_size: int = 1000) -> int:
    """Nạp danh sách đỉnh theo lô dùng UNWIND tối ưu tốc độ."""
    total_loaded = 0
    
    # 1. Nạp Person nodes
    persons = nodes_by_label.get("Person", [])
    if persons:
        query = """
        UNWIND $batch AS row
        MERGE (p:Person {id: row.id})
        ON CREATE SET 
            p.name = row.name,
            p.roles = row.roles,
            p.in_degree = toInteger(row.in_degree),
            p.out_degree = toInteger(row.out_degree)
        """
        for i in range(0, len(persons), batch_size):
            batch = persons[i:i + batch_size]
            session.run(query, batch=batch)
            total_loaded += len(batch)
            print(f"   + [Person] Đã nạp {total_loaded}/{len(persons)} đỉnh...")

    # 2. Nạp Artwork nodes
    artworks = nodes_by_label.get("Artwork", [])
    if artworks:
        query = """
        UNWIND $batch AS row
        MERGE (a:Artwork {id: row.id})
        ON CREATE SET 
            a.title = row.name,
            a.type = row.type,
            a.year = row.year,
            a.in_degree = toInteger(row.in_degree),
            a.out_degree = toInteger(row.out_degree)
        """
        art_count = 0
        for i in range(0, len(artworks), batch_size):
            batch = artworks[i:i + batch_size]
            session.run(query, batch=batch)
            art_count += len(batch)
            total_loaded += len(batch)
            print(f"   + [Artwork] Đã nạp {art_count}/{len(artworks)} đỉnh...")

    # 3. Nạp Organization nodes
    orgs = nodes_by_label.get("Organization", [])
    if orgs:
        query = """
        UNWIND $batch AS row
        MERGE (o:Organization {id: row.id})
        ON CREATE SET 
            o.name = row.name,
            o.type = row.type,
            o.in_degree = toInteger(row.in_degree),
            o.out_degree = toInteger(row.out_degree)
        """
        org_count = 0
        for i in range(0, len(orgs), batch_size):
            batch = orgs[i:i + batch_size]
            session.run(query, batch=batch)
            org_count += len(batch)
            total_loaded += len(batch)
            print(f"   + [Organization] Đã nạp {org_count}/{len(orgs)} đỉnh...")

    return total_loaded

def batch_unwind_edges(session, edges_by_type: Dict[str, List[Dict[str, Any]]], batch_size: int = 1000) -> int:
    """Nạp danh sách cạnh theo lô dùng UNWIND phân loại theo loại quan hệ."""
    total_loaded = 0
    for rel_type, edge_list in edges_by_type.items():
        # Kiểm tra tính an toàn của rel_type (chỉ chứa chữ cái và gạch dưới)
        if not rel_type.replace("_", "").isalnum():
            print(f"[WARN] Bỏ qua loại quan hệ không an toàn: {rel_type}")
            continue

        query = f"""
        UNWIND $batch AS row
        MATCH (s {{id: row.source_id}}), (t {{id: row.target_id}})
        MERGE (s)-[r:{rel_type}]->(t)
        ON CREATE SET r.evidence = row.evidence
        """
        type_loaded = 0
        for i in range(0, len(edge_list), batch_size):
            batch = edge_list[i:i + batch_size]
            session.run(query, batch=batch)
            type_loaded += len(batch)
            total_loaded += len(batch)
        print(f"   + [{rel_type:<18}] Đã nạp {type_loaded:>5,} cạnh")
        
    return total_loaded

def load_from_csv(driver, nodes_path: str, edges_path: str, database: str = "neo4j", batch_size: int = 1000) -> None:
    """Nạp toàn bộ dữ liệu từ nodes.csv và edges.csv vào Neo4j."""
    print(f"-> Đọc tệp đỉnh: {nodes_path}")
    nodes_by_label: Dict[str, List[Dict[str, Any]]] = {"Person": [], "Artwork": [], "Organization": []}
    with open(nodes_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lbl = row.get("label", "Person")
            if lbl not in nodes_by_label:
                nodes_by_label[lbl] = []
            nodes_by_label[lbl].append(row)
            
    total_nodes = sum(len(v) for v in nodes_by_label.values())
    print(f"   Tổng số đỉnh tìm thấy: {total_nodes:,} đỉnh")

    print(f"-> Đọc tệp cạnh: {edges_path}")
    edges_by_type: Dict[str, List[Dict[str, Any]]] = {}
    with open(edges_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel = row.get("rel_type", "RELATED_TO")
            if rel not in edges_by_type:
                edges_by_type[rel] = []
            edges_by_type[rel].append(row)
            
    total_edges = sum(len(v) for v in edges_by_type.values())
    print(f"   Tổng số cạnh tìm thấy: {total_edges:,} cạnh ({len(edges_by_type)} loại quan hệ)")

    with driver.session(database=database) as session:
        apply_constraints(session)
        print(f"-> Bắt đầu nạp {total_nodes:,} đỉnh bằng UNWIND...")
        n_loaded = batch_unwind_nodes(session, nodes_by_label, batch_size=batch_size)
        print(f"   ✓ Đã hoàn tất nạp {n_loaded:,} đỉnh.")

        print(f"-> Bắt đầu nạp {total_edges:,} cạnh theo 10 loại quan hệ...")
        e_loaded = batch_unwind_edges(session, edges_by_type, batch_size=batch_size)
        print(f"   ✓ Đã hoàn tất nạp {e_loaded:,} cạnh.")

def load_from_cypher_script(driver, cypher_path: str, database: str = "neo4j", batch_size: int = 500) -> None:
    """Nạp dữ liệu bằng cách thực thi trực tiếp script Cypher theo batch giao dịch."""
    print(f"-> Đọc kịch bản Cypher: {cypher_path}")
    statements = []
    with open(cypher_path, mode="r", encoding="utf-8") as f:
        current_stmt = []
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            current_stmt.append(stripped)
            if stripped.endswith(";"):
                stmt_str = " ".join(current_stmt).rstrip(";")
                statements.append(stmt_str)
                current_stmt = []

    print(f"   Tổng số câu lệnh Cypher hợp lệ: {len(statements):,}")
    with driver.session(database=database) as session:
        for i in range(0, len(statements), batch_size):
            batch = statements[i:i + batch_size]
            with session.begin_transaction() as tx:
                for stmt in batch:
                    tx.run(stmt)
                tx.commit()
            print(f"   + Đã thực thi {min(i + batch_size, len(statements))}/{len(statements)} câu lệnh...")

def print_graph_stats(driver, database: str = "neo4j") -> None:
    """In thống kê sau khi nạp vào Neo4j."""
    print("\n" + "=" * 70)
    print("   THỐNG KÊ DỮ LIỆU ĐỒ THỊ TRÊN NEO4J (VERIFICATION SUMMARY)")
    print("=" * 70)
    with driver.session(database=database) as session:
        # Đếm đỉnh theo Label
        res = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS total ORDER BY total DESC")
        print("1. ĐỈNH (NODES):")
        total_n = 0
        for r in res:
            lbl = r["label"] or "Unlabeled"
            cnt = r["total"]
            total_n += cnt
            print(f"   - {lbl:<20}: {cnt:>6,} đỉnh")
        print(f"   => TỔNG CỘNG        : {total_n:>6,} đỉnh")

        # Đếm cạnh theo loại quan hệ
        res = session.run("MATCH ()-[r]->() RETURN type(r) AS rel, count(r) AS total ORDER BY total DESC")
        print("\n2. CẠNH (RELATIONSHIPS):")
        total_e = 0
        for r in res:
            rel = r["rel"]
            cnt = r["total"]
            total_e += cnt
            print(f"   - {rel:<20}: {cnt:>6,} cạnh")
        print(f"   => TỔNG CỘNG        : {total_e:>6,} cạnh")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(
        description="Nạp dữ liệu đồ thị Điện ảnh - Sân khấu Việt Nam vào Neo4j (Milestone 2)."
    )
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j Bolt URI (default: bolt://localhost:7687)")
    parser.add_argument("--user", default="neo4j", help="Neo4j username (default: neo4j)")
    parser.add_argument("--password", default="password", help="Neo4j password (default: password)")
    parser.add_argument("--database", default="neo4j", help="Neo4j database name (default: neo4j)")
    parser.add_argument("--batch-size", type=int, default=1000, help="Số bản ghi mỗi batch (default: 1000)")
    parser.add_argument("--nodes-csv", default=DEFAULT_NODES_CSV, help="Đường dẫn tệp nodes.csv")
    parser.add_argument("--edges-csv", default=DEFAULT_EDGES_CSV, help="Đường dẫn tệp edges.csv")
    parser.add_argument("--cypher-file", default=DEFAULT_CYPHER_FILE, help="Đường dẫn tệp import_neo4j.cypher")
    parser.add_argument("--mode", choices=["csv", "cypher"], default="csv", help="Phương thức nạp: 'csv' dùng UNWIND hoặc 'cypher' chạy script")
    parser.add_argument("--dry-run", action="store_true", help="Kiểm tra tính hợp lệ của tệp dữ liệu mà không cần kết nối Neo4j")

    args = parser.parse_args()

    print("=" * 75)
    print("   BỘ NẠP DỮ LIỆU ĐỒ THỊ NEO4J - VIETNAM CINEMA SOCIAL NETWORK")
    print("=" * 75)
    print(f"• URI Kết nối   : {args.uri}")
    print(f"• Người dùng    : {args.user}")
    print(f"• Cơ sở dữ liệu : {args.database}")
    print(f"• Phương thức   : {args.mode.upper()}")
    print(f"• Batch size    : {args.batch_size}")
    print("-" * 75)

    if args.dry_run:
        print("[DRY RUN MODE] Kiểm tra tệp dữ liệu:")
        print(f"- nodes.csv tồn tại: {os.path.exists(args.nodes_csv)} ({args.nodes_csv})")
        print(f"- edges.csv tồn tại: {os.path.exists(args.edges_csv)} ({args.edges_csv})")
        print(f"- cypher file tồn tại: {os.path.exists(args.cypher_file)} ({args.cypher_file})")
        if os.path.exists(args.nodes_csv) and os.path.exists(args.edges_csv):
            with open(args.nodes_csv, encoding="utf-8-sig") as f:
                n_count = sum(1 for _ in f) - 1
            with open(args.edges_csv, encoding="utf-8-sig") as f:
                e_count = sum(1 for _ in f) - 1
            print(f"✓ Dữ liệu hợp lệ: {n_count:,} đỉnh và {e_count:,} cạnh sẵn sàng nạp vào Neo4j.")
        return 0

    if not HAS_NEO4J:
        print("[ERROR] Thư viện 'neo4j' chưa được cài đặt. Vui lòng chạy: pip install neo4j>=5.18.0")
        sys.exit(1)

    try:
        driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo driver Neo4j: {e}")
        sys.exit(1)

    print("-> Đang kiểm tra kết nối tới dịch vụ Neo4j...")
    if not check_connectivity(driver, database=args.database):
        print("\n[HƯỚNG DẪN KHẮC PHỤC]")
        print("Dịch vụ Neo4j chưa hoạt động tại URI:", args.uri)
        print("Để khởi chạy máy chủ Neo4j cục bộ qua Docker, vui lòng thực thi lệnh sau:")
        print("\n  docker run -d --name neo4j-cinema -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password -v $(pwd)/data:/var/lib/neo4j/import neo4j:5-community\n")
        print("Sau đó chạy lại script này với tham số mặc định.")
        driver.close()
        sys.exit(1)

    start_time = time.time()
    try:
        if args.mode == "csv":
            load_from_csv(driver, args.nodes_csv, args.edges_csv, database=args.database, batch_size=args.batch_size)
        else:
            load_from_cypher_script(driver, args.cypher_file, database=args.database, batch_size=args.batch_size)

        duration = time.time() - start_time
        print(f"\n✓ Hoàn tất nạp dữ liệu vào Neo4j trong {duration:.2f} giây.")
        print_graph_stats(driver, database=args.database)
    except Exception as e:
        print(f"[ERROR] Quá trình nạp dữ liệu thất bại: {e}")
        driver.close()
        sys.exit(1)

    driver.close()
    return 0

if __name__ == "__main__":
    sys.exit(main() or 0)
