import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


async def _fake_async_events(items):
    for item in items:
        yield item


class MainApiTests(unittest.TestCase):
    def test_env_flag(self) -> None:
        self.assertTrue(main._env_flag("__NON_EXISTING_FLAG__", default=True))
        self.assertFalse(main._env_flag("__NON_EXISTING_FLAG__", default=False))

    def test_prompt_render(self) -> None:
        text = main.PROMPTS.render_prompt(
            "main_system",
            {
                "long_term_path": "/memories/MEMORY.md",
                "today_path": "/memories/daily/2026-02-12.md",
                "yesterday_path": "/memories/daily/2026-02-11.md",
            },
        )
        self.assertIn("代理人万能销售助手", text)
        self.assertIn("/memories/daily/2026-02-11.md", text)

    def test_convert_dict_history(self) -> None:
        history = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ]
        result = main._to_deepagent_messages(history, "next")
        self.assertEqual(
            result,
            [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "hi"},
                {"role": "user", "content": "next"},
            ],
        )

    def test_convert_tuple_history(self) -> None:
        history = [
            ("hello", "hi"),
            ("second", None),
        ]
        result = main._to_deepagent_messages(history, "next")
        self.assertEqual(
            result,
            [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "hi"},
                {"role": "user", "content": "second"},
                {"role": "user", "content": "next"},
            ],
        )

    def test_frontend_files_exist(self) -> None:
        root = Path(main.FRONTEND_DIR)
        self.assertTrue((root / "index.html").exists())
        self.assertTrue((root / "style.css").exists())
        self.assertTrue((root / "script.js").exists())

    def test_health_endpoint(self) -> None:
        client = TestClient(main.app)
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")

    def test_chat_endpoint(self) -> None:
        client = TestClient(main.app)

        with patch.object(
            main,
            "chat_with_agent",
            return_value=(
                "reply-ok",
                "thread-1",
                [
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": "reply-ok"},
                ],
            ),
        ):
            response = client.post("/api/chat", json={"message": "hello", "history": []})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["reply"], "reply-ok")
        self.assertEqual(payload["thread_id"], "thread-1")
        self.assertEqual(len(payload["history"]), 2)

    def test_chat_with_agent_dispatches_memory_agent(self) -> None:
        class DummyAgent:
            def __init__(self):
                self.last_payload = None

            def invoke(self, payload, **_kwargs):
                self.last_payload = payload
                return {"messages": [{"type": "ai", "content": "ok"}]}

        agent = DummyAgent()
        with patch.object(main, "get_agent", return_value=agent):
            with patch.object(main, "_dispatch_memory_agent") as mock_dispatch:
                reply, _, _ = main.chat_with_agent("u", [], None)

        self.assertEqual(reply, "ok")
        self.assertEqual(agent.last_payload, {"messages": [{"role": "user", "content": "u"}]})
        mock_dispatch.assert_called_once_with(user_message="u", assistant_message="ok")

    def test_dispatch_memory_agent_can_be_disabled(self) -> None:
        with patch.object(main, "MEMORY_AGENT_ENABLED", False):
            with patch("main.threading.Thread") as mock_thread:
                main._dispatch_memory_agent("u", "a")

        mock_thread.assert_not_called()

    def test_sse_payload_format(self) -> None:
        line = main._to_sse({"event": "delta", "text": "abc"})
        self.assertTrue(line.startswith("data: "))
        self.assertTrue(line.endswith("\n\n"))

    def test_extract_ai_text_from_updates(self) -> None:
        update_chunk = (
            (),
            {
                "model": {
                    "messages": [
                        {"type": "ai", "content": "回答A"},
                    ]
                }
            },
        )
        text = main._extract_ai_text_from_updates(update_chunk)
        self.assertEqual(text, "回答A")

    def test_sanitize_user_facing_text(self) -> None:
        raw = (
            "我来读取一下我的记忆，然后清楚地回答你。\n"
            "**结论**：建议先做客户分层。\n"
            "- A类客户优先\n"
            "工作原则：专业严谨"
        )
        out = main._sanitize_user_facing_text(raw)
        self.assertNotIn("读取", out)
        self.assertNotIn("工作原则", out)
        self.assertIn("结论：建议先做客户分层", out)

    def test_consume_stream_buffer_filters_internal_line(self) -> None:
        flushed, remain = main._consume_stream_buffer(
            "我来读取一下我的记忆，然后清楚地回答你。\n建议先做客户分层"
        )
        self.assertEqual(flushed, "")
        self.assertEqual(remain, "建议先做客户分层")

    def test_update_descriptions(self) -> None:
        lines = main._iter_update_descriptions(((), {"planner": {"todo": "x"}}))
        self.assertTrue(any("步骤: planner" in line for line in lines))

    def test_merge_long_term_memory(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "MEMORY.md"
            path.write_text(
                "# 长期记忆\n\n## 用户偏好\n- 喜欢橙色\n\n## 重要决策\n- 暂无\n\n## 关键联系人\n- 暂无\n\n## 项目事实\n- 暂无\n",
                encoding="utf-8",
            )

            main._merge_long_term_memory(
                {
                    "用户偏好": ["喜欢橙色", "需要流式输出"],
                    "项目事实": ["记忆在 memories/daily"],
                },
                path,
            )
            content = path.read_text(encoding="utf-8")
            self.assertIn("- 喜欢橙色", content)
            self.assertIn("- 需要流式输出", content)
            self.assertIn("- 记忆在 memories/daily", content)

    def test_chat_stream_endpoint(self) -> None:
        client = TestClient(main.app)

        fake_events = _fake_async_events(
            [
                {"event": "start", "thread_id": "thread-2"},
                {"event": "process", "text": "步骤: planner"},
                {"event": "delta", "text": "hello"},
                {
                    "event": "done",
                    "reply": "hello",
                    "thread_id": "thread-2",
                    "history": [
                        {"role": "user", "content": "hi"},
                        {"role": "assistant", "content": "hello"},
                    ],
                },
            ]
        )

        with patch.object(main, "stream_chat_with_agent", return_value=fake_events):
            response = client.post(
                "/api/chat/stream",
                json={"message": "hi", "history": []},
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn('"event": "process"', response.text)
        self.assertIn('"event": "delta"', response.text)
        self.assertIn('"event": "done"', response.text)


if __name__ == "__main__":
    unittest.main()
