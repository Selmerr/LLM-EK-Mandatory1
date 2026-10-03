from __future__ import annotations

import json
import re
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class OllamaClient:
    def __init__(self, timeout: int = 600) -> None:
        self.timeout = timeout

    def complete(
        self,
        *,
        base_url: str,
        model: str,
        messages: list[ChatMessage],
        temperature: float,
        num_predict: int = 512,
        progress_label: str | None = None,
    ) -> str:
        payload = _chat_payload(
            model=model,
            messages=messages,
            temperature=temperature,
            num_predict=num_predict,
        )
        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            start = time.monotonic()
            last_update = start
            char_count = 0
            if progress_label:
                print(f"[{progress_label}] request sent to Ollama; waiting for first tokens...", flush=True)
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                chunks: list[str] = []
                for line in response:
                    if not line.strip():
                        continue
                    body = json.loads(line.decode("utf-8"))
                    message = body.get("message", {})
                    content = message.get("content")
                    if content:
                        content_text = str(content)
                        chunks.append(content_text)
                        char_count += len(content_text)
                        now = time.monotonic()
                        if progress_label and now - last_update >= 5:
                            elapsed = int(now - start)
                            print(
                                f"[{progress_label}] generating... {char_count} chars received, {elapsed}s elapsed",
                                flush=True,
                            )
                            last_update = now
                    if body.get("done"):
                        result = _strip_thinking("".join(chunks))
                        if progress_label:
                            elapsed = int(time.monotonic() - start)
                            print(
                                f"[{progress_label}] completed: {len(result)} chars in {elapsed}s",
                                flush=True,
                            )
                        return result
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Ollama endpoint at {base_url} returned HTTP {exc.code}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach Ollama endpoint at {base_url}: {exc}") from exc
        except TimeoutError as exc:
            raise RuntimeError(
                f"Ollama endpoint at {base_url} timed out after {self.timeout} seconds. "
                "The model is probably still generating. Try a smaller model, reduce the prompt, "
                "or wait for the current Ollama request to finish before retrying."
            ) from exc
        except socket.timeout as exc:
            raise RuntimeError(
                f"Ollama endpoint at {base_url} timed out after {self.timeout} seconds. "
                "The model is probably still generating. Try a smaller model, reduce the prompt, "
                "or wait for the current Ollama request to finish before retrying."
            ) from exc

        raise RuntimeError(f"Ollama endpoint at {base_url} ended the stream without a final response")


def _strip_thinking(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r".*?</think>", "", text, count=1, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()


def _chat_payload(
    *,
    model: str,
    messages: list[ChatMessage],
    temperature: float,
    num_predict: int = 512,
) -> dict:
    return {
        "model": model,
        "messages": [message.__dict__ for message in messages],
        "stream": True,
        "think": False,
        "keep_alive": "30m",
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
