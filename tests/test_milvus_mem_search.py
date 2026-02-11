import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.milvus_mem_search import MemoryChunk, MilvusMemSearch


class MilvusMemSearchParsingTests(unittest.TestCase):
    def _build_store_without_init(self) -> MilvusMemSearch:
        store = object.__new__(MilvusMemSearch)
        return store

    def test_chunk_id_is_stable(self) -> None:
        chunk = MemoryChunk(
            source_path="memories/daily/2026-02-12.md",
            date="2026-02-12",
            start_line=3,
            end_line=8,
            content="## 10:00 - 记录\n- 用户喜欢橙色主题",
        )
        self.assertEqual(len(chunk.chunk_id), 64)
        self.assertEqual(chunk.chunk_id, chunk.chunk_id)

    def test_split_daily_markdown_by_headers(self) -> None:
        with TemporaryDirectory() as tmp:
            store = self._build_store_without_init()
            path = Path(tmp) / "2026-02-12.md"
            text = (
                "# 2026-02-12\n\n"
                "## 09:10 - 早会\n"
                "- 同步需求\n\n"
                "## 10:30 - 客户反馈\n"
                "- 需要流式输出\n"
            )
            chunks = MilvusMemSearch._split_daily_markdown(store, path, text)

            self.assertEqual(len(chunks), 2)
            self.assertEqual(chunks[0].date, "2026-02-12")
            self.assertTrue(chunks[0].content.startswith("# 2026-02-12"))
            self.assertIn("## 10:30 - 客户反馈", chunks[1].content)

    def test_iter_daily_files_only_matches_date_pattern(self) -> None:
        with TemporaryDirectory() as tmp:
            daily = Path(tmp)
            (daily / "2026-02-10.md").write_text("# ok", encoding="utf-8")
            (daily / "2026-02-09.md").write_text("# ok", encoding="utf-8")
            (daily / "note.md").write_text("# ignore", encoding="utf-8")
            (daily / "2026-2-9.md").write_text("# ignore", encoding="utf-8")

            store = self._build_store_without_init()
            store.memory_daily_dir = daily

            files = MilvusMemSearch._iter_daily_files(store)
            self.assertEqual([p.name for p in files], ["2026-02-09.md", "2026-02-10.md"])


if __name__ == "__main__":
    unittest.main()
