# 将配药工具脚本升级为更完整的 Streamlit 源码版本：
# - 支持单位转换（µg/mL ↔ mM，分子量输入）
# - 支持保存方案为 CSV
# - 更友好的界面提示
# - 打包为一个可用于 Hugging Face Spaces 或本地部署的 Python 脚本

import streamlit as st
import pandas as pd

st.set_page_config(page_title="🧪 自动配药工具", layout="centered")

st.title("🧪 自动配药计算工具 Pro 版")
st.markdown("设计适用于细胞实验的自动加药计算工具，支持终浓度设置、单位转换、储备液选择等功能。")

# 设置总体积
total_vol = st.number_input("每孔总体积 (µL)", value=2000, step=100)

# 支持单位转换功能
st.markdown("### ✅ 浓度单位转换（可选）")
with st.expander("点击展开 µg/mL ↔ mM 转换工具"):
    mw = st.number_input("分子量 (g/mol)", value=194.19, step=0.01, help="输入药物分子量")
    ug_per_ml = st.number_input("µg/mL 浓度", value=0.0, step=0.1)
    if mw > 0:
        mmol_per_l = (ug_per_ml / 1000) / mw * 1000  # 转为 mM
        st.info(f"≈ {mmol_per_l:.3f} mM")
    mm_input = st.number_input("反向换算：mM 浓度", value=0.0, step=0.1)
    ugml_back = mm_input * mw
    st.info(f"≈ {ugml_back:.2f} µg/mL")

# 储备液输入
st.markdown("### 储备液设置")
stock_input = st.text_area("输入储备液浓度与体积 (格式: 浓度mM:体积µL，每行一个)", "2: 1000\n5: 1000\n20: 1000")

# 将输入的文本转换为字典
stock_solutions = {}
for line in stock_input.strip().split("\n"):  # 使用 \n 而不是 \\n
    try:
        c, v = line.strip().split(":")
        stock_solutions[float(c.strip())] = float(v.strip())
    except:
        st.warning(f"格式错误：{line}")


# 输入目标浓度
st.markdown("### 目标终浓度设置")
target_concs = st.text_input("输入目标浓度列表 (mM, 用逗号分隔)", "0,0.5,1,2,5,10")
target_concs = [float(x.strip()) for x in target_concs.split(",") if x.strip()]

# 计算部分
results = []
for fc in target_concs:
    best_stock = None
    min_vol = float('inf')
    selected_volume = 0

    if fc == 0:
        results.append((fc, "无", 0, total_vol, "对照组"))
        continue

    for sc, max_vol in stock_solutions.items():
        if sc >= fc:
            v1 = (fc * total_vol) / sc
            if v1 <= max_vol and v1 < min_vol:
                min_vol = v1
                best_stock = sc
                selected_volume = round(v1, 2)

    if best_stock is None:
        results.append((fc, "无法满足", "-", "-", "浓度过高或储备液不足"))
    else:
        media_vol = round(total_vol - selected_volume, 2)
        results.append((fc, f"{best_stock} mM", selected_volume, media_vol, "✓"))

# 展示结果
df = pd.DataFrame(results, columns=["终浓度 (mM)", "使用储备液", "加药体积 (µL)", "培养基体积 (µL)", "状态"])
st.markdown("### 📊 计算结果")
st.dataframe(df)

# 下载 CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 下载为 CSV 文件", data=csv, file_name="配药结果.csv", mime="text/csv")

