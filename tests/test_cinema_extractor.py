import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from cinema_extractor import (
    extract_wiki_links,
    parse_movie_infobox,
    parse_person_infobox,
    extract_career_relations
)

def test_extract_wiki_links():
    text = "* [[Trấn Thành]]\n* [[Tuấn Trần]]\n* [[Lê Giang (nghệ sĩ)|Lê Giang]]\n* [[Tập tin:Pic.jpg]]"
    links = extract_wiki_links(text)
    assert "Trấn Thành" in links
    assert "Tuấn Trần" in links
    assert "Lê Giang (nghệ sĩ)" in links
    assert "Tập tin:Pic.jpg" not in links

def test_parse_movie_infobox():
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

def test_parse_person_infobox():
    wikitext = """
{{Thông tin nhân vật
| tên = Victor Vũ
| công việc = [[Nhà làm phim]]|[[Đạo diễn]]
| spouse = {{marriage|[[Đinh Ngọc Diệp]]|2016}}
| nơi công tác = [[Hãng phim Chánh Phương]]
}}
"""
    result = parse_person_infobox("Victor Vũ", wikitext)
    assert result["is_person"] is True
    assert "Đinh Ngọc Diệp" in result["spouses"]
    assert "Hãng phim Chánh Phương" in result["affiliations"]
    assert "Đạo diễn" in result["roles"] or "Nhà làm phim" in result["roles"]

def test_extract_career_relations():
    text = (
        "Trấn Thành được nghệ sĩ Hữu Châu và NSND Việt Anh nâng đỡ nhiệt tình trong những ngày đầu bước vào nghề sân khấu. "
        "Anh từng đóng cặp ăn ý cùng Ninh Dương Lan Ngọc trong bộ phim Cua lại vợ bầu. "
        "Ngoài ra, Ngô Thanh Vân đã sáng lập Studio68 để sản xuất nhiều bộ phim chiếu rạp."
    )
    known = {"Hữu Châu", "Việt Anh", "Trấn Thành", "Ninh Dương Lan Ngọc", "Ngô Thanh Vân", "Studio68"}
    relations = extract_career_relations("Trấn Thành", text, known)

    # relations: list of (source, target, rel_type, evidence)
    types_found = {r[2] for r in relations}
    assert "MENTORED" in types_found or "CO_STARRED" in types_found
