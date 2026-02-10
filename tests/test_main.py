import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


class MainApiTests(unittest.TestCase):
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

    def test_sync_skills_to_project(self) -> None:
        with TemporaryDirectory() as source_tmp, TemporaryDirectory() as target_tmp:
            source = Path(source_tmp)
            target = Path(target_tmp)
            skill_file = source / "demo-skill" / "SKILL.md"
            skill_file.parent.mkdir(parents=True, exist_ok=True)
            skill_file.write_text("# demo", encoding="utf-8")

            main._sync_skills_to_project(source, target)

            copied = target / "demo-skill" / "SKILL.md"
            self.assertTrue(copied.exists())

    def test_update_descriptions(self) -> None:
        lines = main._iter_update_descriptions(((), {"planner": {"todo": "x"}}))
        self.assertTrue(any("步骤: planner" in line for line in lines))

    def test_chat_stream_endpoint(self) -> None:
        client = TestClient(main.app)

        fake_events = iter(
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
