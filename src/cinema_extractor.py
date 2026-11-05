"""
cinema_extractor.py
Module phân tích cú pháp Infobox và khai thác thông tin từ văn bản sự nghiệp trên Wikipedia tiếng Việt.
Hỗ trợ bóc tách quan hệ có cấu trúc và trích xuất quan hệ văn bản (NLP Information Extraction).
"""

import re
from typing import List, Dict, Set, Tuple, Any

# Bộ lọc các namespace không phải bài viết trong liên kết wiki
IGNORED_PREFIXES = (
    "tập tin:", "file:", "hình:", "image:", "thể loại:", "category:",
    "bản mẫu:", "template:", "thảo luận:", "talk:", "trợ giúp:", "help:",
    "wikipedia:", "danh sách", "list of"
)

def extract_wiki_links(text: str) -> List[str]:
    """Trích xuất danh sách thực thể từ các liên kết dạng [[Tên trang|Tên hiển thị]] hoặc [[Tên trang]]."""
    if not text:
        return []
    
    matches = re.findall(r"\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]", text)
    valid_links = []
    for m in matches:
        clean = m.strip()
        lower = clean.lower()
        if any(lower.startswith(p) for p in IGNORED_PREFIXES):
            continue
        # Bỏ qua liên kết năm thuần số ví dụ [[2021]]
        if clean.isdigit() and len(clean) == 4:
            continue
        if clean and clean not in valid_links:
            valid_links.append(clean)
    return valid_links

