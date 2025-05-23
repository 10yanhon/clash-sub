import os

def generate_files():
    os.makedirs("docs", exist_ok=True)
    with open("docs/v2ray.txt", "w") as f:
        f.write("这里是 v2ray.txt 示例内容")
    with open("docs/v2ray64.txt", "w") as f:
        f.write("这里是 v2ray64.txt 示例内容")
    with open("docs/clash.yaml", "w") as f:
        f.write("这里是 clash.yaml 示例内容")
    with open("docs/index.html", "w") as f:
        f.write("<html><body><h1>Clash Subscriptions</h1></body></html>")

if __name__ == "__main__":
    generate_files()
