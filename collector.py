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
    # خواندن منابع از متغیر محیطی و فیلتر لینک‌های معتبر
    return [line.strip() for line in os.getenv("VPN_SOURCES", "").splitlines() if line.strip().startswith("http")]

def fetch_list(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        # فرض می‌کنیم فایل‌ها base64 نیستند، فقط یک سرور در هر خط
        # اگر base64 بود، خط زیر را جایگزین کن:
        # return base64.b64decode(r.text.strip()).decode().splitlines()
        return r.text.strip().splitlines()
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return []

def main():
    configs = {p: [] for p in PROTOCOLS}

    sources = load_sources()
    # نمونه‌گیری تصادفی 4 منبع یا کمتر اگر کمتر باشد
    chosen_sources = random.sample(sources, min(len(sources), 4))

    for src in chosen_sources:
        lines = fetch_list(src)
        for line in lines:
            for proto, prefix in PROTOCOLS.items():
                if line.startswith(prefix):
                    configs[proto].append(line)
                    break

    for proto, items in configs.items():
        unique_items = list(set(items))
        if len(unique_items) < MIN_SERVERS:
            print(f"[WARN] پروتکل {proto} تعداد سرور کافی ندارد: {len(unique_items)}")
        selected = random.sample(unique_items, min(len(unique_items), MAX_SERVERS))
        path = SUB_FILES.get(proto)
        if path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write("\n".join(selected))
            print(f"[INFO] فایل {path} با {len(selected)} سرور به‌روزرسانی شد.")

if __name__ == "__main__":
    main()
