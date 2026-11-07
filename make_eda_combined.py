# -*- coding: utf-8 -*-
"""Generic one-file EDA for Milan daily data: internet + call-out + concentration + full table.

Usage:
    python make_eda_combined.py "C:\\path\\sms-call-internet-mi-2013-11-02.txt"
    # no argument -> use the default 2013-11-01 file

Output: eda_combined_<YYYY-MM-DD>.png / .pdf
"""
import os
import re
import sys
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

DEFAULT_PATH = r"C:\Users\20902\Downloads\sms-call-internet-mi-2013-11-01.txt"
PATH = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
HERE = os.path.dirname(os.path.abspath(__file__))

NAMES = ["square_id", "time_interval", "country_code",
         "sms_in", "sms_out", "call_in", "call_out", "internet"]

print("reading:", PATH)
df = pd.read_csv(PATH, sep="\t", header=None, names=NAMES, usecols=[0, 1, 2, 6, 7])
print("raw rows:", len(df), "| unique squares:", df["square_id"].nunique())
panel = (df.groupby(["square_id", "time_interval"], as_index=False)
           .agg(call_out=("call_out", "sum"), internet=("internet", "sum")))
panel["dt"] = (pd.to_datetime(panel["time_interval"], unit="ms", utc=True)
               .dt.tz_convert("Europe/Rome"))
hourly_all = (panel.set_index("dt")[["internet", "call_out"]]
              .resample("h").sum().sort_index())

m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(PATH))
target_date = pd.Timestamp(m.group(1)).date() if m else hourly_all.index.date[0]
DATE_STR = str(target_date)
hourly = hourly_all[hourly_all.index.date == target_date]
print("date:", DATE_STR, "| hours:", len(hourly))

OUT = os.path.join(HERE, f"eda_combined_{DATE_STR}.png")
OUT_PDF = os.path.join(HERE, f"eda_combined_{DATE_STR}.pdf")

hours = np.arange(len(hourly))
xlabels = [f"{h:02d}" for h in hours]
inet = hourly["internet"].values
call = hourly["call_out"].values
inet_n = inet / inet.max()
call_n = call / call.max()

inet_min_i, inet_max_i = int(inet.argmin()), int(inet.argmax())
call_min_i, call_max_i = int(call.argmin()), int(call.argmax())
call_2nd_i = int(np.argsort(call)[-2])

fig = plt.figure(figsize=(19, 17.2), dpi=150)
gs = GridSpec(5, 1, height_ratios=[2.4, 2.4, 2.4, 2.5, 1.9], hspace=0.72,
              left=0.065, right=0.985, top=0.935, bottom=0.025)

# ---------------- A. Internet ----------------
ax = fig.add_subplot(gs[0])
ax.plot(hours, inet / 1e6, color="#1F4E79", lw=2.0, marker="o", ms=6,
        mfc="white", mew=1.6, label="internet")
ax.set_xticks(hours)
ax.set_xticklabels(xlabels, fontsize=8)
ax.set_xlim(-0.5, 23.5)
ax.set_ylim(min(inet) / 1e6 * 0.85, max(inet) / 1e6 * 1.26)
ax.set_ylabel("internet 活动量（×10⁶, scaled）", fontsize=10)
ax.set_title(f"A. Internet 活动量：逐小时（{DATE_STR}，米兰当地时区）", fontsize=12, loc="left", fontweight="bold")
ax.grid(axis="y", ls="--", alpha=0.35)
ax.legend(loc="lower right", fontsize=9)

bbox_w = dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.82)
ax.annotate(f"最低 {inet_min_i:02d}:00\n{inet[inet_min_i]/1e6:.2f}×10⁶",
            xy=(inet_min_i, inet[inet_min_i] / 1e6), xytext=(1.2, min(inet) / 1e6 * 0.91),
            fontsize=9, color="#B00000", bbox=bbox_w,
            arrowprops=dict(arrowstyle="->", color="#B00000", lw=1.2))
