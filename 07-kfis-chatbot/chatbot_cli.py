"""
KFIS v2.0 — Chatbot CLI
Audit Keuangan Kontraktor & Civil Engineering Indonesia

Cara pakai:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python chatbot_cli.py

Perintah dalam chat:
    /reset    -> mulai sesi audit baru (kosongkan riwayat)
    /save     -> simpan transkrip ke file .md
    /load <file> -> muat isi file teks sebagai data tambahan
    /exit     -> keluar
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: paket 'anthropic' belum terinstal.")
    print("Jalankan: pip install -r requirements.txt")
    sys.exit(1)

from system_prompt import SYSTEM_PROMPT, GREETING_MESSAGE

MODEL = os.environ.get("KFIS_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.environ.get("KFIS_MAX_TOKENS", "4096"))


def banner() -> None:
    print("=" * 72)
    print(" 🔍  KFIS v2.0  —  KONTRAKTOR FINANCIAL INTELLIGENCE SYSTEM")
    print("     AI Audit Keuangan Kontraktor & Civil Engineering Indonesia")
    print("=" * 72)
    print(" Perintah: /reset  /save  /load <file>  /exit")
    print("-" * 72)


def save_transcript(history: list[dict]) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(f"transcript_{stamp}.md")
    lines = [f"# KFIS v2.0 — Transkrip Audit ({stamp})\n"]
    for msg in history:
        role = "🧑 User" if msg["role"] == "user" else "🤖 KFIS"
        lines.append(f"\n## {role}\n\n{msg['content']}\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path.resolve())


def load_file(arg: str) -> str | None:
    path = Path(arg.strip())
    if not path.exists():
        print(f"   ⚠️  File tidak ditemukan: {path}")
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"   ⚠️  Gagal membaca file: {e}")
        return None


def read_multiline() -> str:
    """Baca input multi-baris. Akhiri dengan baris kosong dua kali, atau EOF."""
    print("Anda  > (tekan Enter dua kali untuk kirim, atau ketik perintah /...)")
    lines: list[str] = []
    blank_streak = 0
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            blank_streak += 1
            if blank_streak >= 2 and lines:
                break
            if not lines:
                continue
            lines.append(line)
        else:
            blank_streak = 0
            lines.append(line)
    return "\n".join(lines).strip()


def chat_once(client: Anthropic, history: list[dict]) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=history,
    )
    return "".join(block.text for block in response.content if block.type == "text")


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: variabel lingkungan ANTHROPIC_API_KEY belum diset.")
        print('Contoh: export ANTHROPIC_API_KEY="sk-ant-..."')
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    history: list[dict] = []

    banner()
    print(f"\n🤖 KFIS > {GREETING_MESSAGE}\n")

    while True:
        try:
            user_input = read_multiline()
        except KeyboardInterrupt:
            print("\n\nSesi dihentikan oleh pengguna.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/exit", "/quit"):
            print("\nSesi audit ditutup. Sampai jumpa, Wisnu! 👋")
            break

        if user_input.lower() == "/reset":
            history = []
            print("\n   🔄 Riwayat sesi direset. Mulai audit baru.\n")
            print(f"🤖 KFIS > {GREETING_MESSAGE}\n")
            continue

        if user_input.lower() == "/save":
            if not history:
                print("   ⚠️  Belum ada percakapan untuk disimpan.\n")
                continue
            path = save_transcript(history)
            print(f"   💾 Transkrip tersimpan: {path}\n")
            continue

        if user_input.lower().startswith("/load"):
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                print("   Format: /load <path-file>\n")
                continue
            content = load_file(parts[1])
            if content is None:
                continue
            user_input = (
                f"Berikut data dari file `{parts[1]}` untuk diaudit:\n\n"
                f"```\n{content}\n```"
            )
            print(f"   📎 File dimuat ({len(content)} karakter).\n")

        history.append({"role": "user", "content": user_input})

        try:
            print("\n🤖 KFIS > ", end="", flush=True)
            reply = chat_once(client, history)
        except Exception as e:
            print(f"\n   ⚠️  Gagal menghubungi API: {e}\n")
            history.pop()
            continue

        history.append({"role": "assistant", "content": reply})
        print(reply + "\n")


if __name__ == "__main__":
    main()
