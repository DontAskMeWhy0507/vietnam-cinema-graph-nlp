"""
crawl_vietnam_cinema.py
Thu thập dữ liệu toàn diện về Điện ảnh & Sân khấu Việt Nam từ Wikipedia tiếng Việt.
Trích xuất Infobox và văn bản Sự nghiệp để xây dựng đồ thị mạng xã hội chuẩn SNA:
- Hơn 2.000 nút (Person, Artwork, Organization)
- Hơn 5.000 cạnh
- 10 loại quan hệ chi tiết (DIRECTED, ACTED_IN, DIRECTED_ACTOR, CO_STARRED, MENTORED, 
  PRODUCED, PRODUCED_BY, AFFILIATED_WITH, FOUNDED, MARRIED_TO)
- Xuất file CSV (nodes, edges) và script nạp CSDL Neo4j (import_neo4j.cypher).
"""

import os
import sys
import time
import logging
from typing import Set, Dict, List, Tuple, Any
import httpx

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cinema_models import Node, Edge, CinemaGraph
from cinema_extractor import (
    parse_movie_infobox,
    parse_person_infobox,
    extract_career_relations,
    extract_wiki_links
)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("VNCinemaCrawler")

API_ENDPOINT = "https://vi.wikipedia.org/w/api.php"
USER_AGENT = "VNCinemaSNA/1.0 (Student Academic Project; contact: student@example.com)"

SEED_CATEGORIES = [
    "Thể_loại:Diễn_viên_Việt_Nam",
    "Thể_loại:Đạo_diễn_Việt_Nam",
    "Thể_loại:Nhà_sản_xuất_phim_Việt_Nam",
    "Thể_loại:Người_làm_điện_ảnh_Việt_Nam",
    "Thể_loại:Nghệ_sĩ_hài_Việt_Nam",
    "Thể_loại:Nghệ_sĩ_cải_lương",
    "Thể_loại:Nghệ_sĩ_kịch_nói_Việt_Nam",
    "Thể_loại:Nghệ_sĩ_nhân_dân_Việt_Nam",
    "Thể_loại:Nghệ_sĩ_ưu_tú_Việt_Nam",
    "Thể_loại:Phim_Việt_Nam",
    "Thể_loại:Phim_truyền_hình_Việt_Nam",
    "Thể_loại:Phim_điện_ảnh_Việt_Nam",
    "Thể_loại:Công_ty_sản_xuất_phim_Việt_Nam",
    "Thể_loại:Sân_khấu_Việt_Nam",
    "Thể_loại:Nhà_hát_Việt_Nam"
]

def normalize_id(title: str) -> str:
    """Chuẩn hóa tiêu đề thành id duy nhất."""
    clean = title.strip().lower()
    # Loại bỏ tiền tố namespace nếu có
    if ":" in clean:
        clean = clean.split(":", 1)[1]
    return clean.replace(" ", "_")

def collect_titles_from_categories(client: httpx.Client, max_categories: int = 150) -> Set[str]:
    """Thu thập danh sách tiêu đề bài viết từ cây thể loại Wikipedia."""
    logger.info("Bắt đầu thu thập danh sách bài viết từ cây thể loại Điện ảnh - Sân khấu...")
    visited_cats: Set[str] = set()
    collected_titles: Set[str] = set()
    cat_queue = list(SEED_CATEGORIES)

    while cat_queue and len(visited_cats) < max_categories:
        cat = cat_queue.pop(0)
        if cat in visited_cats:
            continue
        visited_cats.add(cat)

        cmcontinue = None
        while True:
            params = {
                "action": "query",
                "format": "json",
                "list": "categorymembers",
                "cmtitle": cat,
                "cmlimit": 500
            }
            if cmcontinue:
                params["cmcontinue"] = cmcontinue

            try:
                res = client.get(API_ENDPOINT, params=params).json()
            except Exception as e:
                logger.warning("Lỗi truy vấn thể loại '%s': %s", cat, e)
                break

            members = res.get("query", {}).get("categorymembers", [])
            for m in members:
                title = m.get("title", "")
                ns = m.get("ns", 0)
                if ns == 0 and not title.startswith("Danh sách"):
                    collected_titles.add(title)
                elif ns == 14 and title not in visited_cats and len(visited_cats) + len(cat_queue) < max_categories * 2:
                    cat_queue.append(title)

            cmcontinue = res.get("continue", {}).get("cmcontinue")
            if not cmcontinue:
                break

    logger.info("Đã quét qua %d thể loại, thu thập được %d bài viết tiềm năng.", len(visited_cats), len(collected_titles))
    return collected_titles

