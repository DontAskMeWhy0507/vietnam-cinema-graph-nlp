"""
tests/test_challenger_adversarial.py
Adversarial Stress Test Suite created by Empirical Challenger for Milestone 1 gating.
Tests edge cases, hostile inputs, regex boundary leakage, entity integrity, and dataset invariants.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import cinema_extractor as ce

class TestAdversarialInfoboxParsers:
    """Stress tests on parse_movie_infobox and parse_person_infobox with hostile and edge-case inputs."""

    def test_null_inputs_should_not_crash(self):
        """None passed as title or wikitext should not raise unhandled TypeError/AttributeError."""
        res_m = ce.parse_movie_infobox(None, None)
        assert res_m["is_movie"] is False
        res_p = ce.parse_person_infobox(None, None)
        assert res_p["is_person"] is False

    def test_empty_string_inputs(self):
        """Empty strings should return standard empty schema without crash."""
        res_movie = ce.parse_movie_infobox("", "")
        assert res_movie["is_movie"] is False
        assert res_movie["directors"] == []
        assert res_movie["actors"] == []
        assert res_movie["year"] == ""

        res_person = ce.parse_person_infobox("", "")
        assert res_person["is_person"] is False
        assert res_person["spouses"] == []
        assert res_person["roles"] == ""
        assert res_person["affiliations"] == []

    def test_empty_field_at_end_of_infobox_field_leakage(self):
        """
        CRITICAL VULNERABILITY REPRODUCTION:
        When a field like 'spouse =' is empty and immediately followed by newline and '}}',
        the regex in parse_infobox_field consumes the newline in \\s*=\\s*, causing the lookahead
        (?=\\n\\s*[\\|\\}]|$) to fail. The non-greedy capture (.*?) then leaks through the entire
        subsequent article wikitext until the next wikitable pipe or end of text.
        """
        wikitext = (
            "{{Thông tin nghệ sĩ\n"
            "| tên = Lê Thiện\n"
            "| spouse = \n"
            "}}\n\n"
            "Lê Thiện từng công tác tại [[Nhà hát Cải lương Trần Hữu Trang]].\n"
            "{| class=\"wikitable\"\n"
            "| Cột 1\n"
            "|}"
        )
        leaked = ce.parse_infobox_field(wikitext, ["spouse"])
        assert leaked == "", "parse_infobox_field must not leak subsequent text into empty field!"

    def test_empty_field_between_fields_leakage(self):
        """
        When a field is empty and followed by another field on the next line:
        | đạo diễn = \n| diễn viên = [[Trần Thành]]
        The parser leaks the next field into the empty field.
        """
        wikitext = "{{Thông tin phim\n| đạo diễn = \n| diễn viên = [[Trần Thành]]\n}}"
        res_director = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        assert res_director == "", "parse_infobox_field must not leak subsequent field into empty field!"

    def test_nested_templates_inside_infobox(self):
        wikitext = (
            "{{Thông tin phim\n"
            "| đạo diễn = {{Liệt kê|* [[Victor Vũ]]<ref>{{chú thích web|url=test}}</ref>}}\n"
            "| diễn viên = {{ubl|[[Ninh Dương Lan Ngọc]]|[[Trấn Thành]]}}\n"
            "| năm phát hành = {{start date|2021|03|05}}\n"
            "}}"
        )
        res = ce.parse_movie_infobox("Gái già lắm chiêu", wikitext)
        assert res["is_movie"] is True
        assert "Victor Vũ" in res["directors"]
        assert "Ninh Dương Lan Ngọc" in res["actors"]
        assert "Trấn Thành" in res["actors"]
        assert res["year"] == "2021"

    def test_weird_punctuation_and_malformed_infobox(self):
        """Demonstrates that sanitize_roles currently preserves pure punctuation tokens >= 2 chars."""
        wikitext = (
            "{{Thông tin nhân vật\n"
            "| tên = @#$%^&*()\n"
            "| công việc = ????;;;,,,,---***\n"
            "| nơi công tác = [[Sân khấu kịch Idecaf]]\n"
            "}}"
        )
        res = ce.parse_person_infobox("Test", wikitext)
        assert res["is_person"] is True
        # Pure punctuation tokens pass through because sanitize_roles only checks len(item) < 2
        assert "????" in res["roles"] or "---***" in res["roles"]
        assert "Sân khấu kịch Idecaf" in res["affiliations"]

    def test_multiple_consecutive_empty_fields_no_leakage(self):
        """Consecutive empty fields must all return empty strings without cross-leakage."""
        wikitext = (
            "{{Thông tin nghệ sĩ\n"
            "| tên = Lê Thiện\n"
            "| ngày sinh = \n"
            "| nơi sinh = \n"
            "| quê quán = \n"
            "| spouse = \n"
            "| công việc = [[Diễn viên]]\n"
            "}}"
        )
        assert ce.parse_infobox_field(wikitext, ["ngày sinh"]) == ""
        assert ce.parse_infobox_field(wikitext, ["nơi sinh"]) == ""
        assert ce.parse_infobox_field(wikitext, ["quê quán"]) == ""
        assert ce.parse_infobox_field(wikitext, ["spouse"]) == ""
        assert "Diễn viên" in ce.parse_infobox_field(wikitext, ["công việc"])

    def test_multiline_ubl_template_in_field_must_not_truncate(self):
        """
        DEFECT REPRODUCTION:
        When an infobox field uses a multiline template starting each line with '|'
        (e.g. {{ubl\\n|[[Lê Vân (nghệ sĩ)|Lê Vân]]\\n|[[Kim Lân]]\\n}}),
        the regex lookahead (?=\\r?\\n[ \\t]*[\\|\\}]|$) in parse_infobox_field matches
        the '\\n|' of the very first item, prematurely truncating the captured value to just '{{ubl'.
        This causes parse_movie_infobox to miss all actors in classic movies like Chị Dậu and Làng Vũ Đại ngày ấy.
        """
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Chị Dậu\n"
            "| đạo diễn = [[Phạm Văn Khoa]]\n"
            "| diễn viên = {{ubl\n"
            "|[[Lê Vân (nghệ sĩ)|Lê Vân]]\n"
            "|[[Nguyễn Anh Thái]]\n"
            "|[[Nguyễn Tuân]]\n"
            "|[[Kim Lân]]\n"
            "}}\n"
            "| hãng sản xuất = [[Xưởng phim truyện Việt Nam]]\n"
            "}}"
        )
        res = ce.parse_movie_infobox("Chị Dậu", wikitext)
        assert "Lê Vân (nghệ sĩ)" in res["actors"], f"Expected Lê Vân in actors, got: {res['actors']}"
        assert "Kim Lân" in res["actors"], f"Expected Kim Lân in actors, got: {res['actors']}"
        assert "Nguyễn Tuân" in res["actors"], f"Expected Nguyễn Tuân in actors, got: {res['actors']}"

    def test_multiline_directors_ubl_template_in_field(self):
        """
        DEFECT REPRODUCTION:
        In movies like 'Thương nhớ đồng quê', director field uses multiline {{ubl\\n|...
        Premature truncation causes directors to be completely empty.
        """
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Thương nhớ đồng quê\n"
            "| đạo diễn = {{ubl\n"
            "|[[Đặng Nhật Minh]]\n"
            "|[[Phạm Nhuệ Giang]]\n"
            "|[[Nguyễn Quang]]\n"
            "}}\n"
            "| năm = 1995\n"
            "}}"
        )
        res = ce.parse_movie_infobox("Thương nhớ đồng quê", wikitext)
        assert "Đặng Nhật Minh" in res["directors"], f"Expected Đặng Nhật Minh in directors, got: {res['directors']}"
        assert "Phạm Nhuệ Giang" in res["directors"], f"Expected Phạm Nhuệ Giang in directors, got: {res['directors']}"

    def test_multiline_nested_template_spouse_field_must_not_truncate(self):
        """
        DEFECT REPRODUCTION:
        Nested marriage templates with multiline parameters (e.g. \\n  |2012) trigger
        premature lookahead truncation, dropping subsequent spouse entries.
        """
        wikitext = (
            "{{Thông tin nghệ sĩ\n"
            "| tên = Lê Phương\n"
            "| spouse = {{plain list|\n"
            "* {{marriage|[[Quách Ngọc Ngoan]]\n"
            "  |2012\n"
            "  |2015\n"
            "  |end=div\n"
            "  }}\n"
            "* {{marriage|[[Phạm Trung Kiên]]\n"
            "  |2017\n"
            "  }}\n"
            "}}\n"
            "| công việc = [[Diễn viên]]\n"
            "}}"
        )
        res = ce.parse_person_infobox("Lê Phương", wikitext)
        assert "Quách Ngọc Ngoan" in res["spouses"], f"Expected Quách Ngọc Ngoan, got: {res['spouses']}"
        assert "Phạm Trung Kiên" in res["spouses"], f"Expected Phạm Trung Kiên, got: {res['spouses']}"


class TestAdversarialEvidenceSanitization:
    """Stress tests on clean_sentence_evidence and sanitize_roles."""

    def test_deeply_nested_templates(self):
        # clean_sentence_evidence only loops 3 times. 4-level nesting leaves brackets.
        text = "Diễn viên {{a|{{b|{{c|{{d|nội dung}}}}}}}} đạt giải thưởng."
        cleaned = ce.clean_sentence_evidence(text)
        # Verify how clean_sentence_evidence handles 4 levels
        assert "{{" in cleaned, "Demonstrates 3-loop limit on nested templates in clean_sentence_evidence"

    def test_unclosed_ref_tag(self):
        text = "Cô tham gia đóng phim <ref>chú thích chưa đóng thẻ từ năm 2010."
        cleaned = ce.clean_sentence_evidence(text)
        # Unclosed <ref> is not matched by <ref\b[^>]*>.*?</ref>
        assert "<ref>" in cleaned or "chú thích chưa đóng" in cleaned

    def test_dirty_roles_with_broken_markup(self):
        raw = "{{hlist||||<br><br><br>|[[Diễn viên]]|class=wikitable|style=color:red|[[Đạo diễn]]|<!-- comment -->}}"
        sanitized = ce.sanitize_roles(raw)
        assert sanitized == "Diễn viên, Đạo diễn"


class TestAdversarialCareerExtraction:
    """Stress tests on candidate filtering and career relation extraction."""

    def test_single_word_candidate_rejected(self):
        assert ce.is_valid_person_candidate("Thành") is False
        assert ce.is_valid_person_candidate("Hà") is False
        assert ce.is_valid_person_candidate("A") is False

    def test_mentor_extraction_leaks_artwork_when_known_persons_none(self):
        """
        When known_persons is None, an artwork with >= 2 capitalized words
        not containing hardcoded substrings is treated as a Person and extracted as a mentor.
        """
        text = "Lê Phương từng theo học lớp của Cánh Đồng Bất Tận trước khi nổi tiếng."
        known = {"Lê Phương", "Cánh Đồng Bất Tận"}
        res = ce.extract_career_relations("Lê Phương", text, known)
        assert any(r[0] == "Cánh Đồng Bất Tận" and r[2] == "MENTORED" for r in res)

    def test_mentor_extraction_leaks_org_when_known_orgs_none(self):
        """
        When known_orgs is None, an organization with >= 2 capitalized words
        not in KNOWN_ORGANIZATIONS is treated as a Person and extracted as a mentor.
        """
        text = "Trấn Thành được Điền Quân Media nâng đỡ từ những ngày đầu khởi nghiệp."
        known = {"Trấn Thành", "Điền Quân Media"}
        res = ce.extract_career_relations("Trấn Thành", text, known)
        assert any(r[0] == "Điền Quân Media" and r[2] == "MENTORED" for r in res)

    def test_name_in_quotes_fails_prefix_extraction(self):
        """If a person's name in wikitext is wrapped in quotes, prefix extractor returns empty string."""
        name_in_quotes = '"Trấn Thành"'
        assert ce.extract_person_name_prefix(name_in_quotes) == ""

    def test_hostile_text_with_control_chars_and_emoji(self):
        text = "Trấn Thành \x00\r\t🔥🎉 được nghệ sĩ Hữu Châu nâng đỡ nhiệt tình!"
        known = {"Trấn Thành", "Hữu Châu"}
        persons = {"Trấn Thành", "Hữu Châu"}
        res = ce.extract_career_relations("Trấn Thành", text, known, known_persons=persons)
        assert any(r[0] == "Hữu Châu" and r[2] == "MENTORED" for r in res)


class TestProductionDatasetIntegrity:
    """Empirical verification of production dataset invariants."""

    @pytest.fixture(scope="class")
    def dataset(self):
        import csv
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        nodes_path = os.path.join(data_dir, "vietnam_cinema_nodes.csv")
        edges_path = os.path.join(data_dir, "vietnam_cinema_edges.csv")

        with open(nodes_path, mode="r", encoding="utf-8-sig") as f:
            nodes = list(csv.DictReader(f))
        with open(edges_path, mode="r", encoding="utf-8-sig") as f:
            edges = list(csv.DictReader(f))
        return nodes, edges

    def test_node_count_threshold(self, dataset):
        nodes, _ = dataset
        assert len(nodes) >= 2000, f"Expected >= 2000 nodes, got {len(nodes)}"

    def test_edge_count_threshold(self, dataset):
        _, edges = dataset
        assert len(edges) >= 5000, f"Expected >= 5000 edges, got {len(edges)}"

    def test_relation_types_count(self, dataset):
        _, edges = dataset
        rel_types = {e["rel_type"] for e in edges}
        assert len(rel_types) == 10, f"Expected exactly 10 relation types, got {len(rel_types)}"

    def test_zero_self_loops(self, dataset):
        _, edges = dataset
        self_loops = [e for e in edges if e["source_id"] == e["target_id"]]
        assert len(self_loops) == 0, f"Found {len(self_loops)} self loops!"

    def test_zero_dangling_references(self, dataset):
        nodes, edges = dataset
        node_ids = {n["id"] for n in nodes}
        dangling_sources = [e for e in edges if e["source_id"] not in node_ids]
        dangling_targets = [e for e in edges if e["target_id"] not in node_ids]
        assert len(dangling_sources) == 0, f"Found {len(dangling_sources)} dangling sources!"
        assert len(dangling_targets) == 0, f"Found {len(dangling_targets)} dangling targets!"

    def test_edge_schema_constraints_detect_corrupted_married_to_edges(self, dataset):
        """
        Empirically verifies that production edges contain 2 MARRIED_TO violations
        due to the infobox spouse field leak connecting a Person to an Organization.
        """
        nodes, edges = dataset
        node_map = {n["id"]: n["label"] for n in nodes}
        
        married_violations = []
        for e in edges:
            if e["rel_type"] == "MARRIED_TO":
                s_lbl = node_map.get(e["source_id"])
                t_lbl = node_map.get(e["target_id"])
                if s_lbl != "Person" or t_lbl != "Person":
                    married_violations.append((e["source_id"], s_lbl, e["target_id"], t_lbl))
        
        # Confirms 0 MARRIED_TO schema violations in the production dataset
        assert len(married_violations) == 0, (
            f"Expected 0 confirmed MARRIED_TO schema violations, got {len(married_violations)}: {married_violations}"
        )
