<h1 align="center">TELOS – Telegram External Loader & Orchestrator System</h1>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-00BFA6?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-FFD700?style=for-the-badge&logo=docker&logoColor=white">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-ARM64%20%7C%20x86-00BFA6?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-FFD700?style=for-the-badge">
</p>

A Docker-based system that automatically downloads IPA files from Telegram channels, extracts metadata, fetches App Store information, and publishes to GitHub with support for multiple sideloading app formats (AltStore, Esign, Scarlet, Feather).

---

## ✨ Features

- **Telegram Integration**: Monitors configured channels for .IPA files using MTProto
- **IPA Processing**: Extracts Info.plist, entitlements, and detects injected tweaks
- **App Store Lookup**: Fetches icons, screenshots, and descriptions (30-day cache)
- **Multi-Format JSON**: Generates store.json, esign.json, scarlet.json, feather.json
- **GitHub Distribution**: Uploads IPAs and JSON to your repository
- **Version Priority**: Configure preferred tweaks per app (PRIORITY_APPS)
- **Web Dashboard**: Real-time monitoring, metrics, and settings
- **Hybrid Processing**: Local Docker + GitHub Actions support

## 📝 JSON Formats

| File | Format | Notes |
|------|--------|-------|
| `store.json` | AltStore/SideStore | Version priority, MAX_VERSIONS |
| `esign.json` | Esign | Single version per app |
| `scarlet.json` | Scarlet | META + Tweaked structure |
| `feather.json` | Feather | Same as store.json |

## 🏗️ Architecture

```
TELOS Docker Container
├── Backend (FastAPI + Python)
│   ├── Telegram Scanner (TDLib)
│   ├── IPA Processor (ZIP + Plist)
│   ├── App Store API (iTunes)
│   ├── GitHub Uploader (PyGithub)
│   └── JSON Generators
├── Frontend (React + Vite)
│   ├── Dashboard
│   ├── Metrics (Charts)
│   └── Settings
└── PostgreSQL Database
```

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

<p align="center">
  Xiseous
</p>
