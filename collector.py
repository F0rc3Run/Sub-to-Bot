import requests

def get_txt_files_from_repo(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/sub"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        # اگر نیاز به توکن داری اینجا اضافه کن:
        # "Authorization": f"token {GITHUB_TOKEN}"
    }
    r = requests.get(url, headers=headers, timeout=10)

    if r.status_code != 200:
        print(f"Error: Cannot access {owner}/{repo}/sub - Status: {r.status_code}")
        return []

    try:
        data = r.json()
    except Exception as e:
        print(f"Error parsing JSON from {owner}/{repo}/sub: {e}")
        return []

    # اطمینان حاصل کن data یک لیست هست
    if not isinstance(data, list):
        print(f"Unexpected data format for {owner}/{repo}/sub")
        return []

    txt_files = [item['download_url'] for item in data if item.get('type') == 'file' and item.get('name', '').endswith('.txt')]
    return txt_files
