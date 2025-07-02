import os
import base64
import requests
import random

PROTOCOLS = {
    'vmess': 'vmess://',
    'vless': 'vless://',
    'trojan': 'trojan://',
    'shadowsocks': 'ss://',
    'hysteria': 'hysteria://',
    'hysteria2': 'hysteria2://',
    'reality': 'reality://',
    'tuic': 'tuic://',
    'ssh': 'ssh://'
}

SUB_FILES = {
    'vmess': 'configs/vmess.txt',
    'vless': 'configs/vless.txt',
    'trojan': 'configs/trojan.txt',
    'shadowsocks': 'configs/shadowsocks.txt',
    'hysteria': 'configs/hysteria.txt',
    'hysteria2': 'configs/hysteria2.txt',
    'reality': 'configs/reality.txt',
    'tuic': 'configs/tuic.txt',
    'ssh': 'configs/ssh.txt'
}

MIN_SERVERS = 200
MAX_SERVERS = 1000

def load_sources():
    sources = [line.strip() for line in os.getenv("VPN_SOURCES", "").splitlines() if line.strip().startswith("http")]
    print(f"[INFO] Loaded {len(sources)} sources.")
    return sources

def fetch_list(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        # فرض بر این که فایل متنی ساده است
        lines = r.text.strip().splitlines()
        print(f"[INFO] Fetched {len(lines)} lines from {url}")
        return lines
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return []

def main():
    configs = {p: [] for p in PROTOCOLS}

    sources = load_sources()
    if not sources:
        print("[ERROR] No sources found in VPN_SOURCES env variable!")
        return

    chosen_sources = random.sample(sources, min(len(sources), 4))
    print(f"[INFO] Selected sources: {chosen_sources}")

    for src in chosen_sources:
        lines = fetch_list(src)
        for line in lines:
            for proto, prefix in PROTOCOLS.items():
                if line.startswith(prefix):
                    configs[proto].append(line)
                    break

    # ساخت پوشه configs اگر موجود نیست
    for path in SUB_FILES.values():
        os.makedirs(os.path.dirname(path), exist_ok=True)

    for proto, items in configs.items():
        unique_items = list(set(items))
        count = len(unique_items)
        if count < MIN_SERVERS:
            print(f"[WARN] پروتکل {proto} تعداد سرور کافی ندارد: {count}")
        selected = random.sample(unique_items, min(count, MAX_SERVERS))
        path = SUB_FILES.get(proto)
        if path:
            with open(path, "w") as f:
                f.write("\n".join(selected))
            print(f"[INFO] فایل {path} با {len(selected)} سرور به‌روزرسانی شد.")

if __name__ == "__main__":
    main()
