"""
Amy AI Provider Manager
========================
Priority order:
  1. Groq  — llama-3.3-70b-versatile  (10 keys rotating, free & fast)
  2. HuggingChat — free fallback

All providers share the same call_ai() interface.
"""

import os
import asyncio
import itertools
import logging
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Groq key rotation
# ─────────────────────────────────────────────

def _is_usable_key(value: str | None) -> bool:
    if not value:
        return False
    cleaned = value.strip()
    if not cleaned:
        return False
    lowered = cleaned.lower()
    return not ("xxxx" in lowered or "your_" in lowered or "replace" in lowered)


def _resolve_cookie_path(path_value: str) -> str:
    cookie_path = Path(path_value)
    if not cookie_path.is_absolute():
        cookie_path = BASE_DIR / cookie_path
    return str(cookie_path.resolve())


def _load_groq_keys() -> list[str]:
    keys = []
    # Single key support
    single = os.getenv("GROQ_API_KEY")
    if _is_usable_key(single):
        keys.append(single.strip())
    # Numbered keys GROQ_API_KEY_1 … GROQ_API_KEY_10
    for i in range(1, 11):
        k = os.getenv(f"GROQ_API_KEY_{i}")
        if _is_usable_key(k):
            keys.append(k.strip())
    # Remove duplicates while preserving order
    seen, unique = set(), []
    for k in keys:
        if k not in seen:
            seen.add(k)
            unique.append(k)
    return unique


_groq_keys:  list[str]         = _load_groq_keys()
_groq_cycle: itertools.cycle | None = itertools.cycle(_groq_keys) if _groq_keys else None


def get_next_groq_key() -> str | None:
    """Returns the next Groq API key in the rotation (round-robin)."""
    return next(_groq_cycle) if _groq_cycle else None


def groq_key_count() -> int:
    return len(_groq_keys)


# ─────────────────────────────────────────────
# Provider list builder
# ─────────────────────────────────────────────

def get_providers() -> list[dict]:
    """
    Returns ordered list of available providers.
    Called fresh on every request so rotation is applied correctly.
    """
    providers = []

    # ── 1. Groq (rotating key) ──────────────────────────────────
    groq_key = get_next_groq_key()
    if groq_key:
        providers.append({
            "name":     "groq",
            "key":      groq_key,
            "model":    "llama-3.3-70b-versatile",
            "base_url": "https://api.groq.com/openai/v1",
            "type":     "openai_compat",
        })

    # ── 2. HuggingChat (always-on fallback) ─────────────────────
    hugchat_cookie = _resolve_cookie_path(os.getenv("HUGCHAT_COOKIE_PATH", "cookie.json"))
    if os.path.exists(hugchat_cookie):
        providers.append({
            "name":        "hugchat",
            "cookie_path": hugchat_cookie,
            "type":        "hugchat",
        })

    return providers


# ─────────────────────────────────────────────
# HuggingChat sync caller (runs in thread pool)
# ─────────────────────────────────────────────

def _hugchat_call(cookie_path: str, system: str, messages: list) -> str:
    from hugchat import hugchat as hc

    chatbot = hc.ChatBot(cookie_path=cookie_path)

    # Build a single prompt from system + history + latest user message
    history_text = ""
    for m in messages[:-1]:
        prefix = "User" if m["role"] == "user" else "Amy"
        history_text += f"{prefix}: {m['content']}\n"

    user_msg = messages[-1]["content"] if messages else ""
    full_prompt = f"{system}\n\n{history_text}User: {user_msg}\nAmy:"

    cid = chatbot.new_conversation()
    chatbot.change_conversation(cid)
    return str(chatbot.chat(full_prompt))


# ─────────────────────────────────────────────
# Main AI caller — fallback chain
# ─────────────────────────────────────────────

async def call_ai(system: str, messages: list) -> tuple[str, str]:
    """
    Try each provider in order. Return (reply_text, provider_name).
    Raises Exception if all providers fail.
    """
    providers = get_providers()

    if not providers:
        raise Exception(
            "No AI provider configured! "
            "Add GROQ_API_KEY_1 … GROQ_API_KEY_10 to .env, "
            "or place cookie.json at backend/cookie.json for HuggingChat fallback."
        )

    last_error = None

    for provider in providers:
        try:
            # ── Groq / OpenAI-compatible ──
            if provider["type"] == "openai_compat":
                from openai import OpenAI
                client = OpenAI(
                    api_key=provider["key"],
                    base_url=provider["base_url"],
                )
                all_msgs = [{"role": "system", "content": system}] + messages
                response = client.chat.completions.create(
                    model=provider["model"],
                    messages=all_msgs,
                    max_tokens=600,
                    temperature=0.8,
                )
                return response.choices[0].message.content, provider["name"]

            # ── HuggingChat (sync → thread) ──
            elif provider["type"] == "hugchat":
                loop = asyncio.get_event_loop()
                text = await loop.run_in_executor(
                    None,
                    _hugchat_call,
                    provider["cookie_path"],
                    system,
                    messages,
                )
                return text.strip(), "hugchat"

        except Exception as e:
            last_error = f"{provider['name']}: {str(e)[:120]}"
            logger.warning(f"[AI] Provider {provider['name']} failed: {str(e)[:120]}")
            continue

    raise Exception(f"All AI providers failed. Last error → {last_error}")


# ─────────────────────────────────────────────
# Status helper (used by /api/amy/status)
# ─────────────────────────────────────────────

def get_provider_status() -> dict:
    providers = get_providers()
    return {
        "groq_keys_loaded":  groq_key_count(),
        "hugchat_available": any(p["type"] == "hugchat" for p in providers),
        "active_providers":  [p["name"] for p in providers],
        "total":             len(providers),
        "ready":             len(providers) > 0,
    }