ax.annotate(f"峰值 {inet_max_i:02d}:00\n{inet[inet_max_i]/1e6:.2f}×10⁶",
            xy=(inet_max_i, inet[inet_max_i] / 1e6), xytext=(13.0, max(inet) / 1e6 * 1.15),
            fontsize=9, color="#1F4E79", bbox=bbox_w,
            arrowprops=dict(arrowstyle="->", color="#1F4E79", lw=1.2))
ax.annotate("10:00–17:00 高位平台", xy=(13.5, inet[13] / 1e6),
            xytext=(9.6, max(inet) / 1e6 * 1.00), fontsize=9, color="#555555", bbox=bbox_w)

# ---------------- B. Call-out ----------------
ax = fig.add_subplot(gs[1])
ax.plot(hours, call / 1e3, color="#C55A11", lw=2.0, marker="s", ms=6,
        mfc="white", mew=1.6, label="call-out")
ax.set_xticks(hours)
ax.set_xticklabels(xlabels, fontsize=8)
ax.set_xlim(-0.5, 23.5)
ax.set_ylim(min(call) / 1e3 * 0.80, max(call) / 1e3 * 1.28)
ax.set_ylabel("call-out 活动量（×10³, scaled）", fontsize=10)
ax.set_title(f"B. Call-out 活动量：逐小时（{DATE_STR}，同一时区）", fontsize=12, loc="left", fontweight="bold")
ax.grid(axis="y", ls="--", alpha=0.35)
ax.legend(loc="upper right", fontsize=9)

ax.annotate(f"最低 {call_min_i:02d}:00\n{call[call_min_i]/1e3:.1f}×10³",
            xy=(call_min_i, call[call_min_i] / 1e3), xytext=(1.2, min(call) / 1e3 * 0.86),
            fontsize=9, color="#B00000", bbox=bbox_w,
            arrowprops=dict(arrowstyle="->", color="#B00000", lw=1.2))
ax.annotate(f"主峰 {call_max_i:02d}:00\n{call[call_max_i]/1e3:.1f}×10³",
            xy=(call_max_i, call[call_max_i] / 1e3), xytext=(4.8, max(call) / 1e3 * 1.18),
            fontsize=9, color="#C55A11", bbox=bbox_w,
            arrowprops=dict(arrowstyle="->", color="#C55A11", lw=1.2))
ax.annotate(f"次峰 {call_2nd_i:02d}:00\n{call[call_2nd_i]/1e3:.1f}×10³",
            xy=(call_2nd_i, call[call_2nd_i] / 1e3), xytext=(15.0, max(call) / 1e3 * 1.05),
            fontsize=9, color="#C55A11", bbox=bbox_w,
            arrowprops=dict(arrowstyle="->", color="#C55A11", lw=1.2))

# ---------------- C. Compare ----------------
ax = fig.add_subplot(gs[2])
ax.plot(hours, inet_n, color="#1F4E79", lw=2.2, marker="o", ms=6, label="internet（归一化）")
ax.plot(hours, call_n, color="#C55A11", lw=2.2, marker="s", ms=6, label="call-out（归一化）")
ax.set_xticks(hours)
ax.set_xticklabels(xlabels, fontsize=8)
ax.set_xlim(-0.5, 23.5)
ax.set_ylim(0, 1.30)
ax.set_ylabel("归一化到各自日峰值", fontsize=10)
ax.set_title(f"C. 形态对比：internet 平缓；call-out 双峰（主峰 {call_max_i:02d}:00、次峰 {call_2nd_i:02d}:00）", fontsize=12, loc="left", fontweight="bold")
ax.grid(axis="y", ls="--", alpha=0.35)
ax.legend(loc="lower right", fontsize=9)

ax.annotate(f"internet 峰值 {inet_max_i:02d}:00", xy=(inet_max_i, inet_n[inet_max_i]),
            xytext=(18.8, 0.80), fontsize=9, color="#1F4E79", bbox=bbox_w,
            arrowprops=dict(arrowstyle="->", color="#1F4E79", lw=1.1))
ax.annotate(f"call-out 主峰 {call_max_i:02d}:00", xy=(call_max_i, call_n[call_max_i]),
            xytext=(4.2, 1.22), fontsize=9, color="#C55A11", bbox=bbox_w,
            arrowprops=dict(arrowstyle="->", color="#C55A11", lw=1.1))