def parse_infobox_field(wikitext: str, field_names: List[str]) -> str:
    """Tìm giá trị của một trường trong Infobox wikitext."""
    for field in field_names:
        # Chuẩn hóa khoảng trắng và gạch dưới
        field_parts = [re.escape(p) for p in re.split(r"[\s_]+", field) if p]
        pattern_field = r"[\s_]+".join(field_parts)
        pattern = r"(?:^|\n)\s*\|\s*" + pattern_field + r"\s*=\s*(.*?)(?=\n\s*[\|\}]|$)"
        match = re.search(pattern, wikitext, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""

def parse_movie_infobox(title: str, wikitext: str) -> Dict[str, Any]:
    """Phân tích Infobox phim / tác phẩm nghệ thuật."""
    is_movie = bool(re.search(r"\{\{\s*thông tin phim|\{\{\s*infobox film|\{\{\s*thông tin truyền hình", wikitext, re.IGNORECASE))
    
    if not is_movie:
        # Nếu tiêu đề có chữ "(phim" hoặc "(phim truyền hình"
        if "(phim" in title.lower() or "phim truyền hình" in title.lower():
            is_movie = True

    directors = extract_wiki_links(parse_infobox_field(wikitext, ["đạo diễn", "đạo_diễn", "director"]))
    actors = extract_wiki_links(parse_infobox_field(wikitext, ["diễn viên", "diễn_viên", "starring"]))
    producers = extract_wiki_links(parse_infobox_field(wikitext, ["sản xuất", "sản_xuất", "nhà_sản_xuất", "producer"]))
    studios = extract_wiki_links(parse_infobox_field(wikitext, ["hãng_sản_xuất", "hãng sản xuất", "công_ty_sản_xuất", "studio", "nhà_sản_xuất"]))
    
    year_raw = parse_infobox_field(wikitext, ["năm", "năm phát hành", "năm_phát_hành", "công chiếu", "phát sóng", "release_date"])
    year_match = re.search(r"\b(19\d\d|20\d\d)\b", year_raw)
    year = year_match.group(1) if year_match else ""
    if not year:
        # Thử tìm năm trong tiêu đề (ví dụ: Bố già (phim 2021))
        title_year = re.search(r"\b(19\d\d|20\d\d)\b", title)
        if title_year:
            year = title_year.group(1)

    return {
        "is_movie": is_movie,
        "directors": directors,
        "actors": actors,
        "producers": producers,
        "studios": studios,
        "year": year
    }

def parse_person_infobox(title: str, wikitext: str) -> Dict[str, Any]:
    """Phân tích Infobox diễn viên / đạo diễn / nghệ sĩ."""
    is_person = bool(re.search(r"\{\{\s*thông tin nhân vật|\{\{\s*thông tin nghệ sĩ|\{\{\s*infobox person", wikitext, re.IGNORECASE))
    
    spouses = extract_wiki_links(parse_infobox_field(wikitext, ["vợ_chồng", "vợ chồng", "spouse", "bạn_đời", "hôn phối"]))
    roles = parse_infobox_field(wikitext, ["công việc", "công_việc", "nghề nghiệp", "occupation"])
    affiliations = extract_wiki_links(parse_infobox_field(wikitext, ["nơi làm việc", "nơi_công_tác", "đơn vị", "đơn_vị", "nhà_hát", "hãng_phim"]))

    return {
        "is_person": is_person,
        "spouses": spouses,
        "roles": roles,
        "affiliations": affiliations
    }

KNOWN_ORGANIZATIONS = [
    "Sân khấu kịch Idecaf", "Sân khấu kịch Phú Nhuận", "Sân khấu kịch Hồng Vân",
    "Sân khấu kịch Hoàng Thái Thanh", "Sân khấu Thế Giới Trẻ", "Nhà hát Kịch Việt Nam",
    "Nhà hát Tuổi trẻ", "Nhà hát Kịch Hà Nội", "Nhà hát Cải lương Trần Hữu Trang",
    "Đoàn kịch Kim Cương", "Nhà hát Kịch Sân khấu nhỏ", "Trung tâm Phim truyền hình Việt Nam",
    "Hãng phim Truyền hình Thành phố Hồ Chí Minh", "Hãng phim Giải Phóng", "Hãng phim truyện Việt Nam",
    "Hãng phim Chánh Phương", "Hãng phim Phước Sang", "Hãng phim Phương Nam",
    "BHD", "Galaxy Studio", "CJ HK Entertainment", "Studio68", "Đoàn kịch nói Quân đội"
]

def extract_career_relations(
    person_title: str, 
    text: str, 
    known_entities: Set[str]
) -> List[Tuple[str, str, str, str]]:
    """
    Khai thác quan hệ từ văn bản (mục Sự nghiệp / Tiểu sử) bằng NLP Pattern Matching.
    Trả về danh sách tuple: (source_title, target_title, rel_type, evidence)
    """
    relations: List[Tuple[str, str, str, str]] = []
    if not text:
        return relations

    sentences = re.split(r"[.\n;]", text)

    # 1. Quan hệ MENTORED (Người nâng đỡ / Phát hiện tài năng / Thầy trò)
    mentored_patterns = [
        r"(?:được|nhờ có)\s+(?:nghệ sĩ\s+|nsnd\s+|nsƯt\s+|đạo diễn\s+)?([A-ZĐ][\w\s]+?)\s+(?:nâng đỡ|phát hiện|dìu dắt|dẫn dắt|chỉ bảo|nhận làm học trò|truyền nghề|chỉ dạy)",
        r"(?:học trò|đệ tử)\s+(?:của|thân thiết của)\s+([A-ZĐ][\w\s]+)",
        r"(?:người thầy|người dẫn dắt)\s+(?:của anh|của cô|của ông|của bà)?\s*(?:là|chính là)\s+([A-ZĐ][\w\s]+)",
        r"(?:theo học|học lớp diễn xuất của|được dạy dỗ bởi)\s+([A-ZĐ][\w\s]+)"
    ]

    # 2. Quan hệ CO_STARRED (Đóng cặp ăn ý / bạn diễn)
    costar_patterns = [
        r"(?:đóng cặp|kết đôi|bạn diễn ăn ý|hợp tác ăn ý|song hành)\s+(?:với|cùng)\s+([A-ZĐ][\w\s]+)",
        r"(?:cặp đôi màn ảnh|cặp đôi ăn ý)\s+(?:với|cùng)\s+([A-ZĐ][\w\s]+)"
    ]

    # 3. Quan hệ DIRECTED_ACTOR (Đạo diễn chỉ đạo diễn viên)
    director_actor_patterns = [
        r"được\s+(?:đạo diễn\s+)?([A-ZĐ][\w\s]+?)\s+(?:giao vai|chọn vào vai|mời tham gia|mời đóng|chỉ đạo diễn xuất|mời vào vai)",
        r"(?:dưới sự chỉ đạo của đạo diễn|làm việc cùng đạo diễn)\s+([A-ZĐ][\w\s]+)"
    ]

    # 4. Quan hệ FOUNDED (Sáng lập hãng phim / sân khấu)
    founder_patterns = [
        r"(?:sáng lập|thành lập|mở|lập ra|đồng sáng lập)\s+(?:hãng phim|công ty|sân khấu kịch|sân khấu|đoàn kịch)\s+([A-ZĐ][\w\s]+)",
        r"(?:chủ nhiệm|người sáng lập|giám đốc)\s+(?:của\s+)?(?:sân khấu|hãng phim|đoàn kịch)\s+([A-ZĐ][\w\s]+)"
    ]

    # 5. Quan hệ AFFILIATED_WITH (Nghệ sĩ gắn bó với Nhà hát / Sân khấu kịch)
    affiliation_patterns = [
        r"(?:công tác|làm việc|gắn bó|diễn viên|nghệ sĩ|gia nhập|đầu quân|thuộc biên chế)\s+(?:tại|ở|với|của)\s+([A-ZĐ][\w\s]+)"
    ]

    for sentence in sentences:
        s_clean = sentence.strip()
        if len(s_clean) < 15:
            continue

        # Kiểm tra MENTORED
        for pat in mentored_patterns:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                for ent in known_entities:
                    if (ent in target_cand or target_cand in ent) and ent != person_title and len(ent) > 3:
                        relations.append((ent, person_title, "MENTORED", s_clean[:120]))
                        break

        # Kiểm tra CO_STARRED
        for pat in costar_patterns:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                for ent in known_entities:
                    if (ent in target_cand or target_cand in ent) and ent != person_title and len(ent) > 3:
                        relations.append((person_title, ent, "CO_STARRED", s_clean[:120]))
                        break

        # Kiểm tra DIRECTED_ACTOR
        for pat in director_actor_patterns:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                for ent in known_entities:
                    if (ent in target_cand or target_cand in ent) and ent != person_title and len(ent) > 3:
                        relations.append((ent, person_title, "DIRECTED_ACTOR", s_clean[:120]))
                        break

        # Kiểm tra FOUNDED
        for pat in founder_patterns:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                for ent in list(known_entities) + KNOWN_ORGANIZATIONS:
                    if (ent in target_cand or target_cand in ent) and ent != person_title and len(ent) > 3:
                        relations.append((person_title, ent, "FOUNDED", s_clean[:120]))
                        break

        # Kiểm tra AFFILIATED_WITH
        for pat in affiliation_patterns:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                for org in KNOWN_ORGANIZATIONS:
                    if (org in target_cand or target_cand in org) and org != person_title:
                        relations.append((person_title, org, "AFFILIATED_WITH", s_clean[:120]))
                        break

    return relations
