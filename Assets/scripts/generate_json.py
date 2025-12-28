#!/usr/bin/env python3
"""
TELOS JSON Generator Script

Standalone script for GitHub Actions to generate JSON files from IPAs.
This is the hybrid approach - local Docker pushes IPAs, GitHub Actions regenerates JSON.

Matches official AltStore format (YTLitePlus style).
"""

import json
import os
import re
import zipfile
import plistlib
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# =======================
# DESCRIPTION CLEANER
# =======================
LINK_PATTERNS = [
    r'https?://apps\.apple\.com/[^\s\)]+',
    r'https?://itunes\.apple\.com/[^\s\)]+',
    r'https?://.*?donate[^\s\)]*',
    r'https?://.*?paypal[^\s\)]*',
    r'https?://.*?patreon[^\s\)]*',
    r'https?://.*?ko-fi[^\s\)]*',
    r'https?://.*?github\.com/[^\s\)]+',
    r'https?://.*?bit\.ly/[^\s\)]+',
    r'https?://.*?t\.me/[^\s\)]+',
    r'https?://.*?discord[^\s\)]*',
]


def clean_description(text: str, tweaks: list = None) -> str:
    """Clean description and add tweak info."""
    if not text:
        text = ""
    
    text = text.replace('**', '').replace('__', '').replace('`', '')
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    for pattern in LINK_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    result = text.strip()
    
    if tweaks:
        tweak_str = ', '.join(tweaks[:5])
        if result:
            result += f"\n\nTweaks Injected: {tweak_str}"
        else:
            result = f"Tweaks Injected: {tweak_str}"
    
    return result


# =======================
# APP DATA
# =======================
@dataclass
class AppInfo:
    """Extracted app information."""
    bundle_id: str = ""
    app_name: str = ""
    version: str = ""
    build: str = ""
    min_ios: str = "12.0"
    device_families: list = field(default_factory=list)
    tweaks: list = field(default_factory=list)
    entitlements: list = field(default_factory=list)
    privacy: dict = field(default_factory=dict)
    file_name: str = ""
    file_size: int = 0
    file_date: str = ""
    github_url: str = ""


def extract_ipa_info(ipa_path: Path, github_base_url: str) -> Optional[AppInfo]:
    """Extract info from an IPA file."""
    try:
        mtime = datetime.fromtimestamp(ipa_path.stat().st_mtime)
        file_date = mtime.strftime('%Y-%m-%d')
        
        with zipfile.ZipFile(ipa_path, 'r') as zf:
            for name in zf.namelist():
                if name.startswith('Payload/') and name.endswith('.app/Info.plist'):
                    with zf.open(name) as f:
                        plist = plistlib.load(f)
                    
                    app_folder = name.rsplit('/', 2)[0] + '/'
                    tweaks = detect_tweaks(zf, app_folder)
                    privacy = extract_privacy(plist)
                    
                    return AppInfo(
                        bundle_id=plist.get('CFBundleIdentifier', ''),
                        app_name=plist.get('CFBundleDisplayName', plist.get('CFBundleName', '')),
                        version=plist.get('CFBundleShortVersionString', ''),
                        build=plist.get('CFBundleVersion', ''),
                        min_ios=plist.get('MinimumOSVersion', '12.0'),
                        device_families=plist.get('UIDeviceFamily', [1, 2]),
                        tweaks=tweaks,
                        privacy=privacy,
                        file_name=ipa_path.name,
                        file_size=ipa_path.stat().st_size,
                        file_date=file_date,
                        github_url=f"{github_base_url}/{ipa_path.name}",
                    )
    except Exception as e:
        print(f"Error processing {ipa_path.name}: {e}")
    return None


def detect_tweaks(zf: zipfile.ZipFile, app_folder: str) -> list:
    """Detect injected dylibs in the IPA."""
    system_libs = {'libSystem', 'libobjc', 'libc++', 'libswift', 'libz', 'libsqlite', 'libdispatch'}
    tweaks = []
    
    for name in zf.namelist():
        if name.startswith(f"{app_folder}Frameworks/") and name.endswith('.dylib'):
            dylib_name = Path(name).stem
            if not any(dylib_name.startswith(sys_lib) for sys_lib in system_libs):
                tweaks.append(dylib_name)
    
    return tweaks


