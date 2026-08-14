import datetime
import hashlib

def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_text(filename, text):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)

        print("保存成功")

    except Exception as e:
        print("保存失败:", e)

def generate_id(url: str) -> str:
    return hashlib.md5(
        url.strip().encode("utf-8")
    ).hexdigest()