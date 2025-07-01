import requests
import base64
import socket
import time

INPUT_FILE = "private_subs.txt"
OUTPUT_FILE = "filtered_shadowsocks.txt"
MAX_LATENCY_MS = 500
TIMEOUT = 2

def tcp_ping(host, port, timeout=TIMEOUT):
    try:
        start = time.time()
        with socket.create_connection((host, int(port)), timeout=timeout):
            return (time.time() - start) * 1000
    except:
        return None

def decode_ss_line(line):
    if not line.startswith("ss://"):
        return None, None
    raw = line[5:]
    try:
        if '#' in raw:
            raw = raw.split('#')[0]
        decoded = base64.b64decode(raw + '=' * (-len(raw) % 4)).decode()
        if '@' not in decoded:
            return None, None
        server = decoded.split('@')[1]
        host, port = server.split(':')
        return host, port
    except:
        return None, None

def main():
    try:
        with open(INPUT_FILE, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ فایل {INPUT_FILE} پیدا نشد.")
        return

    good_servers = []

    for url in urls:
        print(f"📥 بررسی: {url}")
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                print(f"❌ خطا در دریافت: {r.status_code}")
                continue
            if "://" not in r.text:
                decoded = base64.b64decode(r.text.strip() + '=' * (-len(r.text.strip()) % 4)).decode()
                lines = decoded.strip().splitlines()
            else:
                lines = r.text.strip().splitlines()
        except Exception as e:
            print(f"❌ خطا: {e}")
            continue

        for line in lines:
            line = line.strip()
            if not line.startswith("ss://"):
                continue
            host, port = decode_ss_line(line)
            if not host:
                continue
            print(f"⏳ پینگ {host}:{port} ... ", end='')
            latency = tcp_ping(host, port)
            if latency is not None and latency < MAX_LATENCY_MS:
                print(f"✅ ({int(latency)}ms)")
                good_servers.append(line)
            else:
                print("❌")

    if good_servers:
        with open(OUTPUT_FILE, 'w') as f:
            for s in good_servers:
                f.write(s + '\n')
        print(f"\n✅ {len(good_servers)} سرور سالم ذخیره شد در {OUTPUT_FILE}")
    else:
        print("\n⚠️ هیچ سرور سریعی یافت نشد.")

if __name__ == "__main__":
    main()