def extract_privacy(plist: dict) -> dict:
    """Extract privacy usage descriptions from Info.plist."""
    privacy_keys = [
        "NSPhotoLibraryUsageDescription", "NSCameraUsageDescription",
        "NSMicrophoneUsageDescription", "NSLocationWhenInUseUsageDescription",
        "NSContactsUsageDescription", "NSCalendarsUsageDescription",
        "NSAppleMusicUsageDescription", "NSSiriUsageDescription",
        "NSBluetoothPeripheralUsageDescription", "NSLocalNetworkUsageDescription",
        "NSUserTrackingUsageDescription", "NSPhotoLibraryAddUsageDescription",
    ]
    return {k: plist[k] for k in privacy_keys if k in plist}


# =======================
# NEWS GENERATOR
# =======================
def generate_news(apps: list[AppInfo], config: dict, max_entries: int = 10) -> list[dict]:
    """
    Generate news entries from apps.
    
    Format:
    - Title: "⚙️ Telos Update X.X" (month.day)
    - Caption: "New Files Uploaded:\nApp1 - (Tweak) Version\nApp2 - Version..."
    - TintColor: Alternates between #00BFA6 and #FFD700
    """
    # Alternating colors
    TINT_COLORS = ["#00BFA6", "#FFD700"]
    
    apps_by_date = defaultdict(list)
    for app in apps:
        apps_by_date[app.file_date].append(app)
    
    sorted_dates = sorted(apps_by_date.keys(), reverse=True)[:max_entries]
    news_url = config.get('news_url', '')
    
    news = []
    for idx, date_str in enumerate(sorted_dates):
        date_apps = apps_by_date[date_str]
        
        # Build friendly file list
        file_list = []
        for app in date_apps:
            if app.tweaks:
                # Get primary tweak name (skip lib* prefixes)
                tweak_names = [t for t in app.tweaks if not t.startswith('lib')]
                if tweak_names:
                    tweak_str = tweak_names[0]
                    file_list.append(f"{app.app_name} - ({tweak_str}) {app.version}")
                else:
                    file_list.append(f"{app.app_name} - {app.version}")
            else:
                file_list.append(f"{app.app_name} - {app.version}")
        
        # Build caption with friendly file list
        caption = "New Files Uploaded:\n" + "\n".join(file_list)
        
        # Generate version number from date (e.g., 12.21 for Dec 21)
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            version_str = f"{dt.month}.{dt.day}"
        except:
            version_str = date_str.replace('-', '.')
        
        # Alternate tint colors
        tint_color = TINT_COLORS[idx % 2]
        
        entry = {
            "title": f"⚙️ Telos Update {version_str}",
            "identifier": f"telos-update-{date_str}",
            "caption": caption,
            "date": date_str,
            "tintColor": tint_color,
            "notify": True,
            "appID": date_apps[0].bundle_id,  # Link to first app
        }
        
        # Add url if configured
        if news_url:
            entry["url"] = news_url
        
        news.append(entry)
    
    return news


