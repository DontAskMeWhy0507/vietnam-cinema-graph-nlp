"""
test_cinema_extractor.py
Bộ kiểm thử toàn diện cho module cinema_extractor:
- Kiểm thử phân tích liên kết wiki và infobox
- Kiểm thử làm sạch wikitext và bằng chứng (clean_sentence_evidence)
- Kiểm thử chuẩn hóa vai trò (sanitize_roles)
- Kiểm thử bộ lọc ứng viên thực thể người (is_valid_person_candidate)
- Kiểm thử các ca dương tính và âm tính của quan hệ sự nghiệp (MENTORED, CO_STARRED, DIRECTED_ACTOR, FOUNDED, AFFILIATED_WITH)
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from cinema_extractor import (
    extract_wiki_links,
    parse_movie_infobox,
    parse_person_infobox,
    clean_sentence_evidence,
    sanitize_roles,
    is_valid_person_candidate,
    extract_career_relations,
    KNOWN_ORGANIZATIONS
)

def test_extract_wiki_links():
    text = "* [[Trấn Thành]]\n* [[Tuấn Trần]]\n* [[Lê Giang (nghệ sĩ)|Lê Giang]]\n* [[Tập tin:Pic.jpg]]\n* [[2021]]"
    links = extract_wiki_links(text)
    assert "Trấn Thành" in links
    assert "Tuấn Trần" in links
    assert "Lê Giang (nghệ sĩ)" in links
    assert "Tập tin:Pic.jpg" not in links
    assert "2021" not in links

def test_parse_movie_infobox_standard():
    wikitext = """
{{Thông tin phim
| tên = Bố già
| đạo diễn = {{Liệt kê|
* [[Trấn Thành]]
* [[Vũ Ngọc Đãng]]
}}
| sản xuất = [[Nguyễn Phương Thảo]]
| diễn viên = {{Liệt kê|
* [[Trấn Thành]]
* [[Tuấn Trần]]
* [[Lê Giang (nghệ sĩ)|Lê Giang]]
}}
| hãng_sản_xuất = [[Galaxy Studio]]
| năm phát hành = 2021
}}
"""
    result = parse_movie_infobox("Bố già (phim 2021)", wikitext)
    assert result["is_movie"] is True
    assert "Trấn Thành" in result["directors"]
    assert "Vũ Ngọc Đãng" in result["directors"]
    assert "Tuấn Trần" in result["actors"]
    assert "Nguyễn Phương Thảo" in result["producers"]
    assert "Galaxy Studio" in result["studios"]
    assert result["year"] == "2021"

def test_parse_movie_infobox_extended_templates():
    # Kiểm thử template bảng tóm tắt về phim (như Scandal: Bí mật thảm đỏ)
    wikitext = """
{{Bảng tóm tắt về phim
| name = Scandal: Bí mật thảm đỏ
| director = [[Victor Vũ]]
| producer = [[Phạm Việt Anh Khoa]]
| starring = [[Vân Trang]]<br />[[Maya (ca sĩ)|Maya]]
| studio = [[Galaxy Studio]]
| release_date = 2012
}}
"""
    res = parse_movie_infobox("Scandal: Bí mật thảm đỏ", wikitext)
    assert res["is_movie"] is True
    assert "Victor Vũ" in res["directors"]
    assert "Vân Trang" in res["actors"]
    assert res["year"] == "2012"

def test_clean_sentence_evidence():
    dirty = (
        '<ref name=":9" /><ref>{{chú thích web|url=https://example.com|tựa đề=Test}}</ref>'
        " Năm 2005, ông tốt nghiệp tại [[Trường Đại học Sân khấu và Điện ảnh Hà Nội|Đại học Sân khấu Điện ảnh]]."
    )
    cleaned = clean_sentence_evidence(dirty)
    assert "<ref" not in cleaned
    assert "chú thích web" not in cleaned
    assert "[[" not in cleaned
    assert "Đại học Sân khấu Điện ảnh" in cleaned
    assert cleaned.startswith("Năm 2005")

def test_sanitize_roles():
    assert sanitize_roles("{{hlist|Diễn viên|Người mẫu}}") == "Diễn viên, Người mẫu"
    assert sanitize_roles("{{hlist||[[Diễn viên]]|[[Nghệ sĩ hài]]|[[Người dẫn chương trình]]}}") == "Diễn viên, Nghệ sĩ hài, Người dẫn chương trình"
    assert sanitize_roles("Người dẫn chương trình<br>Doanh nhân<br>Ca sĩ") == "Người dẫn chương trình, Doanh nhân, Ca sĩ"
    assert sanitize_roles("{{ubl|[[Đạo diễn]]|[[Biên kịch]]}}") == "Đạo diễn, Biên kịch"
    assert sanitize_roles("[[Diễn viên điện ảnh]]") == "Diễn viên điện ảnh"
    assert sanitize_roles("") == ""

def test_parse_person_infobox_with_sanitized_roles():
    wikitext = """
{{Thông tin nhân vật
| tên = Trấn Thành
| công việc = {{hlist|[[Diễn viên]]|[[Nghệ sĩ hài]]|[[Người dẫn chương trình]]}}
| spouse = {{marriage|[[Hari Won]]|2016}}
| nơi công tác = [[Sân khấu kịch Idecaf]]
}}
"""
    result = parse_person_infobox("Trấn Thành", wikitext)
    assert result["is_person"] is True
    assert "Hari Won" in result["spouses"]
    assert "Sân khấu kịch Idecaf" in result["affiliations"]
    # Vai trò phải được làm sạch, không chứa bản mẫu wiki {{hlist...}} hay liên kết [[...]]
    assert result["roles"] == "Diễn viên, Nghệ sĩ hài, Người dẫn chương trình"
    assert "{{" not in result["roles"]
    assert "[[" not in result["roles"]

def test_is_valid_person_candidate():
    known_art = {"Đường lên Điện Biên", "Áo trắng sân trường", "Ngày ấy mình đã yêu", "Bên trong vỏ kén vàng"}
    known_org = {"Nhà hát Kịch Hà Nội", "Hãng phim Giải Phóng"}

    # Hợp lệ: Tên người >= 2 từ viết hoa
    assert is_valid_person_candidate("Hữu Châu", known_art, known_org) is True
    assert is_valid_person_candidate("Việt Anh", known_art, known_org) is True
    assert is_valid_person_candidate("Ninh Dương Lan Ngọc", known_art, known_org) is True

    # Không hợp lệ: Tên đơn / từ chung / viết thường
    assert is_valid_person_candidate("Hà", known_art, known_org) is False
    assert is_valid_person_candidate("học", known_art, known_org) is False
    assert is_valid_person_candidate("chèo", known_art, known_org) is False

    # Không hợp lệ: Ban ngành / Hội đồng / Thành phố
    assert is_valid_person_candidate("Hội đồng cấp Nhà nước", known_art, known_org) is False
    assert is_valid_person_candidate("Ủy ban Nhân dân Thành phố Hà Nội", known_art, known_org) is False
    assert is_valid_person_candidate("Trường Đại học Sân khấu và Điện ảnh Hà Nội", known_art, known_org) is False

    # Không hợp lệ: Tên tác phẩm điện ảnh
    assert is_valid_person_candidate("Đường lên Điện Biên", known_art, known_org) is False
    assert is_valid_person_candidate("Áo trắng sân trường", known_art, known_org) is False
    assert is_valid_person_candidate("Bên trong vỏ kén vàng", known_art, known_org) is False

def test_extract_career_relations_positive():
    text = (
        "Trấn Thành được nghệ sĩ Hữu Châu và NSND Việt Anh nâng đỡ nhiệt tình trong những ngày đầu bước vào nghề sân khấu. "
        "Anh từng đóng cặp ăn ý cùng Ninh Dương Lan Ngọc trong bộ phim Cua lại vợ bầu. "
        "Ngoài ra, Ngô Thanh Vân đã sáng lập Studio68 để sản xuất nhiều bộ phim chiếu rạp. "
        "Nam diễn viên từng công tác tại Sân khấu kịch Idecaf trong nhiều năm."
    )
    known = {"Hữu Châu", "Việt Anh", "Trấn Thành", "Ninh Dương Lan Ngọc", "Ngô Thanh Vân", "Studio68", "Sân khấu kịch Idecaf"}
    persons = {"Hữu Châu", "Việt Anh", "Trấn Thành", "Ninh Dương Lan Ngọc", "Ngô Thanh Vân"}
    orgs = {"Studio68", "Sân khấu kịch Idecaf"}
    
    relations = extract_career_relations("Trấn Thành", text, known, known_persons=persons, known_orgs=orgs)
    types_found = {r[2] for r in relations}
    
    assert "MENTORED" in types_found
    assert "CO_STARRED" in types_found
    assert "AFFILIATED_WITH" in types_found
    
    # Kiểm tra cấu trúc cạnh MENTORED
    mentored = [r for r in relations if r[2] == "MENTORED"]
    mentor_sources = {r[0] for r in mentored}
    assert "Hữu Châu" in mentor_sources or "Việt Anh" in mentor_sources
    assert all(r[1] == "Trấn Thành" for r in mentored)

def test_extract_career_relations_negative_mentor_cases():
    # Trường hợp câu văn chứa 'theo học' hoặc 'xét tặng' nhưng đối tượng là Hội đồng, trường học, tác phẩm
    text = (
        "Năm 2015, cô kết hôn. Chồng cô là ca sĩ, từng theo học tại Nhạc viện Thành phố Hồ Chí Minh, "
        "được Hội đồng cấp Nhà nước xét tặng danh hiệu Nghệ sĩ Ưu tú. "
        "Năm 2005, Doãn Hoàng Kiên tốt nghiệp và tiếp tục theo học tại Hà Nội. "
        "Năm 13 tuổi, Kim Tiến theo học trường múa và tham gia nghệ thuật. "
        "Đăng Dương rất nghiêm khắc trong việc đào tạo các học trò của mình."
    )
    known = {
        "Lê Phương", "Doãn Hoàng Kiên", "Kim Tiến", "Đăng Dương",
        "Hội đồng cấp Nhà nước xét tặng danh hiệu “Nghệ sĩ Nhân dân”, “Nghệ sĩ Ưu tú” tại Việt Nam",
        "Đường lên Điện Biên", "Áo trắng sân trường", "Ngày ấy mình đã yêu"
    }
    artworks = {"Đường lên Điện Biên", "Áo trắng sân trường", "Ngày ấy mình đã yêu"}
    orgs = {"Hội đồng cấp Nhà nước xét tặng danh hiệu “Nghệ sĩ Nhân dân”, “Nghệ sĩ Ưu tú” tại Việt Nam"}
    persons = {"Lê Phương", "Doãn Hoàng Kiên", "Kim Tiến", "Đăng Dương"}

    relations = extract_career_relations("Lê Phương", text, known, known_persons=persons, known_artworks=artworks, known_orgs=orgs)
    
    # Tuyệt đối không được tạo quan hệ MENTORED với Hội đồng hoặc các tác phẩm
    for s, t, rel, ev in relations:
        if rel == "MENTORED":
            assert "Hội đồng" not in s
            assert s not in artworks
            assert s not in orgs

def test_extract_career_relations_negative_founded_cases():
    # Trường hợp từ ngữ trùng hợp gây gán sai FOUNDED vào tác phẩm phim
    text = (
        "Hiện nay, Vân Hà cùng chồng kỷ niệm 1 năm thành lập sân khấu vàng. "
        "Thiệu Ánh Dương hiện mở công ty luật tại Hà Nội. "
        "Mỹ Uyên gắn bó với sân khấu và là Giám đốc của sân khấu này."
    )
    known = {
        "Vân Hà", "Thiệu Ánh Dương", "Mỹ Uyên",
        "Bên trong vỏ kén vàng", "Ngoài vòng pháp luật 2", "Xin nhận nơi này làm quê hương"
    }
    artworks = {"Bên trong vỏ kén vàng", "Ngoài vòng pháp luật 2", "Xin nhận nơi này làm quê hương"}
    persons = {"Vân Hà", "Thiệu Ánh Dương", "Mỹ Uyên"}

    relations = extract_career_relations("Vân Hà", text, known, known_persons=persons, known_artworks=artworks)
    
    # Tuyệt đối không được nhận diện tác phẩm phim làm tổ chức sáng lập (FOUNDED)
    founded = [r for r in relations if r[2] == "FOUNDED"]
    for s, t, rel, ev in founded:
        assert t not in artworks
        assert t not in ["Bên trong vỏ kén vàng", "Ngoài vòng pháp luật 2", "Xin nhận nơi này làm quê hương"]

def test_extract_career_relations_negative_affiliated_city_leak():
    # Tránh việc nghệ sĩ sinh sống ở 'Hà Nội' bị liên kết sai vào 'Nhà hát Kịch Hà Nội'
    text = "Năm 1999, ông lên Hà Nội, làm việc tại Hà Nội và tham gia nhiều hoạt động biểu diễn."
    known = {"Quang Thắng", "Nhà hát Kịch Hà Nội"}
    persons = {"Quang Thắng"}
    orgs = {"Nhà hát Kịch Hà Nội"}

    relations = extract_career_relations("Quang Thắng", text, known, known_persons=persons, known_orgs=orgs)
    
    affiliated = [r for r in relations if r[2] == "AFFILIATED_WITH"]
    # Không được tự động liên kết với Nhà hát Kịch Hà Nội chỉ vì câu có từ 'Hà Nội'
    assert len(affiliated) == 0

def test_parse_infobox_field_empty_closing_no_runaway():
    from cinema_extractor import parse_infobox_field
    # Case 1: spouse = \n}}
    wikitext1 = (
        "{{Thông tin nghệ sĩ\n"
        "| tên = Lê Thiện\n"
        "| spouse = \n"
        "}}\n\n"
        "Lê Thiện từng công tác tại [[Nhà hát Cải lương Trần Hữu Trang]].\n"
        "{| class=\"wikitable\"\n"
        "| Cột 1\n"
        "|}"
    )
    assert parse_infobox_field(wikitext1, ["spouse"]) == ""

    # Case 2: spouse = }} on same line
    wikitext2 = (
        "{{Thông tin nghệ sĩ\n"
        "| tên = Nghệ sĩ\n"
        "| spouse = }}\n"
        "Nội dung bài viết [[Liên xô]]."
    )
    assert parse_infobox_field(wikitext2, ["spouse"]) == ""

    # Case 3: empty field before next field
    wikitext3 = (
        "{{Thông tin phim\n"
        "| đạo diễn = \n"
        "| diễn viên = [[Trần Thành]]\n"
        "}}"
    )
    assert parse_infobox_field(wikitext3, ["đạo diễn"]) == ""
    assert parse_infobox_field(wikitext3, ["diễn viên"]) == "[[Trần Thành]]"

def test_clean_sentence_evidence_self_closing_ref_preserved_text():
    dirty = (
        '<ref name=":0" />Anh có cơ hội gặp gỡ và trở thành học trò của [[Công Ninh]]'
        '<ref>{{chú thích web|url=test}}</ref>.'
    )
    cleaned = clean_sentence_evidence(dirty)
    assert "học trò của Công Ninh" in cleaned
    assert "<ref" not in cleaned

def test_parse_infobox_null_and_empty_inputs():
    res_m = parse_movie_infobox(None, None)
    assert res_m["is_movie"] is False
    assert res_m["directors"] == []

    res_p = parse_person_infobox(None, None)
    assert res_p["is_person"] is False
    assert res_p["spouses"] == []

