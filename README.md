# Laya Decision Engine - Production Backend API & Studio

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Laya](https://img.shields.io/badge/Laya-System%201%20Engine-emerald.svg)](https://github.com/NandhaKishorM/laya)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

REST API backend and interactive Web Studio for **[Laya](https://github.com/NandhaKishorM/laya)** .

---

## ⚡ Fitur Utama

- **Single Forward Pass Decision Engine (`/api/v1/predict`)**: Mengevaluasi pertanyaan typed (`choice`, `score`, `noul`) dalam <35ms.
- **API Token Security & Key Generator (`/api/v1/api-keys`)**: Generate, kelola, dan revoke API Key (`laya_live_...`) dengan proteksi wajib via header `X-API-Key: <token>`.
- **Custom Workflow Project Builder (`/api/v1/workflows`)**: Membuat, menyimpan, dan mengelola alur keputusan kustom baru langsung dari Web UI (tersimpan permanen dalam JSON).
- **Live cURL & Python Code Snippet Generator**: Preview otomatis perintah `curl`, Python (`requests`), dan JavaScript `fetch` yang sinkron secara real-time dengan API Key aktif.
- **Dedicated Login Screen & User Management (`/api/v1/auth`)**: Gate autentikasi penuh sebelum masuk studio dengan password hashing PBKDF2-HMAC-SHA256 (Default: `admin` / `admin123`) serta fitur ganti password.
- **Intelligent Checkpoint Router**: Otomatis merutekan ke `english` (ModernBERT) atau `multilingual` (mmBERT-base, 100+ bahasa termasuk Bahasa Indonesia).
- **Production Preloading (`/api/v1/router/preload`)**: Menjaga model tetap panas di RAM/VRAM untuk menghilangkan cold-start latency.
- **Built-in Presets (`/api/v1/presets`)**: Preset bawaan untuk Support Ticket Triage, Inbound Email Filtering, Prompt Injection & Guardrails, Content Moderation, AI Agent Observability, dan Invoice Anomaly.

---

## 🚀 Panduan Memulai Cepat (Quickstart)

### 1. Menjalankan Server API

```powershell
# Jalankan server
.\.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Akses layanan di browser:
- 🌐 **Web Studio & Playground**: [http://localhost:8000](http://localhost:8000)
- 📖 **Swagger UI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📑 **ReDoc Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔐 Kredensial Login & API Token

| Akses | Kredensial Default | Keterangan |
|---|---|---|
| **Web Studio Login** | `admin` / `admin123` | Login untuk masuk ke UI Dashboard (dapat diganti di modal profil) |
| **API Token Header** | `X-API-Key: laya_live_...` | Wajib disertakan pada setiap request API eksternal |

---

## 📡 Contoh Memanggil API dengan API Key

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: laya_live_xxxxxxxxxxxxxxxxxxxxxxxx" \
  -d '{
    "state": {
      "customer": "Budi",
      "pesan": "Tolong batalkan pesanan saya dan kembalikan uangnya."
    },
    "preset": "triage"
  }'
```

*Jika request tidak menyertakan API Key yang valid saat proteksi aktif, server akan mengembalikan status `401 Unauthorized`.*

---

## 🧪 Pengujian (Pytest)

Jalankan seluruh 23 pengujian unit & integrasi:

```powershell
.\.venv\Scripts\pytest -v
```

Hasil:
```
tests/test_api_keys.py::test_api_key_lifecycle_and_protection PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_workflows.py::test_create_and_list_custom_workflow PASSED
...
======================= 23 passed in 1.48s =======================
```
