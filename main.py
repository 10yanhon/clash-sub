import base64
import json
import os
import re
import requests
import yaml
from urllib.parse import unquote

SUB_LINKS = [
   "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
   "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
   "https://raw.githubusercontent.com/freefq/free/master/v2",
   "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
   "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray"
]

TARGET_LOCATIONS = ["日本", "韩国", "香港", "台湾", "新加坡", "美国", "英国", "德国", "法国", "芬兰", "瑞典", "荷兰"]

OUTPUT_DIR = "docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_subscription(link):
   try:
       print(f"获取订阅：{link}")
       res = requests.get(link, timeout=10)
       if res.status_code == 200:
           content = res.text.strip()
           if not content.startswith("vmess://") and not content.startswith("ss://") and not content.startswith("trojan://"):
               content = base64.b64decode(content + "=" * (-len(content) % 4)).decode("utf-8", errors="ignore")
           return content.splitlines()
   except Exception as e:
       print(f" 订阅源错误: {link} -> {e}")
   return []

def filter_nodes(nodes):
   filtered = []
   for node in nodes:
       node = node.strip()
       if not node or not any(node.startswith(prefix) for prefix in ["vmess://", "ss://", "trojan://"]):
           continue
       node_lc = node.lower()
       if any(keyword in node_lc for keyword in ["剩余流量", "过期", "时间", "expire"]):
           continue
       if any(loc in node for loc in TARGET_LOCATIONS):
           try:
               if node.startswith("vmess://"):
                   decoded = base64.b64decode(node[8:] + '=' * (-len(node[8:]) % 4)).decode('utf-8', errors='ignore')
                   json.loads(decoded)
               filtered.append(node)
           except:
               continue
   return filtered

def to_clash_yaml(nodes):
   proxies = []
   for node in nodes:
       if node.startswith("vmess://"):
           try:
               vmess_conf = base64.b64decode(node[8:] + '=' * (-len(node[8:]) % 4)).decode("utf-8", errors="ignore")
               vmess_json = json.loads(vmess_conf)
               proxies.append({
                   "name": vmess_json.get("ps", "Unnamed"),
                   "type": "vmess",
                   "server": vmess_json["add"],
                   "port": int(vmess_json["port"]),
                   "uuid": vmess_json["id"],
                   "alterId": int(vmess_json.get("aid", 0)),
                   "cipher": "auto",
                   "tls": vmess_json.get("tls", "") == "tls",
                   "network": vmess_json.get("net", "tcp"),
                   "ws-opts": {
                       "path": vmess_json.get("path", ""),
                       "headers": {
                           "Host": vmess_json.get("host", "")
                       }
                   } if vmess_json.get("net") == "ws" else None
               })
           except Exception as e:
               print("️ 跳过无效 vmess：", e)
       elif node.startswith("ss://"):
           try:
               ss = node[5:]
               if "#" in ss:
                   ss, name = ss.split("#", 1)
                   name = unquote(name)
               else:
                   name = "ss"

               decoded = base64.b64decode(ss.split('@')[0] + "=" * (-len(ss.split('@')[0]) % 4)).decode()
               method, password = decoded.split(":", 1)
               server_port = ss.split('@')[1]
               server, port = server_port.split(":")
               proxies.append({
                   "name": name,
                   "type": "ss",
                   "server": server,
                   "port": int(port),
                   "cipher": method,
                   "password": password
               })
           except Exception as e:
               print("️ 跳过无效 ss：", e)

   clash_config = {
       "proxies": proxies,
       "proxy-groups": [
           {
               "name": " 节点选择",
               "type": "select",
               "proxies": [p["name"] for p in proxies]
           }
       ],
       "rules": [
           "MATCH, 节点选择"
       ]
   }

   return yaml.dump(clash_config, allow_unicode=True)

def save_file(filename, content):
   with open(filename, "w", encoding="utf-8") as f:
       f.write(content)

def main():
   all_nodes = []
   for url in SUB_LINKS:
       all_nodes.extend(fetch_subscription(url))

   filtered = filter_nodes(all_nodes)
   final_nodes = filtered[:10]  # 保留前10个

   # v2ray.txt
   save_file(os.path.join(OUTPUT_DIR, "v2ray.txt"), " ".join(final_nodes))
   # v2ray64.txt（base64）
   save_file(os.path.join(OUTPUT_DIR, "v2ray64.txt"), base64.b64encode(" ".join(final_nodes).encode()).decode())
   # clash.yaml
   save_file(os.path.join(OUTPUT_DIR, "clash.yaml"), to_clash_yaml(final_nodes))

if __name__ == "__main__":
   main()
