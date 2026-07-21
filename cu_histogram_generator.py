"""
1m XRF Copper Histogram Generator
by Addy Chapman

"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

# ── colour palette (rose-quartz / amethyst vibes) ─────────────────────────────
BG_DARK   = "#2b1b2e"   # deep plum
BG_CARD   = "#3a2040"   # soft purple-black
ROSE      = "#e8a0bf"   # dusty rose
LILAC     = "#c780e8"   # amethyst lilac
BLUSH     = "#f7c5d5"   # pale blush
MAUVE     = "#9b5d8a"   # mauve border
WHITE     = "#f5eef8"   # warm white
SOFT_GREY = "#b09ab8"   # muted purple-grey


def build_gui():
    root = tk.Tk()
    root.title("💎  Cu Histogram Generator")
    root.configure(bg=BG_DARK)
    root.resizable(False, False)

    WIN_W, WIN_H = 1080, 740
    root.geometry(f"{WIN_W}x{WIN_H}")
    root.update_idletasks()
    x = (root.winfo_screenwidth()  - WIN_W) // 2
    y = (root.winfo_screenheight() - WIN_H) // 2
    root.geometry(f"+{x}+{y}")

    csv_path   = tk.StringVar()
    output_dir = tk.StringVar()
    hole_name  = tk.StringVar()

    # ── rounded button helper ─────────────────────────────────────────────────
    def make_btn(parent, text, command, fg=BG_DARK, bg=ROSE, w=100, h=30):
        c = tk.Canvas(parent, width=w, height=h,
                      bg=parent["bg"], highlightthickness=0, cursor="hand2")
        r = 10
        def draw(color):
            c.delete("all")
            for ax, ay, start in [(0,0,90),(w-r*2,0,0),(w-r*2,h-r*2,270),(0,h-r*2,180)]:
                c.create_arc(ax, ay, ax+r*2, ay+r*2,
                             start=start, extent=90, fill=color, outline=color)
            c.create_rectangle(r, 0, w-r, h, fill=color, outline=color)
            c.create_rectangle(0, r, w, h-r, fill=color, outline=color)
            c.create_text(w//2, h//2, text=text, fill=fg,
                          font=("Georgia", 10, "bold"))
        draw(bg)
        c.bind("<Enter>",    lambda e: draw(BLUSH))
        c.bind("<Leave>",    lambda e: draw(bg))
        c.bind("<Button-1>", lambda e: command())
        return c

    # ── decorative header ─────────────────────────────────────────────────────
    header = tk.Canvas(root, width=WIN_W, height=160,
                       bg=BG_DARK, highlightthickness=0)
    header.pack(fill="x")

    # shadow + title
    header.create_text(WIN_W//2+1, 75, text="💎  Cu Histogram Generator",
                       fill=MAUVE, font=("Georgia", 28, "bold"))
    header.create_text(WIN_W//2,   74, text="💎  Cu Histogram Generator",
                       fill=BLUSH, font=("Georgia", 28, "bold"))
    header.create_text(WIN_W//2, 118, text="✨  Length vs Copper Concentration  ✨",
                       fill=ROSE, font=("Georgia", 14, "italic"))
    header.create_line(60, 148, WIN_W-60, 148, fill=MAUVE, width=1, dash=(4,3))

    # ── card ──────────────────────────────────────────────────────────────────
    card = tk.Frame(root, bg=BG_CARD, padx=50, pady=32)
    card.pack(fill="both", expand=True, padx=32, pady=(4,28))
    card.columnconfigure(0, weight=1)

    def lbl(text, r):
        tk.Label(card, text=text, bg=BG_CARD, fg=ROSE,
                 font=("Georgia", 13, "bold")).grid(
                     row=r, column=0, sticky="w", pady=(0,3))

    def entry_row(var, r):
        f = tk.Frame(card, bg=BG_CARD)
        f.grid(row=r, column=0, sticky="ew", pady=(0,11))
        tk.Entry(f, textvariable=var, width=72,
                 bg="#4a2a55", fg=WHITE, insertbackground=BLUSH,
                 relief="flat", font=("Courier", 11),
                 highlightthickness=1, highlightcolor=LILAC,
                 highlightbackground=MAUVE).pack(side="left", ipady=5, padx=(0,8))
        return f

    # ── Hole Name input ───────────────────────────────────────────────────────
    # FIX 1: width=72 to match CSV and Output Directory entry boxes
    lbl("✦  Hole Name", 0)
    f0 = tk.Frame(card, bg=BG_CARD)
    f0.grid(row=1, column=0, sticky="ew", pady=(0,11))
    tk.Entry(f0, textvariable=hole_name, width=72,
             bg="#4a2a55", fg=WHITE, insertbackground=BLUSH,
             relief="flat", font=("Courier", 11),
             highlightthickness=1, highlightcolor=LILAC,
             highlightbackground=MAUVE).pack(side="left", ipady=5, padx=(0,8))

    # CSV picker
    lbl("✦  CSV Input File", 2)
    f1 = entry_row(csv_path, 3)

    def pick_file():
        path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            csv_path.set(path)
            if not output_dir.get():
                output_dir.set(os.path.dirname(path))

    make_btn(f1, "Browse…", pick_file, fg=BG_DARK, bg=ROSE, w=130, h=34).pack(side="left")

    # Output dir picker
    lbl("✦  Output Directory", 4)
    f2 = entry_row(output_dir, 5)

    def pick_dir():
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            output_dir.set(path)

    make_btn(f2, "Browse…", pick_dir, fg=BG_DARK, bg=ROSE, w=130, h=34).pack(side="left")

    # Status
    status_var = tk.StringVar(value="Ready — select a CSV and output folder 🌸")
    tk.Label(card, textvariable=status_var, bg=BG_CARD, fg=SOFT_GREY,
             font=("Georgia", 10, "italic"), wraplength=900,
             justify="left").grid(row=6, column=0, sticky="w", pady=(0,8))

    # Generate button
    def generate():
        if not csv_path.get():
            messagebox.showwarning("Oops!", "Please select a CSV file first 💕")
            return
        if not output_dir.get():
            messagebox.showwarning("Oops!", "Please select an output folder 💕")
            return
        status_var.set("⏳ Processing…")
        root.update_idletasks()
        try:
            run_histogram(csv_path.get(), output_dir.get(), hole_name.get(), status_var, root)
        except Exception as exc:
            status_var.set(f"❌ Error: {exc}")
            messagebox.showerror("Error", str(exc))

    make_btn(card, "✨  Generate Histogram", generate,
             fg=BG_DARK, bg=LILAC, w=340, h=54).grid(row=7, column=0, pady=(0,2))

    root.mainloop()


# ── histogram logic ───────────────────────────────────────────────────────────

def get_bar_color(v):
    if v < 0.1:   return "#4477cc"
    elif v < 0.2: return "#ddcc44"
    elif v < 0.3: return "#ff8833"
    elif v < 0.5: return "#cc2222"
    else:         return "#ff00ff"


def run_histogram(csv_path, output_dir, hole_name, status_var, root):
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    from datetime import datetime

    status_var.set("📂 Reading CSV…"); root.update_idletasks()

    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    # ── FIX 2: depth column detection with row-2 fallback ────────────────────
    # Try named column first, then positional column 216, then check if row 0
    # is blank/NaN and retry using row 1 (the second row) as the header.
    def find_column(df, name, pos):
        """Return a Series for `name` col or column at `pos`, with row-2 fallback."""
        if name in df.columns:
            col = df[name]
        elif df.shape[1] > pos:
            col = df.iloc[:, pos]
        else:
            col = None

        # If we found a column but its first value is blank/NaN, try re-reading
        # the CSV treating row 2 (index 1) as the header row instead.
        if col is not None:
            first_val = col.iloc[0] if len(col) > 0 else None
            first_is_blank = (
                first_val is None
                or (isinstance(first_val, float) and np.isnan(first_val))
                or (isinstance(first_val, str) and first_val.strip() == "")
            )
            if first_is_blank:
                col = col.iloc[1:].reset_index(drop=True)
            return col

        # Column not found at all — attempt row-2 header fallback on whole df
        # (re-read with header=1 so second row becomes the header)
        df2 = pd.read_csv(csv_path, encoding="utf-8-sig", header=1)
        if name in df2.columns:
            return df2[name]
        elif df2.shape[1] > pos:
            return df2.iloc[:, pos]
        return None

    depth_col = find_column(df, "Depth", 216)
    if depth_col is None:
        raise ValueError(f"Could not find 'Depth' column.\nFound: {list(df.columns)}")

    cu_col = find_column(df, "Cu Concentration", 38)
    if cu_col is None:
        raise ValueError(f"Could not find 'Cu Concentration' column.\nFound: {list(df.columns)}")

    depth = pd.to_numeric(depth_col, errors="coerce")

    # ── FIX 4: treat "<LOD" (below limit of detection) readings as 0% ────────
    # The XRF instrument reports values below its detection threshold as the
    # literal string "<LOD" rather than a number. pd.to_numeric() turns those
    # into NaN, and the old NaN-drop mask below then silently excluded those
    # rows from the plot entirely (this is why depths 107-112 etc. were
    # missing). Below-detection copper is treated as 0% instead of dropped.
    cu_str      = cu_col.astype(str).str.strip()
    below_lod   = cu_str.str.startswith("<")
    cu_ppm      = pd.to_numeric(cu_col, errors="coerce")
    cu_ppm      = cu_ppm.mask(below_lod, 0)

    # Align indexes after any slicing that happened in find_column
    depth  = depth.reset_index(drop=True)
    cu_ppm = cu_ppm.reset_index(drop=True)

    mask   = depth.notna() & cu_ppm.notna()
    depth  = depth[mask].reset_index(drop=True)
    cu_pct = (cu_ppm[mask] / 10000.0).reset_index(drop=True)

    status_var.set("📊 Building histogram…"); root.update_idletasks()

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    for i in range(len(depth)):
        x   = depth.iloc[i]
        y   = cu_pct.iloc[i]
        yd  = min(y, 0.5)
        ax.bar(x, yd, width=1.0, color=get_bar_color(y), align="center",
               linewidth=0.4, edgecolor="black", zorder=2)

        # ── FIX 3: label position logic ───────────────────────────────────────
        # > 0.5 %  → label inside bar near top (bar is capped)
        # 0.3–0.5% → label inside bar near top (same style as > 0.5)
        # < 0.3 %  → label just above the bar
        if y >= 0.3:
            # Place label inside the bar, near the top
            ax.text(x, yd * 0.93, f"{y:.3f}",
                    color="black", fontsize=7, va="top", ha="center",
                    rotation=90, fontweight="bold", clip_on=True, zorder=6)
        else:
            ax.text(x, yd + 0.01, f"{y:.3f}",
                    color="black", fontsize=7, va="bottom", ha="center",
                    rotation=90, fontweight="bold", clip_on=True, zorder=6)

    x_min = float(depth.min()) - 0.5
    x_max = float(depth.max()) + 0.5
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, 0.5)

    ax.set_xticks(np.arange(np.floor(x_min), np.ceil(x_max) + 1, 1))
    ax.xaxis.set_tick_params(labelsize=7, rotation=90)
    ax.set_yticks(np.arange(0, 0.501, 0.025))
    ax.yaxis.set_tick_params(labelsize=8)

    ax.set_axisbelow(False)
    ax.grid(axis="both", color="#cccccc", linewidth=0.8, linestyle="-", zorder=5)

    ax.set_xlabel("Length (m)",            color="black", fontsize=11, labelpad=8)
    ax.set_ylabel("Cu Concentration (%)", color="black", fontsize=11, labelpad=8)

    # ── dynamic title incorporating hole name ─────────────────────────────────
    title_prefix = f"{hole_name} " if hole_name.strip() else ""
    ax.set_title(f"{title_prefix}1m XRF Copper Concentration vs Length",
                 color="black", fontsize=14, fontweight="bold", pad=12)

    ax.tick_params(colors="black")
    for spine in ax.spines.values():
        spine.set_edgecolor("black")

    patches = [
        mpatches.Patch(color="#4477cc", label="0 – 0.1 %"),
        mpatches.Patch(color="#ddcc44", label="0.1 – 0.2 %"),
        mpatches.Patch(color="#ff8833", label="0.2 – 0.3 %"),
        mpatches.Patch(color="#cc2222", label="0.3 – 0.5 %"),
        mpatches.Patch(color="#ff00ff", label="> 0.5 % (capped)"),
    ]
    legend = ax.legend(handles=patches, loc="upper right",
                       facecolor="white", edgecolor="black",
                       labelcolor="black", fontsize=9, title="Legend")
    legend.get_title().set_fontweight("bold")

    fig.tight_layout()

    ts       = datetime.now().strftime("%Y_%m_%d")
    base     = os.path.splitext(os.path.basename(csv_path))[0]
    out_path = os.path.join(output_dir, f"{base}m_XRF_Graph_{ts}.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    status_var.set("✅ Histogram saved successfully!")
    messagebox.showinfo("Done! 💕", "Histogram saved successfully! 🌸")


# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import importlib.util
    missing = [p for p in ("pandas", "matplotlib")
               if not importlib.util.find_spec(p)]
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print(f"Install with:  pip install {' '.join(missing)}")
        sys.exit(1)
    build_gui()
