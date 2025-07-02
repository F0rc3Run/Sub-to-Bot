import os
import requests
import base64
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

CONFIG_DIR = "configs"

def get_txt_files_from_repo(owner, repo, token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/sub"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    print(f"[INFO] Fetching file list from: {url}")
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        print(f"[ERROR] Cannot access {owner}/{repo}/sub - Status: {r.status_code}")
        return []

    try:
        data = r.json()
    except Exception as e:
        print(f"[ERROR] JSON parse error in {owner}/{repo}/sub: {e}")
        return []

    if not isinstance(data, list):
        print(f"[ERROR] Unexpected data format for {owner}/{repo}/sub")
        return []

    txt_files = [item['download_url'] for item in data if item.get('type') == 'file' and item.get('name', '').endswith('.txt')]
    print(f"[INFO] Found {len(txt_files)} txt files in {owner}/{repo}/sub")
    return txt_files

def fetch_file_lines(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text.splitlines()
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return []

def main():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    repos = os.getenv("VPN_REPOS", "").splitlines()
    token = os.getenv("GITHUB_TOKEN")

    all_lines = []

    for repo_full in repos:
        repo_full = repo_full.strip()
        if not repo_full or "/" not in repo_full:
            continue
        owner, repo = repo_full.split("/", 1)
        txt_urls = get_txt_files_from_repo(owner, repo, token)
        for url in txt_urls:
            lines = fetch_file_lines(url)
            all_lines.extend(lines)

    print(f"[INFO] Total lines fetched before filtering: {len(all_lines)}")

    # فیلتر و دسته‌بندی خطوط بر اساس پروتکل
    configs = {p: [] for p in PROTOCOLS}

    for line in all_lines:
        line = line.strip()
        for proto, prefix in PROTOCOLS.items():
            if line.startswith(prefix):
                configs[proto].append(line)
                break

    # محدود کردن تعداد سرورها: حداقل 200، حداکثر 1000
    for proto in configs:
        servers = list(set(configs[proto]))  # حذف تکراری
        count = len(servers)
        if count < 200:
            print(f"[WARN] پروتکل {proto} تعداد سرور کافی ندارد: {count}")
        elif count > 1000:
            servers = random.sample(servers, 1000)
            print(f"[INFO] پروتکل {proto} تعداد سرورها کاهش داده شد به 1000 (از {count})")
        else:
            print(f"[INFO] پروتکل {proto} تعداد سرورها: {count}")
        configs[proto] = servers

    # ذخیره در فایل‌ها
    for proto, servers in configs.items():
        filepath = os.path.join(CONFIG_DIR, f"{proto}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(servers))
        print(f"[INFO] فایل {filepath} با {len(servers)} سرور به‌روزرسانی شد.")

if __name__ == "__main__":
    main()
