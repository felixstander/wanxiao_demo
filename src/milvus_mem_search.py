import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pymilvus import DataType, MilvusClient
from sentence_transformers import SentenceTransformer


@dataclass
class MemoryChunk:
    source_path: str
    date: str
    start_line: int
    end_line: int
    content: str

    @property
    def chunk_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    @property
    def chunk_id(self) -> str:
        base = f"{self.source_path}:{self.start_line}:{self.end_line}:{self.chunk_hash}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()[:64]


class MilvusMemSearch:
    DAILY_FILE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")

    def __init__(
        self,
        memory_daily_dir: Path,
        milvus_db_path: Path,
        collection_name: str = "daily_memory_chunks",
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.memory_daily_dir = memory_daily_dir
        self.milvus_db_path = milvus_db_path
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model

        self.memory_daily_dir.mkdir(parents=True, exist_ok=True)
        self.milvus_db_path.parent.mkdir(parents=True, exist_ok=True)

        self.embedder = SentenceTransformer(self.embedding_model_name)
        dim = self.embedder.get_sentence_embedding_dimension()
        if dim is None:
            raise RuntimeError("embedding dimension is unavailable")
        self.embedding_dim = int(dim)

        self.client = MilvusClient(uri=str(self.milvus_db_path))
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if self.client.has_collection(collection_name=self.collection_name):
            return

        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=False)
        schema.add_field(
            field_name="id",
            datatype=DataType.VARCHAR,
            is_primary=True,
            max_length=64,
        )
        schema.add_field(
            field_name="source_path",
            datatype=DataType.VARCHAR,
            max_length=512,
        )
        schema.add_field(
            field_name="date",
            datatype=DataType.VARCHAR,
            max_length=10,
        )
        schema.add_field(field_name="start_line", datatype=DataType.INT64)
        schema.add_field(field_name="end_line", datatype=DataType.INT64)
        schema.add_field(
            field_name="chunk_hash",
            datatype=DataType.VARCHAR,
            max_length=64,
        )
        schema.add_field(
            field_name="content",
            datatype=DataType.VARCHAR,
            max_length=65535,
        )
        schema.add_field(
            field_name="vector",
            datatype=DataType.FLOAT_VECTOR,
            dim=self.embedding_dim,
        )

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )

    def _iter_daily_files(self) -> list[Path]:
        files = []
        for path in self.memory_daily_dir.glob("*.md"):
            if path.is_file() and self.DAILY_FILE_PATTERN.match(path.name):
                files.append(path)
        files.sort(key=lambda p: p.name)
        return files

    def _split_daily_markdown(self, file_path: Path, text: str) -> list[MemoryChunk]:
        lines = text.split("\n")
        total_lines = len(lines)
        if total_lines == 0:
            return []

        date = file_path.stem
        body_start_idx = 0
        header_context = ""

        for idx, line in enumerate(lines):
            if line.strip().startswith("## "):
                body_start_idx = idx
                header_context = "\n".join(lines[:idx]).strip()
                break
        else:
            content = text.strip()
            if not content:
                return []
            return [
                MemoryChunk(
                    source_path=file_path.as_posix(),
                    date=date,
                    start_line=1,
                    end_line=total_lines,
                    content=content,
                )
            ]

        chunks: list[MemoryChunk] = []
        current_lines: list[str] = []
        current_start = body_start_idx + 1

        for i in range(body_start_idx, total_lines):
            line = lines[i]
            is_header = line.strip().startswith("## ")
            if is_header and current_lines:
                block = (header_context + "\n\n" + "\n".join(current_lines)).strip()
                if block:
                    chunks.append(
                        MemoryChunk(
                            source_path=file_path.as_posix(),
                            date=date,
                            start_line=current_start,
                            end_line=i,
                            content=block,
                        )
                    )
                current_lines = [line]
                current_start = i + 1
            else:
                current_lines.append(line)

        if current_lines:
            block = (header_context + "\n\n" + "\n".join(current_lines)).strip()
            if block:
                chunks.append(
                    MemoryChunk(
                        source_path=file_path.as_posix(),
                        date=date,
                        start_line=current_start,
                        end_line=total_lines,
                        content=block,
                    )
                )

        return chunks

    def _embed(self, texts: Iterable[str]) -> list[list[float]]:
        embeddings = self.embedder.encode(
            list(texts),
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return [vec.tolist() for vec in embeddings]

    @staticmethod
    def _escape_string(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def _delete_by_source_path(self, source_path: str) -> None:
        escaped = self._escape_string(source_path)
        expr = f'source_path == "{escaped}"'
        self.client.delete(collection_name=self.collection_name, filter=expr)

    def index_file(self, file_path: Path) -> int:
        content = file_path.read_text(encoding="utf-8")
        chunks = self._split_daily_markdown(file_path, content)

        self._delete_by_source_path(file_path.as_posix())
        if not chunks:
            return 0

        vectors = self._embed(chunk.content for chunk in chunks)
        rows = []
        for chunk, vector in zip(chunks, vectors):
            rows.append(
                {
                    "id": chunk.chunk_id,
                    "source_path": chunk.source_path,
                    "date": chunk.date,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_hash": chunk.chunk_hash,
                    "content": chunk.content,
                    "vector": vector,
                }
            )

        self.client.insert(collection_name=self.collection_name, data=rows)
        return len(rows)

    def index_all(self) -> dict[str, int]:
        indexed_files = 0
        indexed_chunks = 0

        for file_path in self._iter_daily_files():
            cnt = self.index_file(file_path)
            indexed_files += 1
            indexed_chunks += cnt

        return {"files": indexed_files, "chunks": indexed_chunks}

    def rebuild(self) -> dict[str, int]:
        if self.client.has_collection(collection_name=self.collection_name):
            self.client.drop_collection(collection_name=self.collection_name)
        self._ensure_collection()
        return self.index_all()

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_vector = self._embed([query])[0]
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="vector",
            limit=top_k,
            output_fields=["source_path", "date", "start_line", "end_line", "content"],
            search_params={"metric_type": "COSINE", "params": {}},
        )

        if not results:
            return []

        rows: list[dict] = []
        for hit in results[0]:
            entity = hit.get("entity", {})
            rows.append(
                {
                    "score": float(hit.get("distance", 0.0)),
                    "source_path": entity.get("source_path", ""),
                    "date": entity.get("date", ""),
                    "start_line": int(entity.get("start_line", 0)),
                    "end_line": int(entity.get("end_line", 0)),
                    "content": entity.get("content", ""),
                }
            )
        return rows

    def stats(self) -> dict:
        info = self.client.describe_collection(collection_name=self.collection_name)
        collection_stats = self.client.get_collection_stats(
            collection_name=self.collection_name
        )
        return {
            "collection": self.collection_name,
            "db_path": str(self.milvus_db_path),
            "embedding_model": self.embedding_model_name,
            "embedding_dim": self.embedding_dim,
            "schema": info,
            "stats": collection_stats,
        }


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def build_default_store() -> MilvusMemSearch:
    root = _project_root()
    memory_daily_dir = root / "memories" / "daily"
    milvus_db_path = root / ".memories" / "milvus_memories.db"
    return MilvusMemSearch(
        memory_daily_dir=memory_daily_dir, milvus_db_path=milvus_db_path
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Milvus Lite memory index/search for memories/daily markdown files"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("index", help="Index all daily memory markdown files")
    sub.add_parser(
        "rebuild", help="Drop collection and rebuild from all markdown files"
    )
    sub.add_parser("stats", help="Show collection and index stats")

    search_parser = sub.add_parser("search", help="Search indexed daily memory chunks")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--top-k", type=int, default=5, help="Top K results")

    args = parser.parse_args()
    store = build_default_store()

    if args.command == "index":
        summary = store.index_all()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    if args.command == "rebuild":
        summary = store.rebuild()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    if args.command == "stats":
        print(json.dumps(store.stats(), ensure_ascii=False, indent=2, default=str))
        return

    if args.command == "search":
        rows = store.search(args.query, top_k=args.top_k)
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    raise RuntimeError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