# =======================
# JSON GENERATORS
# =======================
def generate_store_json(apps: list[AppInfo], config: dict) -> dict:
    """Generate AltStore/SideStore format JSON (YTLitePlus style)."""
    apps_by_bundle = defaultdict(list)
    for app in apps:
        apps_by_bundle[app.bundle_id].append(app)
    
    max_versions = int(config.get('max_versions', 10))
    tint = config.get('tint_color', '5865F2').lstrip('#')
    tint_color = f'#{tint}'  # Official AltStore format uses # prefix
    
    app_entries = []
    for bundle_id, bundle_apps in apps_by_bundle.items():
        bundle_apps.sort(key=lambda x: x.file_date, reverse=True)
        bundle_apps = bundle_apps[:max_versions]
        
        if not bundle_apps:
            continue
        
        primary = bundle_apps[0]
        
        # Build versions
        versions = []
        version_counts = defaultdict(int)
        for app in bundle_apps:
            count = version_counts[app.version]
            version_counts[app.version] += 1
            display_version = app.version if count == 0 else f"{app.version}{chr(ord('a') + count)}"
            
            versions.append({
                "version": display_version,
                "date": app.file_date,
                "localizedDescription": f"Version: {display_version}\nTweaks: {', '.join(app.tweaks)}" if app.tweaks else f"Version {display_version}",
                "downloadURL": app.github_url,
                "size": app.file_size,
            })
        
        description = clean_description("", primary.tweaks)
        subtitle = f"Tweaked with {', '.join(primary.tweaks[:2])}" if primary.tweaks else f"{primary.app_name} for iOS"
        
        app_entries.append({
            "beta": False,
            "name": primary.app_name,
            "bundleIdentifier": bundle_id,
            "developerName": config.get('developer_name', 'TELOS'),
            "subtitle": subtitle,
            "version": primary.version,
            "versionDate": primary.file_date,
            "versionDescription": f"Version: {primary.version}" + (f"\nTweaks: {', '.join(primary.tweaks)}" if primary.tweaks else ""),
            "downloadURL": primary.github_url,
            "localizedDescription": description or f"{primary.app_name} for iOS",
            "iconURL": "",
            "tintColor": tint_color,
            "size": primary.file_size,
            "screenshots": [],
            "appPermissions": {
                "entitlements": primary.entitlements,
                "privacy": primary.privacy,
            },
            "versions": versions,
        })
    
    app_entries.sort(key=lambda x: x['name'].lower())
    featured = [app["bundleIdentifier"] for app in app_entries[:5]]
    news = generate_news(apps, config)
    
    return {
        "name": config.get('source_name', 'TELOS IPA Library'),
        "identifier": config.get('source_id', 'com.telos.library'),
        "subtitle": config.get('source_subtitle', 'Automated IPA Repository'),
        "description": config.get('source_description', 'Welcome to TELOS!'),
        "iconURL": config.get('icon_url', ''),
        "headerURL": config.get('header_url', ''),
        "website": config.get('website', ''),
        "tintColor": tint_color,
        "featuredApps": featured,
        "apps": app_entries,
        "news": news,
    }


def generate_esign_json(apps: list[AppInfo], config: dict) -> dict:
    """Generate Esign format JSON with object keys."""
    esign_data = {}
    tint_color = config.get('tint_color', '5865F2').lstrip('#')
    
    for app in apps:
        name_key = app.app_name.replace(' ', '_').replace('-', '_')
        version_key = app.version.replace('.', '_')
        key = f"{name_key}_{version_key}"
        
        if key in esign_data:
            continue
        
        description = clean_description("", app.tweaks)
        dev_name = f"{app.app_name} {app.version} x {config.get('developer_name', 'TELOS')}"
        
        esign_data[key] = {
            "name": f"{app.app_name} {app.version}",
            "bundleIdentifier": app.bundle_id,
            "developerName": dev_name,
            "version": app.version,
            "versionDate": app.file_date,
            "downloadURL": app.github_url,
            "localizedDescription": description or f"{app.app_name} for iOS",
            "iconURL": "",
            "tintColor": tint_color,
            "size": app.file_size,
            "screenshots": [],
        }
    
    esign_data["features"] = ["IPA signer", "Tweak injector"]
    esign_data["temporal_info"] = {"release_date": datetime.utcnow().strftime('%Y-%m-%d')}
    
    return esign_data