ax.annotate(f"call-out 次峰 {call_2nd_i:02d}:00", xy=(call_2nd_i, call_n[call_2nd_i]),
            xytext=(13.8, 0.98), fontsize=9, color="#C55A11", bbox=bbox_w,
            arrowprops=dict(arrowstyle="->", color="#C55A11", lw=1.1))

# ---------------- D. Grid concentration ----------------
grid_total = (panel.groupby("square_id")["internet"].sum()
              .sort_values(ascending=False))
cum_pct = grid_total.cumsum() / grid_total.sum() * 100
ranks = np.arange(1, len(cum_pct) + 1)

ax = fig.add_subplot(gs[3])
ax.plot(ranks, cum_pct.values, color="#6A3D9A", lw=2.2)
ax.set_xscale("log")
ax.set_xlim(1, len(ranks))
ax.set_ylim(0, 108)
ax.set_xlabel("网格排名（按当日 internet 活动量从高到低，对数轴）", fontsize=10)
ax.set_ylabel("累计覆盖全天流量（%）", fontsize=10)
ax.set_title("D. 网格集中度：前 K 个网格覆盖了多少全天 internet 活动量？",
             fontsize=12, loc="left", fontweight="bold")
ax.grid(True, which="major", ls="--", alpha=0.35)

for k in [10, 100, 500, 1000, len(ranks)]:
    if k <= len(cum_pct):
        v = float(cum_pct.iloc[k - 1])
        ax.scatter([k], [v], s=60, color="#6A3D9A", zorder=5)
        if k == len(ranks):
            ax.annotate(f"Top-{k}: {v:.1f}%", (k, v), textcoords="offset points",
                        xytext=(-12, 10), ha="right", fontsize=9, color="#4B2E83", bbox=bbox_w)
        else:
            ax.annotate(f"Top-{k}: {v:.1f}%", (k, v), textcoords="offset points",
                        xytext=(8, 8), fontsize=9, color="#4B2E83", bbox=bbox_w)
v100 = float(cum_pct.iloc[99])
ax.axvline(100, color="#C00000", ls="--", lw=1.0, alpha=0.65)
ax.annotate(f"Top-100 仅覆盖 {v100:.1f}%\n其余 {100 - v100:.1f}% 散落在另外 9,900 个网格\n分布扁平 → 不能只用 Top-100 代表全网",
            xy=(100, v100), xytext=(650, 62), fontsize=9.2, color="#C00000",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#C00000", alpha=0.9),
            arrowprops=dict(arrowstyle="->", color="#C00000", lw=1.2))

# ---------------- E. Full data table ----------------
ax = fig.add_subplot(gs[4])
ax.axis("off")
cell_text = [
    [f"{v:,.0f}" for v in inet],
    [f"{v:,.0f}" for v in call],
]
table = ax.table(cellText=cell_text,
                 rowLabels=["internet（scaled）", "call-out（scaled）"],
                 colLabels=xlabels,
                 loc="center", cellLoc="center")
table.auto_set_font_size(False)
table.set_fontsize(7.0)
table.scale(1.0, 1.35)
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#BFBFBF")
    cell.set_linewidth(0.4)
    if row == 0:
        cell.set_facecolor("#D9E2F3")
        cell.set_text_props(fontweight="bold", fontsize=8)
    elif row in (1, 2) and col == -1:
        cell.set_facecolor("#F2F2F2")
        cell.set_text_props(fontweight="bold", fontsize=8)
ax.set_title("E. 完整数据点：24 个小时的 internet 与 call-out（单位：scaled 活动量，四舍五入到整数）",
             fontsize=10.5, loc="left", fontweight="bold", pad=6)

fig.suptitle(f"Milan {DATE_STR} EDA：Internet / Call-out 逐小时活动量 + 网格集中度（全部数据点 + 关键点标注）",
             fontsize=15, fontweight="bold", x=0.065, ha="left", y=0.985)
plt.savefig(OUT, dpi=150, bbox_inches="tight")
plt.savefig(OUT_PDF, bbox_inches="tight")
print("saved:", OUT)
print("saved:", OUT_PDF)