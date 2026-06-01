import os
import streamlit as st
import anthropic


def get_client() -> anthropic.Anthropic:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            pass
    if not key:
        st.error("ANTHROPIC_API_KEY not set. Add it in Streamlit Secrets.")
        st.stop()
    return anthropic.Anthropic(api_key=key)


def stream_claude(system: str, user: str, placeholder, model: str = "claude-opus-4-8", max_tokens: int = 4096) -> anthropic.types.Message:
    client = get_client()
    full = ""
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        for text in stream.text_stream:
            full += text
            placeholder.markdown(full + "▌")
    placeholder.markdown(full)
    return stream.get_final_message()


def stream_chat(system: str, messages: list, placeholder, model: str = "claude-opus-4-8", max_tokens: int = 1024) -> tuple[anthropic.types.Message, str]:
    client = get_client()
    full = ""
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            full += text
            placeholder.markdown(full + "▌")
    placeholder.markdown(full)
    return stream.get_final_message(), full
