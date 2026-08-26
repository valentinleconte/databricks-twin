"""Tests for the pure logic in scripts/twin/setup_resources.py: chunking the doc
corpus and escaping values for the hand-built SQL INSERT statements. Both run
unattended against real Databricks resources (see NOTES.md) — if the chunker
mis-sizes a chunk or the escaper mishandles a quote, the failure is a corrupted
row in doc_chunks, discovered late and expensively. Cheap to catch here instead.
"""

from __future__ import annotations


class TestChunkText:
    def test_short_text_is_a_single_chunk(self, setup_resources):
        assert setup_resources.chunk_text("hello world", size=1000, overlap=200) == ["hello world"]

    def test_empty_text_produces_no_chunks(self, setup_resources):
        assert setup_resources.chunk_text("", size=1000, overlap=200) == []

    def test_splits_at_the_configured_size(self, setup_resources):
        text = "a" * 2500
        chunks = setup_resources.chunk_text(text, size=1000, overlap=200)
        assert [len(c) for c in chunks[:-1]] == [1000, 1000]
        assert len(chunks[-1]) <= 1000

    def test_consecutive_chunks_overlap_by_the_configured_amount(self, setup_resources):
        text = "".join(str(i % 10) for i in range(2500))  # digits, so overlap is checkable by content
        chunks = setup_resources.chunk_text(text, size=1000, overlap=200)
        assert chunks[0][-200:] == chunks[1][:200]
        assert chunks[1][-200:] == chunks[2][:200]

    def test_exact_chunk_boundaries_on_a_worked_example(self, setup_resources):
        """The real failure mode this guards: an off-by-one in the sliding window
        that silently drops a slice of the source document from every chunk.
        Uses a small, fully worked example rather than searching for chunk
        positions in the text — with size=10/overlap=3 the step is 7, so a
        26-character text should split exactly as: [0:10], [7:17], [14:24], [21:26]."""
        text = "".join(str(i % 10) for i in range(26))
        chunks = setup_resources.chunk_text(text, size=10, overlap=3)
        assert chunks == [text[0:10], text[7:17], text[14:24], text[21:26]]
        # Every character of the source text appears in the reconstruction.
        assert "".join(chunks[i][:7] for i in range(len(chunks) - 1)) + chunks[-1] == text

    def test_the_configured_project_parameters_produce_196_chunks_from_the_real_corpus(
        self, setup_resources
    ):
        """Regression pin: the actual measured chunk count (see NOTES.md, verified
        against SELECT COUNT(*) on the real doc_chunks table). If this changes,
        either the corpus changed or the chunker did — worth noticing either way."""
        import glob
        import os
        import re

        corpus_dir = setup_resources.CORPUS_DIR
        if not glob.glob(os.path.join(corpus_dir, "*.md")):
            import pytest

            pytest.skip("databricks-docs-md/ not present in this checkout")

        total = 0
        for path in glob.glob(os.path.join(corpus_dir, "*.md")):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            body = re.sub(r"^---\n.*?\n---\n\n", "", text, flags=re.DOTALL)
            total += sum(1 for c in setup_resources.chunk_text(body, 1000, 200) if c.strip())
        assert total == 196


class TestSqlEscape:
    def test_single_quote_is_escaped(self, setup_resources):
        assert setup_resources.sql_escape("it's here") == "it\\'s here"

    def test_backslash_is_escaped(self, setup_resources):
        assert setup_resources.sql_escape("a\\b") == "a\\\\b"

    def test_backslash_before_quote_does_not_swallow_the_quote_escape(self, setup_resources):
        """Order matters: escaping the backslash first, then the quote, is the
        only order that doesn't turn `\\'` into an unescaped quote."""
        result = setup_resources.sql_escape("a\\'b")
        assert result == "a\\\\\\'b"

    def test_plain_text_is_unchanged(self, setup_resources):
        assert setup_resources.sql_escape("Vector Search index sync") == "Vector Search index sync"

    def test_escaped_content_is_safe_to_embed_in_a_single_quoted_sql_literal(self, setup_resources):
        """The property that actually matters: wrapped in single quotes, the
        escaped text cannot terminate the literal early."""
        dangerous = "'; DROP TABLE doc_chunks; --"
        literal = f"'{setup_resources.sql_escape(dangerous)}'"
        # A naive quote-count check: every single quote in the literal must be
        # part of an escape sequence, except the two enclosing quotes.
        inner = literal[1:-1]
        assert inner.count("'") == inner.count("\\'")
