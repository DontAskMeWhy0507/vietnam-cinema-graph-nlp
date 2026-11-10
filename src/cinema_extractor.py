"""
cinema_extractor.py
Module phân tích cú pháp Infobox và khai thác thông tin từ văn bản sự nghiệp trên Wikipedia tiếng Việt.
Hỗ trợ bóc tách quan hệ có cấu trúc và trích xuất quan hệ văn bản (NLP Information Extraction).
"""

import re
from typing import List, Dict, Set, Tuple, Any, Optional, Union

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

def clean_sentence_evidence(text: str) -> str:
    """Loại bỏ thẻ ref, bản mẫu chú thích, liên kết wiki và chuẩn hóa khoảng trắng trong văn bản làm bằng chứng."""
    if not text:
        return ""
    # 1. Bỏ thẻ tự đóng <ref ... /> TRƯỚC TIÊN để tránh nuốt văn bản tới </ref> kế tiếp
    cleaned = re.sub(r"<ref\b[^>]*?/>", "", text, flags=re.IGNORECASE)
    # 2. Bỏ thẻ cặp <ref>...</ref>
    cleaned = re.sub(r"<ref\b[^>]*>.*?</ref>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    # 3. Bỏ bảng wikitext {| ... |} và tiêu đề phần == ... ==
    cleaned = re.sub(r"\{\|.*?\|\}", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"={2,}.*?={2,}", "", cleaned)
    # 4. Bỏ bản mẫu chú thích / citation templates {{...}}
    for _ in range(3):
        cleaned = re.sub(r"\{\{[^{}]*\}\}", "", cleaned)
    # 5. Chuyển [[Link|Text]] -> Text, [[Link]] -> Link
    cleaned = re.sub(r"\[\[(?:[^\]\|]+\|)?([^\]]+)\]\]", r"\1", cleaned)
    # 6. Bỏ các thẻ HTML khác nếu có (<br>, <span>, v.v.)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    # 7. Bỏ định dạng wiki ''' hoặc ''
    cleaned = re.sub(r"'{2,}", "", cleaned)
    # 8. Chuẩn hóa khoảng trắng
    return re.sub(r"\s+", " ", cleaned).strip()

def sanitize_roles(raw: str) -> str:
    """Làm sạch trường vai trò / nghề nghiệp trong Infobox người, loại bỏ template wiki và html."""
    if not raw:
        return ""
    # 1. Bỏ chú thích HTML và thẻ ref (thẻ tự đóng trước, sau đó thẻ cặp)
    s = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)
    s = re.sub(r"<ref\b[^>]*?/>", "", s, flags=re.IGNORECASE)
    s = re.sub(r"<ref\b[^>]*>.*?</ref>", "", s, flags=re.DOTALL | re.IGNORECASE)
    # 2. Đổi thẻ ngắt dòng sang dấu phẩy
    s = re.sub(r"<br\s*/?>", ", ", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", " ", s)
    # 3. Bỏ tên template danh sách: {{hlist|...}}, {{ubl|...}}, {{flatlist|...}}, v.v.
    s = re.sub(r"\{\{(?:hlist|ubl|flatlist|plainlist|unbulleted list|bulleted list)?\|?", "", s, flags=re.IGNORECASE)
    s = s.replace("}}", "")
    # 4. Chuyển [[Link|Text]] -> Text, [[Link]] -> Link
    s = re.sub(r"\[\[(?:[^\]\|]+\|)?([^\]]+)\]\]", r"\1", s)
    # 5. Bỏ dấu đầu dòng * hoặc #
    s = re.sub(r"^\s*[*#]\s*", "", s, flags=re.MULTILINE)
    # 6. Phân tách danh sách theo dấu phẩy, chấm phẩy, gạch đứng, xuống dòng
    tokens = re.split(r"[,;\|\n\r]+", s)
    cleaned = []
    seen = set()
    for t in tokens:
        item = re.sub(r"\s+", " ", t).strip()
        if not item or len(item) < 2:
            continue
        # Bỏ các tham số cấu hình bản mẫu nếu còn sót
        if any(item.lower().startswith(p) for p in ("class=", "style=", "list_style=", "indent=")):
            continue
        if item.lower() in seen:
            continue
        seen.add(item.lower())
        cleaned.append(item)
    return ", ".join(cleaned)

def parse_infobox_field(wikitext: str, field_names: List[str]) -> str:
    """Tìm giá trị của một trường trong Infobox wikitext hỗ trợ template nhiều dòng và lồng nhau."""
    if not wikitext:
        return ""
    for field in field_names:
        field_parts = [re.escape(p) for p in re.split(r"[\s_]+", field) if p]
        pattern_field = r"[\s_]+".join(field_parts)
        m = re.search(r"(?:^|\n)[ \t]*\|[ \t]*" + pattern_field + r"[ \t]*=[ \t]*", wikitext, re.IGNORECASE)
        if not m:
            continue
        start_pos = m.end()
        i = start_pos
        depth = 0
        captured = []
        while i < len(wikitext):
            if wikitext[i:i+2] == "{{":
                depth += 1
                captured.append("{{")
                i += 2
                continue
            elif wikitext[i:i+2] == "}}":
                if depth == 0:
                    break
                depth -= 1
                captured.append("}}")
                i += 2
                continue
            elif depth == 0 and wikitext[i] == "\n":
                rest = wikitext[i+1:]
                # Next top-level infobox field (| field_name =) or end of infobox (}})
                if re.match(r"[ \t]*\|[ \t]*[\w\s_\.\-]+=", rest) or re.match(r"[ \t]*(\}\}|\|\})", rest):
                    break
            captured.append(wikitext[i])
            i += 1
        raw_val = "".join(captured).strip()
        if raw_val:
            return raw_val
    return ""

def parse_movie_infobox(title: str, wikitext: str) -> Dict[str, Any]:
    """Phân tích Infobox phim / tác phẩm nghệ thuật."""
    if not title:
        title = ""
    if not wikitext:
        return {
            "is_movie": False,
            "directors": [],
            "actors": [],
            "producers": [],
            "studios": [],
            "year": ""
        }

    is_movie = bool(re.search(
        r"\{\{\s*(?:thông tin phim|infobox[_ ]film|thông tin truyền hình|thông tin chương trình truyền hình|bảng tóm tắt về phim|phim chưa ra mắt|infobox television film|infobox television\b)", 
        wikitext, 
        re.IGNORECASE
    ))
    
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
    if not title:
        title = ""
    if not wikitext:
        return {
            "is_person": False,
            "spouses": [],
            "roles": "",
            "affiliations": []
        }

    is_person = bool(re.search(
        r"\{\{\s*(?:thông tin nhân vật|thông tin nghệ sĩ|infobox person|nghệ sĩ\b)", 
        wikitext, 
        re.IGNORECASE
    ))
    
    spouses = extract_wiki_links(parse_infobox_field(wikitext, ["vợ_chồng", "vợ chồng", "vợ", "chồng", "spouse", "bạn_đời", "bạn đời", "hôn phối"]))
    roles_raw = parse_infobox_field(wikitext, ["công việc", "công_việc", "nghề nghiệp", "occupation"])
    roles = sanitize_roles(roles_raw)
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

STOP_PERSON_PATTERNS = [
    "hội đồng", "nhà nước", "việt nam", "trường đại học", "đại học", "cao đẳng",
    "học viện", "nhà hát", "hãng phim", "sân khấu", "đoàn kịch", "liên hoan",
    "bộ văn hóa", "nghệ sĩ nhân dân", "nghệ sĩ ưu tú", "giải thưởng",
    "thành phố", "hà nội", "sài gòn", "hồ chí minh", "quân đội", "bộ quốc phòng",
    "ban giám khảo", "trung tâm", "công ty", "tạp chí", "đài truyền hình",
    "tiếng hát truyền hình", "học sinh", "sinh viên", "khóa học", "lớp học",
    "giám đốc", "chủ tịch", "tổng biên tập", "trưởng đoàn",
    "đường lên điện biên", "áo trắng sân trường", "ngày ấy mình đã yêu",
    "hai người mẹ", "đêm trắng", "ván bài lật ngửa", "lá sầu riêng",
    "bên trong vỏ kén vàng", "ngoài vòng pháp luật", "xin nhận nơi này làm quê hương",
    "sài gòn, anh yêu em", "đấu trí"
]

STOP_CITIES = {"hà nội", "sài gòn", "tp.hcm", "hồ chí minh", "thành phố hồ chí minh", "đà nẵng", "việt nam"}

def is_valid_person_candidate(
    cand: str, 
    known_artworks: Optional[Set[str]] = None, 
    known_orgs: Optional[Set[str]] = None
) -> bool:
    """Kiểm tra tên ứng viên Person có hợp lệ (>= 2 từ viết hoa, không phải từ chung, ban ngành, tác phẩm)."""
    if not cand or len(cand.strip()) < 3:
        return False
    cand_strip = cand.strip()
    cand_lower = cand_strip.lower()

    # Phải có ít nhất 2 từ viết hoa chữ cái đầu
    cap_tokens = [w for w in cand_strip.split() if w and (w[0].isupper() or w[0] in "ĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ")]
    if len(cap_tokens) < 2:
        return False

    # Không khớp với các từ dừng / ban ngành / tác phẩm mẫu
    for sp in STOP_PERSON_PATTERNS:
        if sp in cand_lower:
            return False

    # Không phải là tác phẩm trong danh mục
    if known_artworks:
        for art in known_artworks:
            art_base = re.sub(r"\s*\([^)]*\)", "", art).strip().lower()
            if cand_lower == art_base or cand_lower == art.lower():
                return False

    # Không phải là tổ chức trong danh mục
    if known_orgs:
        for org in known_orgs:
            org_base = re.sub(r"\s*\([^)]*\)", "", org).strip().lower()
            if cand_lower == org_base or cand_lower == org.lower():
                return False

    return True

def extract_person_name_prefix(text: str) -> str:
    """Trích xuất chuỗi các từ viết hoa liên tiếp ở đầu chuỗi (tên riêng của người)."""
    if not text:
        return ""
    clean = re.sub(
        r"^(?:cố nghệ sĩ|nghệ sĩ|nsnd|nsƯt|đạo diễn|thầy|cô|bác|chú|ca sĩ|nhạc sĩ|nhà văn|họa sĩ|soạn giả|diễn viên|người mẫu)\s+", 
        "", 
        text.strip(), 
        flags=re.IGNORECASE
    ).strip()
    
    tokens = []
    for w in clean.split():
        if w and (w[0].isupper() or w[0] in "ĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ"):
            tokens.append(w)
        else:
            break
    return " ".join(tokens)

def extract_career_relations(
    person_title: str, 
    text: str, 
    known_entities: Set[str],
    known_persons: Optional[Set[str]] = None,
    known_artworks: Optional[Set[str]] = None,
    known_orgs: Optional[Set[str]] = None
) -> List[Tuple[str, str, str, str]]:
    """
    Khai thác quan hệ từ văn bản (mục Sự nghiệp / Tiểu sử) bằng NLP Pattern Matching.
    Trả về danh sách tuple: (source_title, target_title, rel_type, evidence)
    """
    relations: List[Tuple[str, str, str, str]] = []
    if not text:
        return relations

    # Xây dựng tập hợp thực thể theo loại nếu chưa có
    artworks_set = set(known_artworks) if known_artworks else set()
    orgs_set = set(known_orgs) if known_orgs else set(KNOWN_ORGANIZATIONS)
    if known_persons is not None:
        persons_set = set(known_persons)
    else:
        # Nếu không cung cấp riêng, lọc từ known_entities bỏ qua các tác phẩm / tổ chức rõ ràng
        persons_set = set()
        for e in known_entities:
            el = e.lower()
            if any(k in el for k in ("(phim", "phim truyền hình", "(vở kịch", "hãng phim", "sân khấu", "nhà hát", "đoàn kịch", "công ty", "bhd", "galaxy", "studio")):
                continue
            if e in KNOWN_ORGANIZATIONS or e in artworks_set or e in orgs_set:
                continue
            persons_set.add(e)

    # Lập bản đồ tra cứu tên gốc (loại bỏ phần định danh trong ngoặc đơn)
    person_base_map: Dict[str, str] = {}
    for p in persons_set:
        base = re.sub(r"\s*\([^)]*\)", "", p).strip()
        person_base_map[base.lower()] = p
        person_base_map[p.lower()] = p

    # 1. Quan hệ MENTORED (Người nâng đỡ / Phát hiện tài năng / Thầy trò)
    mentored_patterns = [
        r"(?:được|nhờ có)\s+(?:nghệ sĩ\s+|nsnd\s+|nsƯt\s+|đạo diễn\s+|thầy\s+|cô\s+|nhạc sĩ\s+|nhà văn\s+|họa sĩ\s+|soạn giả\s+)?([A-ZĐ][\w\s]+?)\s+(?:nâng đỡ|phát hiện|dìu dắt|dẫn dắt|chỉ bảo|nhận làm học trò|truyền nghề|chỉ dạy)",
        r"(?:học trò|đệ tử)\s+(?:của|thân thiết của|ruột của)\s+(?:nghệ sĩ\s+|nsnd\s+|nsƯt\s+|đạo diễn\s+|thầy\s+|cô\s+|nhạc sĩ\s+|nhà văn\s+|họa sĩ\s+|soạn giả\s+)?([A-ZĐ][\w\s]+)",
        r"(?:người thầy|người dẫn dắt|người truyền nghề)\s+(?:của anh|của cô|của ông|của bà)?\s*(?:là|chính là)\s+(?:nghệ sĩ\s+|nsnd\s+|nsƯt\s+|đạo diễn\s+|thầy\s+|cô\s+|nhạc sĩ\s+|nhà văn\s+|họa sĩ\s+|soạn giả\s+)?([A-ZĐ][\w\s]+)",
        r"(?:theo học\s+(?:lớp của|khóa của|thầy|cô|nghệ sĩ|đạo diễn|nsnd|nsƯt|nhạc sĩ|nhà văn|họa sĩ|soạn giả)?|học lớp diễn xuất của|được dạy dỗ bởi)\s+([A-ZĐ][\w\s]+)",
        r"(?:nhận sự dìu dắt|nhận sự chỉ bảo|nhận sự dạy dỗ)\s+của\s+(?:nghệ sĩ\s+|nsnd\s+|nsƯt\s+|đạo diễn\s+|thầy\s+|cô\s+|bác\s+|chú\s+|nhạc sĩ\s+|nhà văn\s+|họa sĩ\s+|soạn giả\s+)?([A-ZĐ][\w\s]+)"
    ]

    # 2. Quan hệ CO_STARRED (Đóng cặp ăn ý / bạn diễn)
    costar_patterns = [
        r"(?:đóng cặp(?:\s+ăn ý)?|kết đôi|bạn diễn ăn ý|hợp tác ăn ý|song hành)\s+(?:với|cùng)\s+([A-ZĐ][\w\s]+)",
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
        r"(?:công tác|cộng tác|làm việc|gắn bó|diễn viên|nghệ sĩ|gia nhập|đầu quân|thuộc biên chế|trực thuộc|hoạt động)(?:\s+nghệ thuật)?(?:\s+thường xuyên|\s+lâu năm)?\s+(?:tại|ở|với|của)\s+([A-ZĐ][\w\s]+)"
    ]

    # Tách câu dựa trên văn bản đã làm sạch thẻ và liên kết wiki
    clean_full_text = clean_sentence_evidence(text)
    sentences = re.split(r"[.\n;]", clean_full_text)

    for sentence in sentences:
        s_clean = re.sub(r"\s+", " ", sentence).strip()
        if len(s_clean) < 15:
            continue
        # Bỏ qua nếu còn sót mã bảng wikitext
        if "{|" in s_clean or "|}" in s_clean or "wikitable" in s_clean:
            continue
        ev_snippet = s_clean[:300]

        # Kiểm tra MENTORED
        for pat in mentored_patterns:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                # Tránh các mệnh đề phức gây đảo ngược vai trò (ví dụ: 'được X xem như chị ruột vì từng dìu dắt...')
                if any(sw in target_cand.lower().split() for sw in ("xem", "như", "vì", "từng", "ruột")):
                    continue
                # Tách nếu ứng viên gồm nhiều người nối bằng và/cùng/với
                sub_cands = [c.strip() for c in re.split(r"[,;]|\bvà\b|\bcùng\b|\bvới\b", target_cand) if c.strip()]
                for cand in sub_cands:
                    clean_c = extract_person_name_prefix(cand)
                    if not is_valid_person_candidate(clean_c, artworks_set, orgs_set):
                        continue
                    matched_ent = None
                    if clean_c.lower() in person_base_map:
                        matched_ent = person_base_map[clean_c.lower()]
                    else:
                        for p_base, p_orig in person_base_map.items():
                            if len(p_base) > 4 and (p_base == clean_c.lower() or p_base.endswith(clean_c.lower())):
                                if len(clean_c.split()) >= 2:
                                    matched_ent = p_orig
                                    break
                    if matched_ent and matched_ent != person_title and matched_ent in persons_set:
                        relations.append((matched_ent, person_title, "MENTORED", ev_snippet))
                        break

        # Kiểm tra CO_STARRED
        for pat in costar_patterns:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                sub_cands = [c.strip() for c in re.split(r"[,;]|\bvà\b|\bcùng\b|\bvới\b", target_cand) if c.strip()]
                for cand in sub_cands:
                    clean_c = extract_person_name_prefix(cand)
                    if not is_valid_person_candidate(clean_c, artworks_set, orgs_set):
                        continue
                    matched_ent = None
                    if clean_c.lower() in person_base_map:
                        matched_ent = person_base_map[clean_c.lower()]
                    else:
                        for p_base, p_orig in person_base_map.items():
                            if len(p_base) > 4 and (p_base == clean_c.lower() or p_base.endswith(clean_c.lower())):
                                if len(clean_c.split()) >= 2:
                                    matched_ent = p_orig
                                    break
                    if matched_ent and matched_ent != person_title and matched_ent in persons_set:
                        relations.append((person_title, matched_ent, "CO_STARRED", ev_snippet))
                        break

        # Kiểm tra DIRECTED_ACTOR
        for pat in director_actor_patterns:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                sub_cands = [c.strip() for c in re.split(r"[,;]|\bvà\b|\bcùng\b|\bvới\b", target_cand) if c.strip()]
                for cand in sub_cands:
                    clean_c = extract_person_name_prefix(cand)
                    if not is_valid_person_candidate(clean_c, artworks_set, orgs_set):
                        continue
                    matched_ent = None
                    if clean_c.lower() in person_base_map:
                        matched_ent = person_base_map[clean_c.lower()]
                    else:
                        for p_base, p_orig in person_base_map.items():
                            if len(p_base) > 4 and (p_base == clean_c.lower() or p_base.endswith(clean_c.lower())):
                                if len(clean_c.split()) >= 2:
                                    matched_ent = p_orig
                                    break
                    if matched_ent and matched_ent != person_title and matched_ent in persons_set:
                        relations.append((matched_ent, person_title, "DIRECTED_ACTOR", ev_snippet))
                        break

        # Kiểm tra FOUNDED
        for pat in founder_patterns:
            # Bỏ qua nếu câu chỉ nói về múa phụ họa hoặc người thân là giám đốc
            if any(neg in s_clean.lower() for neg in ("phụ họa", "mời qua múa", "anh rể", "chị dâu", "em rể", "anh họ")):
                continue
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                cand_clean = re.sub(r"\[\[(?:[^\]\|]+\|)?([^\]]+)\]\]", r"\1", target_cand).strip()
                cand_clean = re.sub(r"[\"']", "", cand_clean).strip()
                cand_lower = cand_clean.lower()
                # Ứng viên phải là tổ chức, không được là thành phố hoặc từ chung
                if cand_lower in STOP_CITIES or cand_lower in ("việt nam", "công ty riêng", "công ty luật", "sân khấu này"):
                    continue
                if any(sp in cand_lower for sp in ("phim", "vở kịch", "công ty riêng", "công ty luật")):
                    if not any(k in cand_lower for k in ("hãng phim", "sân khấu", "nhà hát", "đoàn kịch")):
                        continue
                for org in orgs_set:
                    org_lower = org.lower()
                    org_base = re.sub(r"^(?:hãng phim|sân khấu kịch|sân khấu|nhà hát|đoàn kịch|công ty cổ phần phim|công ty)\s+", "", org, flags=re.IGNORECASE).strip().lower()
                    if (org_lower == cand_lower or 
                        (org_base and org_base == cand_lower) or 
                        (org_lower in cand_lower and len(org) >= 6) or 
                        (len(cand_clean) >= 6 and len(cand_clean.split()) >= 2 and cand_lower in org_lower)):
                        relations.append((person_title, org, "FOUNDED", ev_snippet))
                        break

        # Kiểm tra AFFILIATED_WITH
        for pat in affiliation_patterns:
            m = re.search(pat, s_clean, re.IGNORECASE)
            if m:
                target_cand = m.group(1).strip()
                cand_lower = target_cand.lower()
                # Tránh các thành phố lớn hoặc từ thông dụng gây nhận diện sai (ví dụ: Hà Nội -> Nhà hát Kịch Hà Nội)
                if cand_lower in STOP_CITIES:
                    continue
                for org in orgs_set:
                    org_lower = org.lower()
                    # Phải là tổ chức khớp chính xác hoặc tên tổ chức (>= 8 ký tự) xuất hiện đầy đủ trong target_cand
                    if org_lower == cand_lower or (org_lower in cand_lower and len(org) >= 8):
                        if org != person_title:
                            relations.append((person_title, org, "AFFILIATED_WITH", ev_snippet))
                            break

    return relations
