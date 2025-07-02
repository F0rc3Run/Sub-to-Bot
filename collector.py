import requests
import base64
import os

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

def find_sub_folder(owner, repo):
    url_root = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    try:
        r = requests.get(url_root, timeout=10)
        r.raise_for_status()
        items = r.json()
        # چک میکنیم فولدر ریشه فایل txt داره یا نه
        for item in items:
            if item['type'] == 'file' and item['name'].endswith('.txt'):
                return ''  # فولدر ریشه است
        # اگر فولدر داشتیم داخل هر فولدر رو چک میکنیم
        for item in items:
            if item['type'] == 'dir':
                url_sub = f"{url_root}{item['name']}"
                r2 = requests.get(url_sub, timeout=10)
                r2.raise_for_status()
                sub_items = r2.json()
                for sub_item in sub_items:
                    if sub_item['type'] == 'file' and sub_item['name'].endswith('.txt'):
                        return item['name']
        return None
    except Exception as e:
        print(f"[ERROR] Cannot access {owner}/{repo} root: {e}")
        return None

def get_txt_files_from_repo(owner, repo):
    folder = find_sub_folder(owner, repo)
    if folder is None:
        print(f"[WARN] No folder with txt files found in {owner}/{repo}")
        return []

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}" if folder else f"https://api.github.com/repos/{owner}/{repo}/contents/"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        items = r.json()
        txt_files = [item for item in items if item['type'] == 'file' and item['name'].endswith('.txt')]
        return txt_files
    except Exception as e:
        print(f"[ERROR] Cannot access {owner}/{repo}/{folder}: {e}")
        return []

def fetch_file_content(download_url):
    try:
        r = requests.get(download_url, timeout=10)
        r.raise_for_status()
        return r.text.splitlines()
    except Exception as e:
        print(f"[ERROR] Cannot fetch file content from {download_url}: {e}")
        return []

def main():
    repos = os.getenv("VPN_REPOS", "").splitlines()
    print(f"[INFO] Loaded {len(repos)} repos.")
    for repo_line in repos:
        repo_line = repo_line.strip()
        if not repo_line or '/' not in repo_line:
            continue
        owner, repo = repo_line.split('/', 1)
        print(f"[INFO] Processing {owner}/{repo}")
        txt_files = get_txt_files_from_repo(owner, repo)
        if not txt_files:
            continue
        for txt_file in txt_files:
            lines = fetch_file_content(txt_file['download_url'])
            for line in lines:
                for proto, prefix in PROTOCOLS.items():
                    if line.startswith(prefix):
                        configs[proto].append(line)
                        break

    # حداقل و حداکثر 200 تا 1000 سرور هر پروتکل
    import random
    for proto, lines in configs.items():
        unique_lines = list(set(lines))
        count = max(200, min(len(unique_lines), 1000))
        selected = random.sample(unique_lines, count) if len(unique_lines) >= count else unique_lines

        os.makedirs("configs", exist_ok=True)
        file_path = f"configs/{proto}.txt"
        with open(file_path, "w") as f:
            f.write("\n".join(selected))
        print(f"[INFO] فایل {file_path} با {len(selected)} سرور به‌روزرسانی شد.")

if __name__ == "__main__":
    main()
