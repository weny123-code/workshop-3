# inspect_milan.py — 统计 + 显示 Milan 一天数据
# 用法: python inspect_milan.py "D:\path\to\file.txt"
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

path = sys.argv[1] if len(sys.argv) > 1 else r"D:\workshop.script\data\raw\your_file.txt"
ncols = pd.read_csv(path, sep="\t", header=None, nrows=1).shape[1]
idx_sq, idx_t, idx_y = 0, 1, 6 if ncols >= 7 else ncols - 1

rows = 0
squares = set()
t_min, t_max = None, None
total_y = 0.0
zeros = 0
missing = 0
hourly = {}
sq_sum = {}

for chunk in pd.read_csv(path, sep="\t", header=None, chunksize=500_000):
    sq = pd.to_numeric(chunk.iloc[:, idx_sq], errors="coerce")
    tt = pd.to_numeric(chunk.iloc[:, idx_t], errors="coerce")
    y = pd.to_numeric(chunk.iloc[:, idx_y], errors="coerce")

    rows += len(chunk)
    missing += int(y.isna().sum())
    zeros += int((y == 0).sum())
    total_y += float(y.sum())
    squares.update(sq.dropna().astype(int).unique().tolist())

    ts = pd.to_datetime(tt, unit="ms", errors="coerce")
    t_min = ts.min() if t_min is None else min(t_min, ts.min())
    t_max = ts.max() if t_max is None else max(t_max, ts.max())

    h = y.groupby(ts.dt.floor("h")).sum()
    for k, v in h.items():
        hourly[k] = hourly.get(k, 0.0) + float(v)

    g = y.groupby(sq).sum()
    for k, v in g.items():
        sq_sum[k] = sq_sum.get(k, 0.0) + float(v)

print("rows      :", rows)
print("columns   :", ncols)
print("squares   :", len(squares))
print("time range:", t_min, "→", t_max)
print("internet  : total=%.2f, zero=%.2f%%, missing=%.2f%%" % (
    total_y, 100 * zeros / max(rows, 1), 100 * missing / max(rows, 1)))

# 每小时总流量
hs = pd.Series(hourly).sort_index()
print("\n--- 每小时总流量（前 5 行） ---")
print(hs.head())

# 总流量 top 10 网格
top = pd.Series(sq_sum).sort_values(ascending=False).head(10)
print("\n--- 总流量 Top 10 网格 ---")
print(top)

# 画图：左=每小时总量，右=Top10 网格
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
hs.plot(ax=axes[0], marker="o")
axes[0].set_title("Total internet activity per hour")
axes[0].set_xlabel("hour")
axes[0].set_ylabel("activity (CDR count)")

top.sort_values().plot(kind="barh", ax=axes[1])
axes[1].set_title("Top 10 grids by total activity")
axes[1].set_xlabel("activity (CDR count)")

plt.tight_layout()
plt.show()   # 如果在 VS Code/终端弹不出图，把这里改成 plt.savefig("data_preview.png")