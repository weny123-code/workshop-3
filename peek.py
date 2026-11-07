# peek.py — 快速查看下载的数据文件
# 用法: python peek.py "D:\path\to\your_file.txt"
import os, sys
import pandas as pd

path = sys.argv[1] if len(sys.argv) > 1 else r"D:\workshop.script\data\raw\your_file.txt"
print("=" * 60)
print("file :", path)
print("size :", round(os.path.getsize(path) / 1024 / 1024, 1), "MB")

with open(path, "rb") as f:
    head = f.read(16)
if head[:2] == b"PK":
    kind = "zip"
elif head[:3] == b"BZh":
    kind = "bz2"
elif head[:2] == b"\x1f\x8b":
    kind = "gzip"
elif head[:8] == b"\x89HDF\r\n\x1a\n":
    kind = "hdf5"
else:
    kind = "text"
print("type :", kind)

if kind in ("zip", "bz2", "gzip"):
    print("这是压缩文件，先解压：tar -xf 文件 或 用 7-Zip")
    sys.exit()
if kind == "hdf5":
    import h5py
    with h5py.File(path, "r") as f:
        print("HDF5 keys:", list(f.keys()))
        def show(name, obj):
            if isinstance(obj, h5py.Dataset):
                print(f"  {name}: shape={obj.shape}, dtype={obj.dtype}")
        f.visititems(show)
    sys.exit()

# 文本：先看原始前 10 行
df = pd.read_csv(path, sep="\t", header=None, nrows=10)
print("\n--- 前 10 行（原始） ---")
print(df.to_string())
print("\n列数:", df.shape[1])