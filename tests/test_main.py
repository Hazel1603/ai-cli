"""AI-generated unit tests for the AI CLI Assistant learning project."""

import json
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

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

    def test_parse_response_text_returns_structured_output_dict(self):
        response_text = json.dumps({
            "answer": "README.md explains the app.",
            "summary": "Summarized README.md.",
            "files_used": ["README.md"],
            "follow_up_questions": [
                "How does file reading work?",
                "Where is conversation history saved?"
            ],
        })

        parsed = main.parse_response_text(response_text)

        self.assertEqual(parsed["answer"], "README.md explains the app.")
        self.assertEqual(parsed["files_used"], ["README.md"])
        self.assertEqual(len(parsed["follow_up_questions"]), 2)

    def test_ask_ai_stream_sends_json_schema_response_format(self):
        class FakeResponses:
            def __init__(self):
                self.kwargs = None

            def create(self, **kwargs):
                self.kwargs = kwargs
                return iter([
                    SimpleNamespace(
                        type="response.output_text.delta",
                        delta='{"answer":"hello",',
                    ),
                    SimpleNamespace(
                        type="response.output_text.delta",
                        delta='"summary":"hi","files_used":[],"follow_up_questions":[]}',
                    ),
                    SimpleNamespace(
                        type="response.completed",
                        response="fake response",
                    ),
                ])

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        client = FakeClient()

        with redirect_stdout(io.StringIO()):
            response_text, response = main.ask_ai_stream(
                client,
                [{"role": "user", "content": "hello"}],
            )

        self.assertEqual(
            response_text,
            '{"answer":"hello","summary":"hi","files_used":[],"follow_up_questions":[]}'
        )
        self.assertEqual(response, "fake response")
        format_config = client.responses.kwargs["text"]["format"]
        self.assertEqual(format_config["type"], "json_schema")
        self.assertTrue(format_config["strict"])
        self.assertIs(format_config["schema"], main.ASSISTANT_RESPONSE_SCHEMA)
        self.assertTrue(client.responses.kwargs["stream"])


class StreamingTests(unittest.TestCase):
    def test_get_event_message_reads_direct_error_message(self):
        event = SimpleNamespace(type="error", message="stream disconnected")

        self.assertEqual(main.get_event_message(event), "stream disconnected")

    def test_get_event_message_reads_response_error_message(self):
        event = SimpleNamespace(
            type="response.failed",
            response=SimpleNamespace(
                error=SimpleNamespace(message="model failed")
            ),
        )

        self.assertEqual(main.get_event_message(event), "model failed")

    def test_ask_ai_stream_prints_thinking_dot_after_half_second(self):
        class FakeResponses:
            def create(self, **kwargs):
                return iter([
                    SimpleNamespace(type="response.output_text.delta", delta='{"answer":"hello",'),
                    SimpleNamespace(type="response.output_text.delta", delta='"summary":"hi",'),
                    SimpleNamespace(type="response.output_text.delta", delta='"files_used":[],"follow_up_questions":[]}'),
                    SimpleNamespace(type="response.completed", response="fake response"),
                ])

        class FakeClient:
            responses = FakeResponses()

        times = iter([0, 0.2, 0.7, 0.8, 0.9])

        with patch.object(main.time, "monotonic", side_effect=lambda: next(times)):
            output = io.StringIO()
            with redirect_stdout(output):
                response_text, response = main.ask_ai_stream(
                    FakeClient(),
                    [{"role": "user", "content": "hello"}],
                )

        self.assertIn("thinking.", output.getvalue())
        self.assertEqual(
            response_text,
            '{"answer":"hello","summary":"hi","files_used":[],"follow_up_questions":[]}'
        )
        self.assertEqual(response, "fake response")

    def test_ask_ai_stream_returns_none_for_failed_event(self):
        class FakeResponses:
            def create(self, **kwargs):
                return iter([
                    SimpleNamespace(type="response.output_text.delta", delta="partial"),
                    SimpleNamespace(
                        type="response.failed",
                        response=SimpleNamespace(
                            error=SimpleNamespace(message="model failed")
                        ),
                    ),
                ])

        class FakeClient:
            responses = FakeResponses()

        with redirect_stdout(io.StringIO()):
            response_text, response = main.ask_ai_stream(
                FakeClient(),
                [{"role": "user", "content": "hello"}],
            )

        self.assertEqual(response_text, "partial")
        self.assertIsNone(response)


class UsageLoggingTests(unittest.TestCase):
    def test_create_empty_token_usage_returns_zero_counts(self):
        usage = main.create_empty_token_usage()

        self.assertEqual(
            usage,
            {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }
        )

    def test_get_token_usage_returns_response_usage_counts(self):
        class FakeUsage:
            input_tokens = 12
            output_tokens = 34
            total_tokens = 46

        class FakeResponse:
            usage = FakeUsage()

        usage = main.get_token_usage(FakeResponse())

        self.assertEqual(
            usage,
            {
                "input_tokens": 12,
                "output_tokens": 34,
                "total_tokens": 46,
            }
        )

    def test_get_token_usage_returns_zero_counts_when_usage_is_missing(self):
        class FakeResponse:
            pass

        usage = main.get_token_usage(FakeResponse())

        self.assertEqual(usage, main.create_empty_token_usage())

    def test_add_usage_log_writes_one_jsonl_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "usage_log.jsonl"
            usage = {
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
            }

            with patch.object(main, "LOG_FILE", log_file):
                main.add_usage_log("model_response", "hello", usage)

            lines = log_file.read_text(encoding="utf-8").splitlines()
            log_entry = json.loads(lines[0])

            self.assertEqual(len(lines), 1)
            self.assertEqual(log_entry["event"], "model_response")
            self.assertEqual(log_entry["user_input"], "hello")
            self.assertEqual(log_entry["token_usage"], usage)
            self.assertTrue(log_entry["success"])
            self.assertIn("timestamp", log_entry)

    def test_add_usage_log_can_record_failed_events(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "usage_log.jsonl"

            with patch.object(main, "LOG_FILE", log_file):
                main.add_usage_log(
                    "model_response_error",
                    "hello",
                    main.create_empty_token_usage(),
                    success=False
                )

            log_entry = json.loads(log_file.read_text(encoding="utf-8"))

            self.assertEqual(log_entry["event"], "model_response_error")
            self.assertFalse(log_entry["success"])


if __name__ == "__main__":
    unittest.main()
