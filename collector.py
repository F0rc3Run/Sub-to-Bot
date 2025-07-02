import os, base64, requests

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

configs = {p: [] for p in PROTOCOLS}

def load_sources():
    return [line.strip() for line in os.getenv("VPN_SOURCES", "").splitlines() if line.strip().startswith("http")]

def fetch_and_decode(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return base64.b64decode(r.text.strip()).decode().splitlines()
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return []

os.makedirs("configs/subs", exist_ok=True)

for src in load_sources():
    for line in fetch_and_decode(src):
        for proto, prefix in PROTOCOLS.items():
            if line.startswith(prefix):
                configs[proto].append(line)
                break

for proto, items in configs.items():
    with open(f"configs/{proto}.txt", "w") as f:
        f.write("\n".join(items))
    if items:
        sub = base64.b64encode("\n".join(items).encode()).decode()
        with open(f"configs/subs/{proto}_sub.txt", "w") as f:
            f.write(f"sub://{sub}")
