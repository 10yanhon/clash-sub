import requests
import base64
import yaml
import os

# ✅ 真实的免费订阅源（目前稳定可用）
SUB_LINKS = [
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray"
]
# ✅ 限定地区关键词（用于优选）
KEYWORDS = ['台湾', 'Hong', 'HK', 'Japan', 'JP', '美国', 'US', 'UK', 'France', 'Germany', 'Europe', 'Norway', 'Sweden']

# ✅ 最多保留节点数
MAX_NODES = 10

def fetch_sub_content():
    all_nodes = []
    for url in SUB_LINKS:
        try:
            print(f"获取订阅：{url}")
            res = requests.get(url, timeout=10)
            content = base64.b64decode(res.text + '===').decode('utf-8')
            all_nodes += [line.strip() for line in content.splitlines() if line.strip()]
        except Exception as e:
            print(f"❌ 订阅源错误: {url} -> {e}")
    return all_nodes

def filter_nodes(nodes):
    filtered = []
    for node in nodes:
        decoded = base64.b64decode(node.split('//')[1] + '===').decode('utf-8', errors='ignore')
        if any(k in decoded for k in KEYWORDS):
            filtered.append(node)
        if len(filtered) >= MAX_NODES:
            break
    return filtered

def write_base64_txt(nodes, path):
    txt = '\n'.join(nodes)
    encoded = base64.b64encode(txt.encode('utf-8')).decode('utf-8')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(encoded)

def write_clash_yaml(nodes, path):
    proxies = []
    proxy_names = []
    for i, node in enumerate(nodes):
        name = f"proxy{i+1}"
        proxy_names.append(name)
        if node.startswith('vmess://'):
            try:
                config = base64.b64decode(node[8:] + '===').decode('utf-8')
                vmess = yaml.safe_load(config)
                proxies.append({
                    "name": name,
                    "type": "vmess",
                    "server": vmess['add'],
                    "port": int(vmess['port']),
                    "uuid": vmess['id'],
                    "alterId": int(vmess.get('aid', 0)),
                    "cipher": vmess.get('cipher', 'auto'),
                    "tls": vmess.get('tls', 'false') == 'tls',
                    "network": vmess.get('net', 'tcp'),
                    "ws-opts": {
                        "path": vmess.get('path', ''),
                        "headers": {
                            "Host": vmess.get('host', '')
                        }
                    } if vmess.get('net') == 'ws' else {}
                })
            except Exception:
                continue

    clash_config = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": True,
        "mode": "Rule",
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": "Auto",
                "type": "url-test",
                "proxies": proxy_names,
                "url": "http://www.gstatic.com/generate_204",
                "interval": 300
            }
        ],
        "rules": [
            "MATCH,Auto"
        ]
    }

    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(clash_config, f, allow_unicode=True)

def main():
    os.makedirs('docs', exist_ok=True)

    all_nodes = fetch_sub_content()
    if not all_nodes:
        print("❌ 没有获取到节点")
        return

    filtered = filter_nodes(all_nodes)
    if not filtered:
        print("❌ 没有符合地区要求的节点")
        return

    # 写入文件
    write_base64_txt(filtered, 'docs/v2ray.txt')
    write_base64_txt(filtered, 'docs/v2ray64.txt')
    write_clash_yaml(filtered, 'docs/clash.yaml')

    print("✅ 节点文件已生成：docs/v2ray.txt, v2ray64.txt, clash.yaml")

if __name__ == '__main__':
    main()
