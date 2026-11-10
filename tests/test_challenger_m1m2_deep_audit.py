"""
tests/test_challenger_m1m2_deep_audit.py
Adversarial and deep stress test suite for Milestone 1 & 2 gating.
Tests:
- parse_infobox_field edge cases: heavily nested templates, multiline comments,
  unclosed braces, fake pipes in comments, unicode spaces, massive wikitext inputs.
- Cypher sanitization in data/import_neo4j.cypher: semicolon termination, single quote escaping,
  template stripping, newline absence, valid statement structure.
- Depth-aware parser empirical verification.
"""

import os
import re
import pytest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import cinema_extractor as ce
import cinema_models as cm

class TestInfoboxFieldAdversarialDeep:
    """Stress testing parse_infobox_field with extreme and adversarial inputs."""

    def test_heavily_nested_templates_5_levels(self):
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Test Deep Nesting\n"
            "| đạo diễn = {{a|{{b|{{c|{{d|{{e|[[Đạo Diễn Lồng Sâu]]}}}}}}}}}}\n"
            "| diễn viên = [[Diễn Viên 1]]\n"
            "}}"
        )
        val = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        assert "[[Đạo Diễn Lồng Sâu]]" in val
        assert val.startswith("{{a|{{b|{{c|{{d|{{e|")
        # Ensure it didn't leak into diễn viên
        assert "Diễn Viên 1" not in val
        actors = ce.parse_infobox_field(wikitext, ["diễn viên"])
        assert "[[Diễn Viên 1]]" in actors

    def test_multiline_html_comment_spanning_lines(self):
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Test Comment\n"
            "| đạo diễn = <!--\n"
            "đây là chú thích nhiều dòng\n"
            "--> [[Nguyễn Văn A]]\n"
            "| diễn viên = [[Trần Văn B]]\n"
            "}}"
        )
        val = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        assert "[[Nguyễn Văn A]]" in val
        assert "Trần Văn B" not in val

    def test_fake_pipe_inside_multiline_comment_boundary_behavior(self):
        """
        Adversarial test: An HTML comment containing a line-initial pipe '| field = '.
        Empirical finding: Because parse_infobox_field tracks '{{' brace depth but does not
        track HTML comment boundaries (<!-- ... -->), a line break followed by '| field = '
        at depth 0 triggers the field termination lookahead, truncating the capture at the fake pipe.
        """
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Test Fake Pipe\n"
            "| đạo diễn = <!--\n"
            "| diễn viên = FAKE_LEAK\n"
            "--> [[Nguyễn Văn Thật]]\n"
            "| diễn viên = [[Trần Văn B]]\n"
            "}}"
        )
        val = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        # The parser terminates at '\n| diễn viên =', returning '<!--'
        assert val == "<!--"

    def test_field_spacing_tabs_and_spaces(self):
        """Standard ASCII spaces and tabs around field and equals sign are handled cleanly."""
        wikitext = (
            "{{Thông tin phim\n"
            "|\t  đạo diễn\t  =\t  [[Đặng Nhật Minh]]\n"
            "| diễn viên = [[Bùi Cường]]\n"
            "}}"
        )
        val = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        assert "[[Đặng Nhật Minh]]" in val

    def test_unicode_non_breaking_space_caveat(self):
        """
        Adversarial edge case: Non-breaking space (\\u00a0) around field pipes.
        Empirical observation: [ \\t]* strictly matches ASCII space/tab.
        Non-breaking spaces in wikitext are not matched as delimiters.
        """
        wikitext = (
            "{{Thông tin phim\n"
            "|\u00a0đạo diễn\u00a0=\u00a0[[Đặng Nhật Minh]]\n"
            "| diễn viên = [[Bùi Cường]]\n"
            "}}"
        )
        val = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        # Documents that \u00a0 is not matched by [ \t]
        assert val == ""

    def test_unclosed_braces_in_field(self):
        """
        Adversarial test: Field contains unclosed '{{ubl|[[A]]|[[B]]' without closing '}}'.
        Depth never returns to 0. Parser should consume gracefully without infinite loop or crash.
        """
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Broken Template\n"
            "| đạo diễn = {{ubl|[[Trần Anh Hùng]]\n"
            "| diễn viên = [[Lương Triều Vỹ]]\n"
            "}}"
        )
        val = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        # Must not raise an exception, returns captured string
        assert isinstance(val, str)
        assert "Trần Anh Hùng" in val

    def test_empty_field_with_whitespace_and_tabs(self):
        wikitext = (
            "{{Thông tin phim\n"
            "| đạo diễn = \t  \t  \n"
            "| diễn viên = [[Ninh Dương Lan Ngọc]]\n"
            "}}"
        )
        val = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        assert val == ""

    def test_field_with_internal_table_markup(self):
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Phim Có Bảng\n"
            "| nội dung = {| class=\"wikitable\"\n"
            "|- \n"
            "| Cột 1 || Cột 2\n"
            "|}\n"
            "| đạo diễn = [[Ngô Thanh Vân]]\n"
            "}}"
        )
        val = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        assert "[[Ngô Thanh Vân]]" in val

    def test_massive_input_performance_no_re_catastrophe(self):
        """Ensure parse_infobox_field scales linearly with large wikitext (> 100 KB)."""
        import time
        filler = "| ghi chú = " + ("nội dung dài " * 5000) + "\n"
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Siêu Phim\n"
            + filler +
            "| đạo diễn = [[Victor Vũ]]\n"
            + filler +
            "}}"
        )
        t0 = time.time()
        val = ce.parse_infobox_field(wikitext, ["đạo diễn"])
        elapsed = time.time() - t0
        assert elapsed < 0.5, f"Execution took too long: {elapsed:.3f}s"
        assert "[[Victor Vũ]]" in val


