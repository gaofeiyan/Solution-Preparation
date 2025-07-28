import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv

def calculate():
    try:
        total_vol = float(total_volume_entry.get())
        mw = float(mw_entry.get())
        ug_ml = float(ugml_entry.get())
        mm_input = float(mm_entry.get())

        # 单位换算
        if mw > 0:
            mmol_per_l = (ug_ml / 1000) / mw * 1000
            mmol_label.config(text=f"≈ {mmol_per_l:.3f} mM")
            ugml_back = mm_input * mw
            ugml_label.config(text=f"≈ {ugml_back:.2f} µg/mL")

        # 解析 stock_solutions
        stock_lines = stock_text.get("1.0", "end").strip().split("\n")
        stock_solutions = {}
        for line in stock_lines:
            try:
                c, v = line.strip().split(":")
                stock_solutions[float(c.strip())] = float(v.strip())
            except:
                messagebox.showwarning("格式错误", f"格式错误：{line}")
                return

        # 目标浓度
        concs = [float(x.strip()) for x in conc_entry.get().split(",") if x.strip()]
        results = []

        for fc in concs:
            best_stock = None
            min_vol = float('inf')
            selected_volume = 0

            if fc == 0:
                results.append([fc, "无", 0, total_vol, "对照组"])
                continue

            for sc, max_vol in stock_solutions.items():
                if sc >= fc:
                    v1 = (fc * total_vol) / sc
                    if v1 <= max_vol and v1 < min_vol:
                        min_vol = v1
                        best_stock = sc
                        selected_volume = round(v1, 2)

            if best_stock is None:
                results.append([fc, "无法满足", "-", "-", "浓度过高或储备液不足"])
            else:
                media_vol = round(total_vol - selected_volume, 2)
                results.append([fc, f"{best_stock} mM", selected_volume, media_vol, "✓"])

        # 展示结果
        for row in result_tree.get_children():
            result_tree.delete(row)
        for row in results:
            result_tree.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("错误", str(e))

def export_csv():
    path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV 文件", "*.csv")])
    if not path:
        return
    with open(path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["终浓度 (mM)", "使用储备液", "加药体积 (µL)", "培养基体积 (µL)", "状态"])
        for row_id in result_tree.get_children():
            writer.writerow(result_tree.item(row_id)['values'])

root = tk.Tk()
root.title("🧪 自动配药计算工具 GUI 版")

tk.Label(root, text="每孔总体积 (µL)").grid(row=0, column=0)
total_volume_entry = tk.Entry(root)
total_volume_entry.insert(0, "2000")
total_volume_entry.grid(row=0, column=1)

tk.Label(root, text="分子量 (g/mol)").grid(row=1, column=0)
mw_entry = tk.Entry(root)
mw_entry.insert(0, "194.19")
mw_entry.grid(row=1, column=1)

tk.Label(root, text="µg/mL 浓度").grid(row=2, column=0)
ugml_entry = tk.Entry(root)
ugml_entry.insert(0, "0.0")
ugml_entry.grid(row=2, column=1)

mmol_label = tk.Label(root, text="≈ 0.000 mM")
mmol_label.grid(row=2, column=2)

tk.Label(root, text="mM 浓度").grid(row=3, column=0)
mm_entry = tk.Entry(root)
mm_entry.insert(0, "0.0")
mm_entry.grid(row=3, column=1)

ugml_label = tk.Label(root, text="≈ 0.00 µg/mL")
ugml_label.grid(row=3, column=2)

tk.Label(root, text="储备液设置 (mM:µL)").grid(row=4, column=0)
stock_text = tk.Text(root, height=4, width=30)
stock_text.insert("1.0", "2: 1000\n5: 1000\n20: 1000")
stock_text.grid(row=4, column=1, columnspan=2)

tk.Label(root, text="目标浓度列表 (mM, 逗号分隔)").grid(row=5, column=0)
conc_entry = tk.Entry(root, width=30)
conc_entry.insert(0, "0,0.5,1,2,5,10")
conc_entry.grid(row=5, column=1, columnspan=2)

tk.Button(root, text="计算", command=calculate).grid(row=6, column=1)
tk.Button(root, text="导出 CSV", command=export_csv).grid(row=6, column=2)

cols = ["终浓度 (mM)", "使用储备液", "加药体积 (µL)", "培养基体积 (µL)", "状态"]
result_tree = ttk.Treeview(root, columns=cols, show="headings", height=8)
for col in cols:
    result_tree.heading(col, text=col)
    result_tree.column(col, width=120)
result_tree.grid(row=7, column=0, columnspan=3, pady=10)

root.mainloop()
