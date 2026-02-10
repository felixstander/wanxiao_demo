import hashlib
import os
import sqlite3
import struct
from pathlib import Path
from typing import Dict, List

import sqlite_vec
from dotenv import load_dotenv
from openai import OpenAI

# 1. 获取当前脚本所在的目录 (src)
current_dir = Path(__file__).resolve().parent
# 2. 获取上一级目录 (项目根目录)
parent_dir = current_dir.parent
# 3. 定义目标文件夹路径
target_memory_folder = parent_dir / ".memories"
target_memory_folder.mkdir(parents=True, exist_ok=True)

load_dotenv()

# === 配置 ===
DB_PATH = target_memory_folder / "wanxiao_memory_chunked.db"
API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = "qwen/qwen3-embedding-8b"  # 假设 OpenRouter 支持此 Embedding 模型
EMBEDDING_DIM = 4096  # ⚠️ 需根据实际模型确认

# === 分块配置 (模拟 400 token / 80 overlap) ===
# 假设平均一行 10-15 token，我们设定：
CHUNK_SIZE_LINES = 15  # 约 300-450 token
OVERLAP_LINES = 3  # 约 50-80 token

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={"HTTP-Referer": "https://localhost", "X-Title": "LocalAgent"},
)


class MemoryStore:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self._init_schema()

    def _init_schema(self):
        cursor = self.conn.cursor()

        # 1. 基础信息表 (增加了 start_line, end_line)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                content TEXT NOT NULL,
                chunk_hash TEXT NOT NULL,
                created_at INTEGER DEFAULT (unixepoch())
            );
        """
        )
        # 为 file_path 建索引，方便删除旧数据
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_filepath ON chunks(file_path);")

        # 2. 向量表
        cursor.execute(
            f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                embedding float[{EMBEDDING_DIM}]
            );
        """
        )

        # 3. 全文搜索表(FTS5)
        cursor.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                content,
                tokenize='porter'
            );
        """
        )

        # 4. 缓存表
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS embedding_cache (
                hash TEXT PRIMARY KEY,
                embedding BLOB
            );
        """
        )
        self.conn.commit()

    def _calculate_hash(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def _get_embedding(self, text: str, text_hash: str) -> List[float]:
        """获取向量 (Cache -> OpenRouter API)"""
        cursor = self.conn.cursor()

        # A. 查缓存
        cursor.execute(
            "SELECT embedding FROM embedding_cache WHERE hash = ?", (text_hash,)
        )
        row = cursor.fetchone()
        if row:
            return list(struct.unpack(f"{EMBEDDING_DIM}f", row[0]))

        # B. 调 API
        try:
            print(f"📡 Calling OpenRouter for embedding...")
            resp = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text,
                encoding_format="float",
            )
            vector = resp.data[0].embedding

            # 维度检查 (防止模型返回 1024 维但我们表是 1536 维)
            if len(vector) != EMBEDDING_DIM:
                raise ValueError(
                    f"维度不匹配! 模型返回 {len(vector)}, 数据库定义 {EMBEDDING_DIM}"
                )

            # 存缓存
            vec_blob = struct.pack(f"{EMBEDDING_DIM}f", *vector)
            cursor.execute(
                "INSERT OR REPLACE INTO embedding_cache (hash, embedding) VALUES (?, ?)",
                (text_hash, vec_blob),
            )
            self.conn.commit()

            return vector
        except Exception as e:
            print(f"❌ OpenRouter API Error: {e}")
            # 返回零向量防止程序崩溃，但在生产中应该抛出异常或重试
            return [0.0] * EMBEDDING_DIM

    def _split_text_sliding_window(self, text: str) -> List[Dict]:
        """
        语义分块：根据 '## ' 标记进行切分。
        特性：会自动将文件头部的日期（第一个 ## 之前的内容）拼接到每个块中，
        确保每个块都有日期上下文。
        """
        lines = text.split("\n")
        total_lines = len(lines)
        chunks = []

        if total_lines == 0:
            return []

        # === 步骤 1: 提取全局上下文 (Global Context) ===
        # 通常是文件的第一行，例如 "# 2026-02-10"
        # 我们把第一个 "## " 出现之前的所有内容都视为 Context
        header_context = ""
        body_start_index = 0

        for i, line in enumerate(lines):
            if line.strip().startswith("## "):
                header_context = "\n".join(lines[:i]).strip()
                body_start_index = i
                break
        else:
            # 如果整个文件没有 "## "，则把全文当作一个块
            return [{"content": text, "start": 1, "end": total_lines}]

        # === 步骤 2: 基于 ## 遍历切分 ===
        current_chunk_lines = []
        # 记录当前块在原始文件中的起始行号 (1-based)
        current_chunk_start = body_start_index + 1

        for i in range(body_start_index, total_lines):
            line = lines[i]
            is_header = line.strip().startswith("## ")

            # 如果遇到了新的 Header，且当前缓存里已有内容，说明上一块结束了
            if is_header and current_chunk_lines:
                # A. 组装上一块的内容
                # 格式: [日期头] + [换行] + [事件内容]
                chunk_text = (
                    header_context + "\n\n" + "\n".join(current_chunk_lines)
                ).strip()

                chunks.append(
                    {
                        "content": chunk_text,
                        "start": current_chunk_start,
                        "end": i,  # 上一块结束于当前行之前 (i 是 0-based，但在行号逻辑里正好代表上一行的结束)
                    }
                )

                # B. 重置，开始新的一块
                current_chunk_lines = [line]  # 把当前的 Header (## 10:00 AM...) 放进去
                current_chunk_start = i + 1  # 记录新块的起始行号
            else:
                # 否则只是普通内容，加入当前块
                current_chunk_lines.append(line)

        # === 步骤 3: 处理最后一块 ===
        if current_chunk_lines:
            chunk_text = (
                header_context + "\n\n" + "\n".join(current_chunk_lines)
            ).strip()
            chunks.append(
                {
                    "content": chunk_text,
                    "start": current_chunk_start,
                    "end": total_lines,
                }
            )

        return chunks

    def process_file(self, file_path: str, full_content: str):
        """
        处理整个文件：清理旧记录 -> 切分 -> 向量化 -> 存储
        """
        print(f"Processing file: {file_path} ...")
        cursor = self.conn.cursor()

        # 1. 事务开始：先删除该文件之前的所有记录 (防止文件变短后残留旧块)
        # 注意：sqlite-vec 和 fts5 需要根据 rowid 删除，这里简化处理，
        # 实际生产中可能需要先查出旧的 id 列表再删除 vec/fts 表对应行。
        # 但为了演示简单，我们假设 id 是自增且不复用的，或者我们接受一定的孤儿数据（定期清理）。

        # 更严谨的做法是：
        cursor.execute("SELECT id FROM chunks WHERE file_path = ?", (file_path,))
        old_ids = [row[0] for row in cursor.fetchall()]

        if old_ids:
            # 批量删除 Vector 表
            for oid in old_ids:
                cursor.execute("DELETE FROM chunks_vec WHERE id = ?", (oid,))
                # FTS 删除稍微麻烦点，通常 FTS 不需要显式删，或者通过 trigger 维护
                # 这里我们简单地只在主表中维护关系

            # 删除主表
            cursor.execute("DELETE FROM chunks WHERE file_path = ?", (file_path,))

        # 2. 切分文件
        chunks = self._split_text_sliding_window(full_content)
        print(f"  - Split into {len(chunks)} chunks.")

        # 3. 逐个写入
        for chunk in chunks:
            content = chunk["content"]
            if not content.strip():
                continue  # 跳过空块

            chunk_hash = self._calculate_hash(content)
            vector = self._get_embedding(content, chunk_hash)

            # A. 写入主表 chunks
            cursor.execute(
                """
                INSERT INTO chunks (file_path, start_line, end_line, content, chunk_hash)
                VALUES (?, ?, ?, ?, ?)
            """,
                (file_path, chunk["start"], chunk["end"], content, chunk_hash),
            )
            row_id = cursor.lastrowid

            # B. 写入 FTS
            cursor.execute(
                "INSERT INTO chunks_fts (rowid, content) VALUES (?, ?)",
                (row_id, content),
            )

            # C. 写入 Vector
            vec_blob = struct.pack(f"{EMBEDDING_DIM}f", *vector)
            cursor.execute(
                "INSERT INTO chunks_vec (id, embedding) VALUES (?, ?)",
                (row_id, vec_blob),
            )

        self.conn.commit()
        print(f"✅ {file_path} indexed successfully.")

    def search(self, query: str, limit: int = 5, alpha: float = 0.7):
        """混合检索逻辑 (保持不变)"""
        query_hash = self._calculate_hash(query)
        query_vec = self._get_embedding(query, query_hash)

        if all(v == 0.0 for v in query_vec):
            return []

        cursor = self.conn.cursor()
        query_blob = struct.pack(f"{EMBEDDING_DIM}f", *query_vec)

        # 1. 向量搜索
        cursor.execute(
            """
            SELECT id, distance FROM chunks_vec 
            WHERE embedding MATCH ? AND k = ? ORDER BY distance
        """,
            (query_blob, limit * 2),
        )
        vec_res = {r[0]: r[1] for r in cursor.fetchall()}

        # 2. 关键词搜索
        cursor.execute(
            """
            SELECT rowid, rank FROM chunks_fts 
            WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?
        """,
            (query, limit * 2),
        )
        fts_res = {r[0]: r[1] for r in cursor.fetchall()}

        # 3. 融合
        all_ids = set(vec_res.keys()) | set(fts_res.keys())
        scores = []

        # 极简归一化函数
        def norm(val, min_v, max_v):
            if max_v == min_v:
                return 0.0
            return (val - min_v) / (max_v - min_v)

        v_vals = vec_res.values() or [0]
        f_vals = fts_res.values() or [0]
        v_min, v_max = min(v_vals), max(v_vals)
        f_min, f_max = min(f_vals), max(f_vals)

        for rid in all_ids:
            # 缺失值处理: 没命中的给最差分
            v_raw = vec_res.get(rid, v_max)
            f_raw = fts_res.get(rid, f_max)

            # 归一化 (越小越好 -> 转为越大越好: 1 - norm)
            v_score = 1.0 - norm(v_raw, v_min, v_max)
            f_score = 1.0 - norm(f_raw, f_min, f_max)

            # text{最终得分} = (0.7 \times \text{向量语义得分}) + (0.3 \times \text{BM25 关键词得分})
            final = (alpha * v_score) + ((1 - alpha) * f_score)
            scores.append((rid, final))

        scores.sort(key=lambda x: x[1], reverse=True)
        # === 结果展示 ===
        results = []
        for rid, score in scores[:limit]:
            cursor.execute(
                "SELECT file_path, start_line, end_line, content FROM chunks WHERE id = ?",
                (rid,),
            )
            row = cursor.fetchone()
            if row:
                results.append(
                    {
                        "score": round(score, 4),
                        "source": f"{row[0]} (L{row[1]}-{row[2]})",  # 关键：显示行号
                        "content": row[3][:100] + "...",  # 预览
                    }
                )

        return results


# === 测试运行 ===
if __name__ == "__main__":
    store = MemoryStore()

    # memory_path = parent_dir / "memory/2026-02-10.md"
    # with open(parent_dir / memory_path, "r", encoding="utf-8") as f:
    #     memory = f.read()
    #
    # # 写入文件（模拟）
    # store.process_file(str(memory_path), memory)

    text = "刚刚聊了什么高潜客户来着？"
    print(f"\n--- {text} ---")
    results = store.search(text, limit=2)
    for r in results:
        print(f"[{r['score']}] {r['source']}\n    {r['content']}")