def generate_scarlet_json(apps: list[AppInfo], config: dict) -> dict:
    """Generate Scarlet format JSON with accentColor RGB."""
    seen = {}
    for app in apps:
        if app.bundle_id not in seen:
            seen[app.bundle_id] = app
    
    app_entries = []
    for app in seen.values():
        description = clean_description("", app.tweaks)
        
        app_entries.append({
            "name": app.app_name,
            "bundleIdentifier": app.bundle_id,
            "developerName": config.get('developer_name', 'TELOS'),
            "localizedDescription": description or f"{app.app_name} for iOS",
            "version": app.version,
            "versionDate": app.file_date,
            "versionDescription": f"Version {app.version}",
            "size": app.file_size,
            "iconURL": "",
            "downloadURL": app.github_url,
            "minOSVersion": app.min_ios,
            "supportedPlatforms": ["iOS"],
            "deviceFamilies": app.device_families,
            "metadata": {"sourceType": "telegram", "originalFile": app.file_name},
        })
    
    app_entries.sort(key=lambda x: x['name'].lower())
    
    tint = config.get('tint_color', '5865F2').lstrip('#')
    try:
        r, g, b = int(tint[0:2], 16) / 255.0, int(tint[2:4], 16) / 255.0, int(tint[4:6], 16) / 255.0
    except:
        r, g, b = 0.35, 0.4, 0.95
    
    return {
        "name": config.get('source_name', 'TELOS IPA Library'),
        "identifier": config.get('source_id', 'com.telos.library'),
        "subtitle": config.get('source_subtitle', 'Automated IPA Repository'),
        "description": config.get('source_description', 'Welcome to TELOS!'),
        "version": "1.0.0",
        "versionDate": datetime.utcnow().strftime('%Y-%m-%d'),
        "accentColor": {"red": round(r, 2), "green": round(g, 2), "blue": round(b, 2)},
        "iconURL": config.get('icon_url', ''),
        "localized": {
            "default": {
                "name": config.get('source_name', 'TELOS IPA Library'),
                "subtitle": config.get('source_subtitle', 'Automated IPA Repository'),
                "description": config.get('source_description', 'Welcome to TELOS!'),
            }
        },
        "apps": app_entries,
    }


def generate_feather_json(apps: list[AppInfo], config: dict) -> dict:
    """Generate Feather format JSON - same as store.json without PRIORITY_APPS."""
    return generate_store_json(apps, config)


# =======================
# MAIN
# =======================
def load_config() -> dict:
    """Load configuration from .github/config.yml file."""
    import yaml
    
    config_path = Path('.github/config.yml')
    
    # Default config
    defaults = {
        'source_name': 'TELOS IPA Library',
        'source_id': 'com.telos.library',
        'source_subtitle': 'Automated IPA Repository',
        'source_description': 'Welcome to TELOS!',
        'developer_name': 'TELOS',
        'tint_color': '5865F2',
        'icon_url': '',
        'header_url': '',
        'website': '',
        'priority_apps': '',
        'max_versions': 10,
        'max_screenshots_per_app': 5,
        'min_ios_version_fallback': '12.0',
        'news_url': '',
    }
    
    if config_path.exists():
        print(f"Loading config from {config_path}")
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f) or {}
        
        # Merge file config with defaults
        for key, value in file_config.items():
            if value is not None and value != '':
                defaults[key] = value
    else:
        print(f"Config file not found: {config_path}, using defaults")
    
    return defaults


def main():
    config = load_config()
    
    repo = os.environ.get('GITHUB_REPOSITORY', os.environ.get('GITHUB_REPO', 'user/repo'))
    branch = os.environ.get('GITHUB_REF_NAME', os.environ.get('GITHUB_BRANCH', 'main'))
    github_base_url = f"https://github.com/{repo}/raw/{branch}/IPAs"
    
    ipa_dir = Path('IPAs')
    if not ipa_dir.exists():
        print("No IPAs directory found")
        return
    
    ipas = list(ipa_dir.glob('*.ipa'))
    print(f"Found {len(ipas)} IPA files")
    
    apps = []
    for ipa_path in ipas:
        print(f"Processing: {ipa_path.name}")
        info = extract_ipa_info(ipa_path, github_base_url)
        if info:
            apps.append(info)
            print(f"  -> {info.app_name} v{info.version} ({len(info.tweaks)} tweaks)")
    
    print(f"\nProcessed {len(apps)} apps successfully")
    
    json_dir = Path('JSON')
    json_dir.mkdir(exist_ok=True)
    
    generators = [
        ('store.json', generate_store_json),
        ('esign.json', generate_esign_json),
        ('scarlet.json', generate_scarlet_json),
        ('feather.json', generate_feather_json),
    ]
    
    for filename, generator in generators:
        data = generator(apps, config)
        output_path = json_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Generated: {filename}")
    
    print("\nJSON generation complete!")


if __name__ == '__main__':
    main()
