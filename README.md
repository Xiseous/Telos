<h1 align="center">TELOS – Telegram External Loader & Orchestrator System</h1>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-00BFA6?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-FFD700?style=for-the-badge&logo=docker&logoColor=white">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-ARM64%20%7C%20x86-00BFA6?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-FFD700?style=for-the-badge">
</p>

<p align="center">
  A fully automated IPA distribution system that monitors Telegram channels, processes apps, and publishes to GitHub with a beautiful real-time dashboard.
</p>

---

## ✨ Features

- **Telegram Integration**: Monitors channels using TDLib with concurrent downloads (up to 20 parallel)
- **IPA Processing**: Extracts Info.plist, entitlements, and detects injected tweaks automatically
- **App Store Lookup**: Fetches icons, screenshots, and descriptions with 30-day caching
- **Multi-Format JSON**: Generates `store.json`, `esign.json`, `scarlet.json`, `feather.json`
- **GitHub Releases**: Uploads IPAs as release assets (2GB+ support) with automatic cleanup
- **Version Management**: Keep multiple versions per app with priority tweak ordering
- **Real-Time Dashboard**: Monitor scans, manage queue, browse database, view metrics
- **Database Browser**: Edit entries, refresh metadata, detect and fix corrupt entries
- **Hybrid Processing**: Run locally via Docker or use GitHub Actions as backup

---

## 🏗️ Architecture

```
TELOS Docker Container
├── Backend (FastAPI + Python)
│   ├── Telegram Scanner (TDLib)
│   ├── IPA Processor (ZIP + Plist)
│   ├── App Store Client (iTunes API)
│   ├── GitHub Releases Manager
│   ├── JSON Generators (4 formats)
│   ├── Database Reconciliation
│   ├── Git History Cleanup
│   ├── Health Monitoring
│   └── Scheduled Jobs (APScheduler)
├── Frontend (React + Vite)
│   ├── Dashboard (real-time status)
│   ├── Database Browser
│   ├── Queue Manager
│   ├── Metrics & Charts
│   ├── Logs Viewer
│   └── Settings
└── PostgreSQL Database
    ├── Downloaded IPAs
    ├── Activity Logs
    ├── Privacy Cache
    └── App Store Cache
```

---

## 📝 JSON Formats

| File | Format | Notes |
|------|--------|-------|
| `store.json` | AltStore/SideStore | Multiple versions, priority sorting |
| `esign.json` | Esign | Single version per app |
| `scarlet.json` | Scarlet | META + Tweaked structure |
| `feather.json` | Feather | Similar to AltStore format |

---

## 🏆 Why TELOS?

TELOS is designed to be the most complete, maintainable, and user-friendly IPA automation system available.

| Feature | TELOS | FTRepo | Static Libraries |
|---------|-------|--------|------------------|
| **Real-time Dashboard** | ✅ Full React UI | ❌ CLI only | ❌ None |
| **Multiple Versions** | ✅ Configurable per app | ❌ Latest only | ❌ Latest only |
| **Database Management** | ✅ Browse, edit, refresh | ❌ JSON files | ❌ None |
| **Corrupt Entry Detection** | ✅ Auto-detect & fix | ❌ None | ❌ None |
| **Telegram Client** | TDLib (official) | Telethon | Varies |
| **Concurrent Downloads** | ✅ Up to 20 parallel | ❌ Sequential | N/A |
| **Output Formats** | 4 (AltStore, Esign, Scarlet, Feather) | 2 | 1-2 |
| **AI/External API Required** | ❌ No | ✅ OpenRouter required | ❌ No |
| **Self-Hosted** | ✅ Docker | ✅ Gitea | ❌ Centralized |
| **Queue Management** | ✅ Retry, delete, batch ops | ❌ None | ❌ None |
| **Activity Logs** | ✅ Searchable, filterable | ❌ Console only | ❌ None |
| **Health Monitoring** | ✅ Component checks | ❌ None | ❌ None |
| **Cleanup Automation** | ✅ Age + version limits | ✅ Basic | ❌ Manual |

### vs. FTRepo

FTRepo requires an external AI API (OpenRouter) for metadata extraction and runs only via Gitea Actions. TELOS extracts metadata directly from IPAs and the App Store—no AI dependency. TELOS also provides a full web dashboard for monitoring and management.

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

<p align="center">
  Xiseous
</p>
