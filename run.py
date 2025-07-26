
import streamlit as st
import pandas as pd

st.title("🧪 自动配药计算工具")
st.markdown("根据你的输入自动计算每孔加药和培养基体积。")

# 输入孔总体积
total_vol = st.number_input("每孔总体积 (µL)", value=2000, step=100)

# 输入目标浓度列表
target_input = st.text_input("目标浓度列表 (mM, 逗号分隔)", "0,0.5,1,2,5,10")
target_concs = [float(x.strip()) for x in target_input.split(",") if x.strip()]

st.markdown("### 储备液设置")
st.markdown("输入每个储备液的浓度和最大可用体积（单位 µL）")

stock_data = st.text_area("储备液列表 (格式: 浓度 mM: 体积 µL，一行一个)", "2: 1000\n5: 1000\n20: 1000")

# 解析储备液信息
stock_solutions = {}
for line in stock_data.strip().split("\n"):
    try:
        c, v = line.strip().split(":")
        stock_solutions[float(c.strip())] = float(v.strip())
    except:
        st.warning(f"格式错误：{line}")

# 计算配药结果
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
df_results = pd.DataFrame(results, columns=["终浓度 (mM)", "使用储备液", "加药体积 (µL)", "培养基体积 (µL)", "状态"])
st.dataframe(df_results)

# 下载按钮
st.download_button("📥 下载结果为 Excel", data=df_results.to_csv(index=False), file_name="配药结果.csv", mime="text/csv")

