# 🔍 KFIS v2.0 — Chatbot Audit Keuangan Kontraktor

**Kontraktor Financial Intelligence System** — AI auditor keuangan spesialis
perusahaan kontraktor & civil engineering Indonesia.

Chatbot ini menjalankan **MASTER PROMPT KFIS v2.0** di atas Claude (Anthropic API):
deteksi kebocoran keuangan, Fraud Hexagon, 47 Red Flag, Beneish M-Score,
Benford's Law, PSAK 34 & PSAK 72.

## Struktur

```
07-kfis-chatbot/
├── system_prompt.py        # Master prompt KFIS v2.0
├── chatbot_cli.py          # Versi terminal (CLI)
├── chatbot_streamlit.py    # Versi Web UI (Streamlit)
├── requirements.txt        # Dependensi
├── .env.example            # Contoh konfigurasi
└── README.md
```

## Persiapan

```bash
cd 07-kfis-chatbot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Menjalankan

### 1. Versi CLI

```bash
python chatbot_cli.py
```

Perintah dalam chat:
- `/reset` — mulai sesi audit baru
- `/save` — simpan transkrip ke `transcript_*.md`
- `/load <file>` — muat isi file teks sebagai data audit
- `/exit` — keluar

Input mendukung multi-baris — tekan **Enter dua kali** untuk mengirim.

### 2. Versi Web (Streamlit)

```bash
streamlit run chatbot_streamlit.py
```

Fitur Web UI:
- Riwayat percakapan persisten dalam satu sesi
- Upload file (`.txt`, `.csv`, `.md`, `.json`) sebagai data audit
- Streaming jawaban real-time
- Unduh transkrip `.md`
- Reset sesi & input API key langsung dari sidebar

## Cara Pakai untuk Audit

1. Jalankan chatbot.
2. Pada giliran pertama, KFIS akan meminta:
   - Nama proyek / perusahaan
   - Periode audit
   - Jenis perusahaan (CV / PT / BUMN)
   - Konteks audit (rutin / forensik / due diligence)
   - Kecurigaan spesifik (jika ada)
3. Tempelkan data keuangan: laporan laba rugi, buku kas, RAB,
   laporan termin, daftar transaksi, dll.
4. KFIS akan menghasilkan **Laporan Audit 8 Bagian**:
   - Ringkasan Eksekutif
   - Temuan Kritis (dengan Risk Score)
   - Analisis Rasio Keuangan
   - Analisis Tren & Anomali
   - Entity Mapping
   - Beneish M-Score
   - Rekomendasi Tindakan
   - Daftar Dokumen yang Perlu Diminta

## Catatan

- Model default: `claude-opus-4-7`. Ubah konstanta `MODEL` di kedua file
  untuk memakai Sonnet/Haiku.
- `max_tokens` default 4096 — naikkan jika laporan terpotong.
- Riwayat percakapan dikirim utuh setiap giliran (belum ada
  trimming/summarization) — sesi sangat panjang akan boros token.

## Disclaimer

Output bersifat **indikatif** dan memerlukan verifikasi lapangan sebelum
disimpulkan sebagai fraud. KFIS tidak memberikan saran hukum.