class TestDepthAwareParserEmpirical:
    """Empirical verification of the specific Iteration 2 bug on multiline templates."""

    def test_multiline_ubl_preserves_all_items(self):
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Làng Vũ Đại ngày ấy\n"
            "| đạo diễn = [[Phạm Văn Khoa]]\n"
            "| diễn viên = {{ubl\n"
            "|[[Bùi Cường]]\n"
            "|[[Đức Lưu]]\n"
            "|[[Hữu Mười]]\n"
            "|[[Kim Lân]]\n"
            "}}\n"
            "| năm = 1982\n"
            "}}"
        )
        val = ce.parse_infobox_field(wikitext, ["diễn viên"])
        assert "Bùi Cường" in val
        assert "Đức Lưu" in val
        assert "Hữu Mười" in val
        assert "Kim Lân" in val

        res = ce.parse_movie_infobox("Làng Vũ Đại ngày ấy", wikitext)
        assert res["is_movie"] is True
        assert set(res["actors"]) == {"Bùi Cường", "Đức Lưu", "Hữu Mười", "Kim Lân"}

    def test_multiline_template_with_empty_parameters(self):
        wikitext = (
            "{{Thông tin phim\n"
            "| tên = Test Template Empty Params\n"
            "| diễn viên = {{ubl\n"
            "|\n"
            "|[[Diễn Viên A]]\n"
            "|\n"
            "|[[Diễn Viên B]]\n"
            "}}\n"
            "| năm = 2020\n"
            "}}"
        )
        res = ce.parse_movie_infobox("Test", wikitext)
        assert "Diễn Viên A" in res["actors"]
        assert "Diễn Viên B" in res["actors"]


class TestCypherSanitizationProductionFile:
    """Direct empirical audit on data/import_neo4j.cypher."""

    @pytest.fixture(scope="class")
    def cypher_lines(self):
        cypher_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "import_neo4j.cypher"))
        assert os.path.exists(cypher_path), f"File {cypher_path} does not exist!"
        with open(cypher_path, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines

    def test_file_not_empty_and_sufficient_lines(self, cypher_lines):
        assert len(cypher_lines) >= 20000, f"Expected >= 20000 lines, got {len(cypher_lines)}"

    def test_all_executable_statements_end_with_semicolon(self, cypher_lines):
        bad_lines = []
        for idx, line in enumerate(cypher_lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            if not stripped.endswith(";"):
                bad_lines.append((idx, stripped[:100]))
        assert len(bad_lines) == 0, f"Found {len(bad_lines)} statements not ending with semicolon: {bad_lines[:5]}"

    def test_zero_raw_unparsed_templates(self, cypher_lines):
        raw_templates = []
        for idx, line in enumerate(cypher_lines, 1):
            if line.strip().startswith("//"):
                continue
            if "{{" in line or "}}" in line:
                # Except Cypher map literal like {id: '...'}
                # Cypher maps use single braces { ... }, Wikitext templates use double {{ ... }}
                raw_templates.append((idx, line.strip()[:100]))
        assert len(raw_templates) == 0, f"Found raw wikitext templates in Cypher: {raw_templates[:5]}"

    def test_zero_embedded_newlines_within_statements(self, cypher_lines):
        bad_newlines = []
        for idx, line in enumerate(cypher_lines, 1):
            # Each line in cypher_lines should only have trailing \n or \r\n
            content = line.rstrip("\r\n")
            if "\r" in content or "\n" in content:
                bad_newlines.append((idx, repr(content[:50])))
        assert len(bad_newlines) == 0, f"Found statements with internal newlines: {bad_newlines[:5]}"

    def test_single_quote_parity_and_escaping(self, cypher_lines):
        """
        Verify that all single quotes in Cypher statements are syntactically balanced.
        Replacing escaped backslashes (\\\\) and escaped quotes (\\') should leave an even number of quotes.
        """
        unbalanced = []
        for idx, line in enumerate(cypher_lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            # Remove double backslashes first, then escaped single quotes
            clean = stripped.replace("\\\\", "")
            clean = clean.replace("\\'", "")
            quote_count = clean.count("'")
            if quote_count % 2 != 0:
                unbalanced.append((idx, quote_count, stripped[:120]))
        assert len(unbalanced) == 0, f"Found {len(unbalanced)} statements with unbalanced single quotes: {unbalanced[:5]}"

    def test_statement_grammar_prefixes(self, cypher_lines):
        """Every executable statement should start with CREATE CONSTRAINT, MERGE, or MATCH."""
        valid_prefixes = ("CREATE CONSTRAINT", "MERGE", "MATCH")
        invalid_statements = []
        for idx, line in enumerate(cypher_lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            if not any(stripped.startswith(p) for p in valid_prefixes):
                invalid_statements.append((idx, stripped[:80]))
        assert len(invalid_statements) == 0, f"Found invalid statements: {invalid_statements[:5]}"

    def test_unique_constraints_present(self, cypher_lines):
        text = "".join(cypher_lines)
        assert "CREATE CONSTRAINT unique_person_id" in text
        assert "CREATE CONSTRAINT unique_artwork_id" in text
        assert "CREATE CONSTRAINT unique_organization_id" in text
