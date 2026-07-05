"""AI-generated unit tests for the AI CLI Assistant learning project."""

import json
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main


class CommandTests(unittest.TestCase):
    def test_should_exit_accepts_exit_commands(self):
        self.assertTrue(main.should_exit("exit"))
        self.assertTrue(main.should_exit("quit"))
        self.assertTrue(main.should_exit("bye"))
        self.assertFalse(main.should_exit("hello"))

    def test_should_clear_accepts_clear_commands(self):
        self.assertTrue(main.should_clear("clear"))
        self.assertTrue(main.should_clear("reset"))
        self.assertTrue(main.should_clear("forget"))
        self.assertFalse(main.should_clear("history"))


class FilePathTests(unittest.TestCase):
    def test_find_text_file_paths_returns_supported_files_in_order(self):
        user_input = "compare README.md, main.py, and data.json"

        result = main.find_text_file_paths(user_input)

        self.assertEqual(result, ["README.md", "main.py", "data.json"])

    def test_find_text_file_paths_removes_duplicates(self):
        user_input = "summarize README.md then compare README.md with testdoc.md"

        result = main.find_text_file_paths(user_input)

        self.assertEqual(result, ["README.md", "testdoc.md"])

    def test_find_text_file_paths_ignores_unsupported_files(self):
        user_input = "read image.png and notes.md"

        result = main.find_text_file_paths(user_input)

        self.assertEqual(result, ["notes.md"])


class HistoryTests(unittest.TestCase):
    def test_add_conversation_history_adds_default_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / "conversation_history.json"
            conversation_history = []

            with patch.object(main, "HISTORY_FILE", history_file):
                main.add_conversation_history(
                    conversation_history,
                    "user",
                    "hello"
                )

            self.assertEqual(len(conversation_history), 1)
            self.assertEqual(conversation_history[0]["role"], "user")
            self.assertEqual(conversation_history[0]["content"], "hello")
            self.assertFalse(conversation_history[0]["metadata"]["used_file"])
            self.assertEqual(conversation_history[0]["metadata"]["file_paths"], [])
            self.assertIn("timestamp", conversation_history[0]["metadata"])

    def test_add_conversation_history_saves_to_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / "conversation_history.json"
            conversation_history = []

            with patch.object(main, "HISTORY_FILE", history_file):
                main.add_conversation_history(
                    conversation_history,
                    "user",
                    "summarize README.md",
                    metadata={
                        "used_file": True,
                        "file_paths": ["README.md"],
                    }
                )

            saved_history = json.loads(history_file.read_text(encoding="utf-8"))

            self.assertEqual(saved_history[0]["role"], "user")
            self.assertEqual(saved_history[0]["metadata"]["file_paths"], ["README.md"])

    def test_load_conversation_history_returns_empty_list_for_missing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / "missing.json"

            with patch.object(main, "HISTORY_FILE", history_file):
                result = main.load_conversation_history()

            self.assertEqual(result, [])

    def test_load_conversation_history_returns_empty_list_for_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / "conversation_history.json"
            history_file.write_text("not json", encoding="utf-8")

            with patch.object(main, "HISTORY_FILE", history_file):
                with redirect_stdout(io.StringIO()):
                    result = main.load_conversation_history()

            self.assertEqual(result, [])


class FileMemoryTests(unittest.TestCase):
    def test_read_text_file_reads_and_caches_supported_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "notes.md"
            file_path.write_text("hello from file", encoding="utf-8")
            file_history = {}

            with redirect_stdout(io.StringIO()):
                result = main.read_text_file(file_history, str(file_path))

            self.assertEqual(result, "hello from file")
            self.assertEqual(file_history[str(file_path)], "hello from file")

    def test_read_text_file_returns_cached_content(self):
        file_history = {"notes.md": "cached content"}

        with redirect_stdout(io.StringIO()):
            result = main.read_text_file(file_history, "notes.md")

        self.assertEqual(result, "cached content")

    def test_build_prompt_adds_each_file_context_once(self):
        conversation_history = [
            {
                "role": "user",
                "content": "summarize README.md",
                "metadata": {
                    "used_file": True,
                    "file_paths": ["README.md"],
                },
            },
            {
                "role": "assistant",
                "content": "Summary here",
                "metadata": {
                    "used_file": False,
                    "file_paths": [],
                },
            },
            {
                "role": "user",
                "content": "compare README.md and testdoc.md",
                "metadata": {
                    "used_file": True,
                    "file_paths": ["README.md", "testdoc.md"],
                },
            },
        ]
        file_history = {
            "README.md": "readme contents",
            "testdoc.md": "testdoc contents",
        }

        with redirect_stdout(io.StringIO()):
            prompt = main.build_prompt(conversation_history, file_history)

        self.assertEqual(prompt[0]["role"], "developer")
        self.assertEqual(prompt[0]["content"].count("File: README.md"), 1)
        self.assertEqual(prompt[0]["content"].count("File: testdoc.md"), 1)

    def test_build_prompt_removes_metadata_from_model_messages(self):
        conversation_history = [
            {
                "role": "user",
                "content": "hello",
                "metadata": {
                    "used_file": False,
                    "file_paths": [],
                    "response_output": {"answer": "hidden app data"},
                },
            }
        ]

        prompt = main.build_prompt(conversation_history, {})

        self.assertEqual(prompt, [{"role": "user", "content": "hello"}])


class StructuredOutputTests(unittest.TestCase):
    def test_assistant_response_schema_requires_expected_fields(self):
        schema = main.ASSISTANT_RESPONSE_SCHEMA

        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            schema["required"],
            ["answer", "summary", "files_used", "follow_up_questions"]
        )
        self.assertNotIn("required", schema["properties"])
        self.assertNotIn("additionalProperties", schema["properties"])

    def test_parse_response_returns_structured_output_dict(self):
        class FakeResponse:
            output_text = json.dumps({
                "answer": "README.md explains the app.",
                "summary": "Summarized README.md.",
                "files_used": ["README.md"],
                "follow_up_questions": [
                    "How does file reading work?",
                    "Where is conversation history saved?"
                ],
            })

        parsed = main.parse_response(FakeResponse())

        self.assertEqual(parsed["answer"], "README.md explains the app.")
        self.assertEqual(parsed["files_used"], ["README.md"])
        self.assertEqual(len(parsed["follow_up_questions"]), 2)

    def test_ask_ai_sends_json_schema_response_format(self):
        class FakeResponses:
            def __init__(self):
                self.kwargs = None

            def create(self, **kwargs):
                self.kwargs = kwargs
                return "fake response"

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        client = FakeClient()

        response = main.ask_ai(client, [{"role": "user", "content": "hello"}])

        self.assertEqual(response, "fake response")
        format_config = client.responses.kwargs["text"]["format"]
        self.assertEqual(format_config["type"], "json_schema")
        self.assertTrue(format_config["strict"])
        self.assertIs(format_config["schema"], main.ASSISTANT_RESPONSE_SCHEMA)


if __name__ == "__main__":
    unittest.main()
