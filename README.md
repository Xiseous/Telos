<h1 align="center">Telos – Telegram External Loader & Orchestrator System</h1>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-00BFA6?style=for-the-badge">
  <img alt="Automation" src="https://img.shields.io/badge/Automation-GitHub%20Actions-FFD700?style=for-the-badge">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Ready-00BFA6?style=for-the-badge">
  <img alt="Status" src="https://img.shields.io/badge/Status-Active-FFD700?style=for-the-badge">
</p>

A fully containerized system for automatically downloading modified iOS apps from Telegram and generating multi-format repositories—including full AltStore compatibility with intelligent bundle ID aggregation and version prioritization.

---

## ✨ Features

- **Automated Telegram Downloads**  
- **Generates 4 Repository Formats**  
  - `store.json` (AltStore/SideStore)  
  - `esign.json`  
  - `scarlet.json`  
  - `feather.json`
- **TDLib Integration**
- **Bundle ID Aggregation + Version Prioritization**
- **Docker-Based Deployment**
- **GitHub Actions Automation**
- **Zero API Costs**

---

## 🚀 How It Works

1. TDLib authenticates to Telegram  
2. Messages/files are fetched from configured channels  
3. `.ipa` files are downloaded  
4. All 4 repo formats are generated  
5. Bundle IDs are aggregated, versions prioritized  
6. Optional `PRIORITY_APPS` overrides  
7. Can run on Docker or GitHub Actions  

---

## 📁 File Structure

```
Telos/
├── .github/
│   └── workflows/
│       └── telegram-files.yml
├── Files/                 # Downloaded files
├── Assets/               # Icons and images
│   ├── app_icon.png      # Default app icon
│   ├── source_icon.png   # Source icon
│   └── source_header.png # Source header
├── scripts/
│   ├── download_telegram_files.py
│   └── update_repo_json.py
├── repo.altstore.json    # Generated repository file
├── .env.example         # Configuration template
└── README.md
```

---

## 📌 Metadata

**Author:** Xiseous  
**Version:** 3.0  
**Last Updated:** 2025-11-15  

---

## ⚠️ Security Notice

This workflow downloads files automatically from Telegram.  
Use trusted sources and always verify `.ipa` files before redistribution.
