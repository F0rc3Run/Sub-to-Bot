import os
import base64
import requests
import random
import time

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

# این تابع با GitHub API فایل‌های txt داخل پوشه sub رو پیدا میکنه (بازگشتی)
def get_txt_files_from_repo(owner, repo, path="sub"):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=headers)
    files = []
    if resp.status_code == 200:
        items = resp.json()
        for item in items:
            if item['type'] == 'file' and item['name'].endswith('.txt'):
                files.append(item['download_url'])
            elif item['type'] == 'dir':
                files.extend(get_txt_files_from_repo(owner, repo, item['path']))
    else:
        print(f"[ERROR] Cannot access {owner}/{repo}/{path} - Status: {resp.status_code}")
    return files

def fetch_and_decode(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        # فایل ها معمولا base64 نیستند، مستقیم استفاده میکنیم
        return r.text.strip().splitlines()
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return []

def main():
    repos = os.getenv("VPN_REPOS", "")
    if not repos:
        print("[ERROR] No repositories provided in VPN_REPOS env variable.")
        return

    repos_list = [r.strip().split('/') for r in repos.strip().splitlines()]
    # ساختار هر خط: owner/repo

    all_sources = []

    print(f"[INFO] Loading repos: {repos_list}")
    for owner_repo in repos_list:
        if len(owner_repo) != 2:
            print(f"[WARN] Invalid repo format: {'/'.join(owner_repo)}")
            continue
        owner, repo = owner_repo
        sources = get_txt_files_from_repo(owner, repo)
        print(f"[INFO] Found {len(sources)} sources in {owner}/{repo}")
        all_sources.extend(sources)

    # هر ۱۲ ساعت رندوم انتخاب کن (مثلا همه رو برای تنوع بگیریم)
    random.shuffle(all_sources)

    # پاک کردن قبلی ها
    for proto in PROTOCOLS:
        configs[proto] = []

    # بارگذاری و دسته‌بندی
    for src in all_sources:
        lines = fetch_and_decode(src)
        for line in lines:
            for proto, prefix in PROTOCOLS.items():
                if line.startswith(prefix):
                    configs[proto].append(line)
                    break

    # فیلتر حداقل 200 تا و حداکثر 1000 تا سرور برای هر پروتکل
    for proto in configs:
        servers = configs[proto]
        if len(servers) < 200:
            print(f"[WARN] پروتکل {proto} تعداد سرور کافی ندارد: {len(servers)}")
        if len(servers) > 1000:
            servers = random.sample(servers, 1000)
        configs[proto] = servers

    # ذخیره فایل‌ها
    os.makedirs("configs", exist_ok=True)
    os.makedirs("configs/subs", exist_ok=True)

    for proto, items in configs.items():
        with open(f"configs/{proto}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(items))
        if items:
            sub = base64.b64encode("\n".join(items).encode()).decode()
            with open(f"configs/subs/{proto}_sub.txt", "w", encoding="utf-8") as f:
                f.write(f"sub://{sub}")

    print("[INFO] Finished updating config files.")

if __name__ == "__main__":
    main()