def fetch_articles_content(client: httpx.Client, titles: List[str], batch_size: int = 40) -> Dict[str, str]:
    """Tải nội dung wikitext của các bài viết theo từng đợt (batching)."""
    logger.info("Bắt đầu tải nội dung wikitext cho %d bài viết...", len(titles))
    results: Dict[str, str] = {}
    
    for i in range(0, len(titles), batch_size):
        batch = titles[i:i + batch_size]
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "titles": "|".join(batch)
        }
        try:
            resp = client.get(API_ENDPOINT, params=params).json()
            pages = resp.get("query", {}).get("pages", {})
            for pid, p in pages.items():
                title = p.get("title", "")
                revisions = p.get("revisions", [])
                if revisions:
                    content = revisions[0].get("slots", {}).get("main", {}).get("*", "")
                    if content and len(content) > 50:
                        results[title] = content
        except Exception as e:
            logger.warning("Lỗi tải đợt %d-%d: %s", i, i + len(batch), e)

        time.sleep(0.1)
        if (i // batch_size) % 10 == 0:
            logger.info("Tiến độ tải: %d/%d bài viết (%.1f%%)", len(results), len(titles), (len(results)/len(titles))*100)

    logger.info("Hoàn tất tải wikitext. Tổng cộng %d bài viết có nội dung.", len(results))
    return results

def build_vietnam_cinema_graph() -> CinemaGraph:
    """Xây dựng đồ thị tri thức và mạng xã hội hoàn chỉnh."""
    graph = CinemaGraph()

    import json
    cache_file = os.path.join(DATA_DIR, "vietnam_cinema_articles_cache.json")
    if not os.path.exists(cache_file):
        alt_cache = os.path.join(ROOT_DIR, "vietnam_cinema_articles_cache.json")
        if os.path.exists(alt_cache):
            cache_file = alt_cache

    if os.path.exists(cache_file):
        logger.info("Phát hiện file cache '%s', đang nạp dữ liệu offline...", cache_file)
        with open(cache_file, mode="r", encoding="utf-8") as f:
            articles_data = json.load(f)
        logger.info("Đã nạp thành công %d bài viết từ cache.", len(articles_data))
    else:
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30.0) as client:
            # 1. Thu thập danh sách bài viết
            titles_set = collect_titles_from_categories(client, max_categories=180)
            titles_list = list(titles_set)
            
            # 2. Tải wikitext
            articles_data = fetch_articles_content(client, titles_list, batch_size=40)
            
            with open(cache_file, mode="w", encoding="utf-8") as f:
                json.dump(articles_data, f, ensure_ascii=False)
            logger.info("Đã lưu cache vào '%s'.", cache_file)

    logger.info("Bắt đầu xử lý NLP và trích xuất quan hệ có cấu trúc...")

    # Tập hợp các thực thể đã biết để phục vụ Entity Linking và trích xuất văn bản
    known_entities: Set[str] = set(articles_data.keys())

    # Lưu trữ tạm các quan hệ phát hiện được
    extracted_edges: List[Edge] = []
    
    # Track movie co-starring pairs to find frequent collaborations
    movie_actor_map: Dict[str, List[str]] = {}
    movie_director_map: Dict[str, List[str]] = {}

    for title, wikitext in articles_data.items():
        title_id = normalize_id(title)
        
        # Phân tích Infobox phim
        movie_info = parse_movie_infobox(title, wikitext)
        # Phân tích Infobox người
        person_info = parse_person_infobox(title, wikitext)

        # Phân loại Node
        if movie_info["is_movie"]:
            graph.add_node(Node(
                id=title_id,
                name=title,
                label="Artwork",
                metadata={"type": "Phim điện ảnh / Truyền hình", "year": movie_info["year"]}
            ))
            
            # Quan hệ 1: DIRECTED (Đạo diễn -> Phim)
            for d in movie_info["directors"]:
                d_id = normalize_id(d)
                graph.add_node(Node(id=d_id, name=d, label="Person", metadata={"roles": "Đạo diễn"}))
                extracted_edges.append(Edge(source_id=d_id, target_id=title_id, rel_type="DIRECTED", evidence=f"Đạo diễn phim {title}"))
            
            # Quan hệ 2: ACTED_IN (Diễn viên -> Phim)
            for a in movie_info["actors"]:
                a_id = normalize_id(a)
                graph.add_node(Node(id=a_id, name=a, label="Person", metadata={"roles": "Diễn viên"}))
                extracted_edges.append(Edge(source_id=a_id, target_id=title_id, rel_type="ACTED_IN", evidence=f"Diễn viên trong {title}"))

            # Quan hệ 6: PRODUCED (Nhà sản xuất -> Phim)
            for p in movie_info["producers"]:
                p_id = normalize_id(p)
                graph.add_node(Node(id=p_id, name=p, label="Person", metadata={"roles": "Nhà sản xuất"}))
                extracted_edges.append(Edge(source_id=p_id, target_id=title_id, rel_type="PRODUCED", evidence=f"Nhà sản xuất phim {title}"))

            # Quan hệ 7: PRODUCED_BY (Phim -> Hãng phim/Đài truyền hình)
            for s in movie_info["studios"]:
                s_id = normalize_id(s)
                graph.add_node(Node(id=s_id, name=s, label="Organization", metadata={"type": "Hãng phim / Đài truyền hình"}))
                extracted_edges.append(Edge(source_id=title_id, target_id=s_id, rel_type="PRODUCED_BY", evidence=f"Sản xuất bởi {s}"))

            movie_actor_map[title_id] = [normalize_id(a) for a in movie_info["actors"]]
            movie_director_map[title_id] = [normalize_id(d) for d in movie_info["directors"]]

        elif any(k in title.lower() for k in ["hãng phim", "sân khấu", "nhà hát", "đoàn kịch", "công ty cổ phần phim", "bhd", "galaxy"]):
            graph.add_node(Node(
                id=title_id,
                name=title,
                label="Organization",
                metadata={"type": "Đơn vị nghệ thuật"}
            ))
        else:
            # Mặc định là Person
            graph.add_node(Node(
                id=title_id,
                name=title,
                label="Person",
                metadata={"roles": person_info["roles"]}
            ))

            # Quan hệ 10: MARRIED_TO (Vợ chồng / Cặp đôi nghệ sĩ)
            for sp in person_info["spouses"]:
                sp_id = normalize_id(sp)
                graph.add_node(Node(id=sp_id, name=sp, label="Person", metadata={"roles": "Nghệ sĩ"}))
                extracted_edges.append(Edge(source_id=title_id, target_id=sp_id, rel_type="MARRIED_TO", evidence="Vợ chồng / Bạn đời"))
                extracted_edges.append(Edge(source_id=sp_id, target_id=title_id, rel_type="MARRIED_TO", evidence="Vợ chồng / Bạn đời"))

            # Quan hệ 8: AFFILIATED_WITH (Nghệ sĩ -> Nhà hát / Sân khấu)
            for org in person_info["affiliations"]:
                org_id = normalize_id(org)
                graph.add_node(Node(id=org_id, name=org, label="Organization", metadata={"type": "Nhà hát / Sân khấu"}))
                extracted_edges.append(Edge(source_id=title_id, target_id=org_id, rel_type="AFFILIATED_WITH", evidence=f"Công tác tại {org}"))

            # Trích xuất quan hệ từ văn bản sự nghiệp (MENTORED, CO_STARRED, DIRECTED_ACTOR, FOUNDED)
            text_rels = extract_career_relations(title, wikitext, known_entities)
            for s_ent, t_ent, r_type, ev in text_rels:
                s_id = normalize_id(s_ent)
                t_id = normalize_id(t_ent)
                
                # Xác định label phù hợp
                if r_type == "FOUNDED":
                    graph.add_node(Node(id=s_id, name=s_ent, label="Person"))
                    graph.add_node(Node(id=t_id, name=t_ent, label="Organization"))
                else:
                    graph.add_node(Node(id=s_id, name=s_ent, label="Person"))
                    graph.add_node(Node(id=t_id, name=t_ent, label="Person"))
                    
                extracted_edges.append(Edge(source_id=s_id, target_id=t_id, rel_type=r_type, evidence=ev))

    logger.info("Đang suy luận quan hệ dẫn xuất (DIRECTED_ACTOR & CO_STARRED) từ danh sách phim...")
    # Quan hệ 3: DIRECTED_ACTOR (Đạo diễn -> Diễn viên)
    # Quan hệ 4: CO_STARRED (Diễn viên <-> Diễn viên đóng chung/đóng cặp)
    co_star_count: Dict[Tuple[str, str], int] = {}
    
    for m_id, actors in movie_actor_map.items():
        directors = movie_director_map.get(m_id, [])
        # Đạo diễn chỉ đạo diễn viên
        for d_id in directors:
            for a_id in actors:
                if d_id != a_id:
                    extracted_edges.append(Edge(
                        source_id=d_id,
                        target_id=a_id,
                        rel_type="DIRECTED_ACTOR",
                        evidence="Đạo diễn chỉ đạo diễn xuất trong tác phẩm"
                    ))

        # Đóng chung phim (giới hạn tối đa 10 diễn viên chính mỗi phim để đảm bảo độ chính xác cao)
        main_actors = actors[:10]
        for idx1 in range(len(main_actors)):
            for idx2 in range(idx1 + 1, len(main_actors)):
                act1, act2 = main_actors[idx1], main_actors[idx2]
                pair = tuple(sorted([act1, act2]))
                co_star_count[pair] = co_star_count.get(pair, 0) + 1

    # Thêm cạnh CO_STARRED hai chiều cho các diễn viên đóng chung phim
    for (act1, act2), count in co_star_count.items():
        evidence_str = f"Đóng chung trong {count} tác phẩm"
        extracted_edges.append(Edge(source_id=act1, target_id=act2, rel_type="CO_STARRED", evidence=evidence_str))
        extracted_edges.append(Edge(source_id=act2, target_id=act1, rel_type="CO_STARRED", evidence=evidence_str))

    # Ràng buộc Schema Type Check để đảm bảo độ chính xác > 95%
    VALID_EDGE_CONSTRAINTS = {
        "DIRECTED": ("Person", "Artwork"),
        "ACTED_IN": ("Person", "Artwork"),
        "PRODUCED": ("Person", "Artwork"),
        "PRODUCED_BY": ("Artwork", "Organization"),
        "DIRECTED_ACTOR": ("Person", "Person"),
        "CO_STARRED": ("Person", "Person"),
        "MENTORED": ("Person", "Person"),
        "MARRIED_TO": ("Person", "Person"),
        "FOUNDED": ("Person", "Organization"),
        "AFFILIATED_WITH": ("Person", "Organization"),
    }

    logger.info("Lọc và kiểm tra tính hợp lệ của %d cạnh theo Ontology Schema...", len(extracted_edges))
    valid_edges_count = 0
    for edge in extracted_edges:
        if edge.source_id in graph.nodes and edge.target_id in graph.nodes:
            s_label = graph.nodes[edge.source_id].label
            t_label = graph.nodes[edge.target_id].label
            expected = VALID_EDGE_CONSTRAINTS.get(edge.rel_type)
            if expected:
                exp_s, exp_t = expected
                # Nếu nhãn khớp hoặc có thể tự động điều chỉnh nếu phù hợp
                if s_label == exp_s and t_label == exp_t:
                    if graph.add_edge(edge):
                        valid_edges_count += 1
                elif edge.rel_type == "AFFILIATED_WITH" and s_label == "Person":
                    # Đảm bảo target được gán nhãn Organization
                    graph.nodes[edge.target_id].label = "Organization"
                    if graph.add_edge(edge):
                        valid_edges_count += 1
                elif edge.rel_type == "FOUNDED" and s_label == "Person":
                    graph.nodes[edge.target_id].label = "Organization"
                    if graph.add_edge(edge):
                        valid_edges_count += 1

    logger.info("Đã nạp thành công %d cạnh hợp lệ vào đồ thị.", len(graph.edges))

    logger.info("=== KẾT QUẢ XÂY DỰNG ĐỒ THỊ ===")
    logger.info("Tổng số nút (Nodes): %d", len(graph.nodes))
    logger.info("Tổng số cạnh (Edges): %d", len(graph.edges))
    return graph

def main():
    graph = build_vietnam_cinema_graph()

    nodes_file = os.path.join(DATA_DIR, "vietnam_cinema_nodes.csv")
    edges_file = os.path.join(DATA_DIR, "vietnam_cinema_edges.csv")
    cypher_file = os.path.join(DATA_DIR, "import_neo4j.cypher")

    logger.info("Đang xuất file CSV: '%s' và '%s'...", nodes_file, edges_file)
    graph.export_csv(nodes_file, edges_file)

    logger.info("Đang xuất kịch bản Cypher cho Neo4j: '%s'...", cypher_file)
    graph.export_neo4j_cypher(cypher_file)

    logger.info("=== HOÀN TẤT CRAWL VÀ XÂY DỰNG ĐỒ THỊ! ===")

if __name__ == "__main__":
    main()
