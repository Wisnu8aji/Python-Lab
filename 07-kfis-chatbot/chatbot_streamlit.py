"""
KFIS v2.0 — Chatbot Web UI (Streamlit)
Audit Keuangan Kontraktor & Civil Engineering Indonesia

Cara pakai:
    export ANTHROPIC_API_KEY="sk-ant-..."
    streamlit run chatbot_streamlit.py
"""

import os
from pathlib import Path

import streamlit as st
from anthropic import Anthropic

from system_prompt import SYSTEM_PROMPT, GREETING_MESSAGE

MODEL = "claude-opus-4-7"
MAX_TOKENS = 4096


def get_client() -> Anthropic | None:
    api_key = st.session_state.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return Anthropic(api_key=api_key)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### ⚙️ Konfigurasi")

        existing_key = os.environ.get("ANTHROPIC_API_KEY", "")
        st.session_state.setdefault("api_key", existing_key)
        st.session_state["api_key"] = st.text_input(
            "Anthropic API Key",
            value=st.session_state["api_key"],
            type="password",
            help="Dari console.anthropic.com",
        )

        st.markdown("---")
        st.markdown("### 📎 Unggah Dokumen")
        uploaded = st.file_uploader(
            "Tempel file teks/CSV (opsional)",
            type=["txt", "csv", "md", "json"],
            accept_multiple_files=True,
        )
        if uploaded and st.button("Kirim file sebagai data audit"):
            payload = []
            for f in uploaded:
                try:
                    text = f.read().decode("utf-8", errors="replace")
                except Exception as e:
                    st.error(f"Gagal membaca {f.name}: {e}")
                    continue
                payload.append(f"### Berkas: {f.name}\n```\n{text}\n```")
            if payload:
                combined = "Berikut data untuk diaudit:\n\n" + "\n\n".join(payload)
                st.session_state["pending_input"] = combined

        st.markdown("---")
        if st.button("🔄 Reset Sesi"):
            st.session_state["messages"] = []
            st.rerun()

        if st.session_state.get("messages") and st.button("💾 Unduh Transkrip"):
            lines = ["# KFIS v2.0 — Transkrip Audit\n"]
            for msg in st.session_state["messages"]:
                role = "🧑 User" if msg["role"] == "user" else "🤖 KFIS"
                lines.append(f"\n## {role}\n\n{msg['content']}\n")
            st.download_button(
                "Klik untuk unduh .md",
                data="\n".join(lines),
                file_name="transkrip_kfis.md",
                mime="text/markdown",
            )

        st.markdown("---")
        st.caption(
            "**KFIS v2.0** — AI Audit Keuangan Kontraktor.\n\n"
            "Modul: Fraud Hexagon · 47 Red Flag · Beneish M-Score · "
            "Benford's Law · PSAK 34/72."
        )


def render_chat() -> None:
    st.set_page_config(
        page_title="KFIS v2.0 — Audit Keuangan Kontraktor",
        page_icon="🔍",
        layout="wide",
    )

    st.markdown(
        "## 🔍 KFIS v2.0 — Kontraktor Financial Intelligence System"
    )
    st.caption(
        "AI Audit Keuangan Spesialis Kontraktor & Civil Engineering Indonesia"
    )

    render_sidebar()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if not st.session_state["messages"]:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(GREETING_MESSAGE)

    for msg in st.session_state["messages"]:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    user_input = st.chat_input("Tulis pertanyaan atau tempel data audit...")
    pending = st.session_state.pop("pending_input", None)
    if pending and not user_input:
        user_input = pending

    if not user_input:
        return

    client = get_client()
    if client is None:
        st.error(
            "ANTHROPIC_API_KEY belum diset. "
            "Masukkan API key di sidebar atau set environment variable."
        )
        return

    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        accumulated = ""
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=st.session_state["messages"],
            ) as stream:
                for text in stream.text_stream:
                    accumulated += text
                    placeholder.markdown(accumulated + "▌")
            placeholder.markdown(accumulated)
        except Exception as e:
            placeholder.error(f"Gagal menghubungi API: {e}")
            st.session_state["messages"].pop()
            return

    st.session_state["messages"].append(
        {"role": "assistant", "content": accumulated}
    )


if __name__ == "__main__":
    render_chat()
