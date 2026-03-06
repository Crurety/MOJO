import sys
import py_compile

files = [
    r"d:\Project\PycharmProjects\toolsProject\backend\app\core\exceptions.py",
    r"d:\Project\PycharmProjects\toolsProject\backend\app\payment\alipay.py",
    r"d:\Project\PycharmProjects\toolsProject\backend\app\payment\wechat.py"
]

for file in files:
    try:
        py_compile.compile(file, doraise=True)
        print(f"OK: {file}")
    except Exception as e:
        print(f"ERROR: {file}\n{e}")
        sys.exit(1)
