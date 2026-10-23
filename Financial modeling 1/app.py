import streamlit as st
import pandas as pd
import plotly.express as px

# ページ設定
st.set_page_config(
    page_title="Simple Financial Model",
    page_icon="📈",
    layout="wide"
)

st.title("📈 シンプル財務モデル・シミュレーター")
st.markdown("サイドバーのパラメータを調整して、将来の損益計算書（PL）と推移を確認できます。")

# --- サイドバー：入力パラメータ ---
st.sidebar.header("⚙️ 前提条件（入力）")

initial_revenue = st.sidebar.number_input("初期売上高 (百万円)", min_value=10, max_value=10000, value=100, step=10)
growth_rate = st.sidebar.slider("年間売上成長率 (%)", min_value=-20.0, max_value=100.0, value=15.0, step=1.0) / 100.0
cogs_rate = st.sidebar.slider("売上原価率 (%)", min_value=10.0, max_value=90.0, value=40.0, step=1.0) / 100.0
opex = st.sidebar.number_input("年間販管費 (固定費・百万円)", min_value=1, max_value=5000, value=40, step=5)
tax_rate = st.sidebar.slider("実効税率 (%)", min_value=0.0, max_value=50.0, value=30.0, step=1.0) / 100.0
forecast_years = st.sidebar.slider("予測期間 (年)", min_value=3, max_value=10, value=5, step=1)

# --- 財務モデルの計算 ---
years = [f"{i+1}年目" for i in range(forecast_years)]
revenues = []
cogs_list = []
gross_profits = []
opex_list = []
operating_incomes = []
taxes = []
net_incomes = []

current_rev = initial_revenue
for i in range(forecast_years):
    if i > 0:
        current_rev = current_rev * (1 + growth_rate)
    
    rev = current_rev
    cogs = rev * cogs_rate
    gp = rev - cogs
    op = opex  # ここでは単純化のため固定費として扱う
    oi = gp - op
    tax = max(0, oi * tax_rate)
    ni = oi - tax
    
    revenues.append(rev)
    cogs_list.append(cogs)
    gross_profits.append(gp)
    opex_list.append(op)
    operating_incomes.append(oi)
    taxes.append(tax)
    net_incomes.append(ni)

# 見やすいように転置してテーブルを作成
data_dict = {
    "売上高": revenues,
    "売上原価": cogs_list,
    "売上総利益": gross_profits,
    "販管費": opex_list,
    "営業利益": operating_incomes,
    "法人税等": taxes,
    "当期純利益": net_incomes
}
df_table = pd.DataFrame(data_dict, index=years).T

# 小数点第1位で丸める
df_table = df_table.round(1)

# --- 画面レイアウト ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📊 損益計算書 (PL) 予測")
    st.dataframe(df_table, use_container_width=True)
    
    # CSVダウンロードボタン（utf-8-sigを指定してExcelでの文字化けを防ぐ）
csv = df_table.to_csv().encode('utf-8-sig')
st.download_button(
    label="📥 CSV形式でダウンロード",
    data=csv,
    file_name='financial_model.csv',
    mime='text/csv',
)

with col2:
    st.subheader("📈 主要指標の推移")
    # グラフ用データの作成
    df_chart = pd.DataFrame({
        "年": years,
        "売上高": revenues,
        "売上総利益": gross_profits,
        "営業利益": operating_incomes,
        "当期純利益": net_incomes
    })
    df_chart_melted = df_chart.melt(id_vars="年", value_vars=["売上高", "売上総利益", "営業利益", "当期純利益"], 
                                      var_name="指標", value_name="金額 (百万円)")
    
    fig = px.line(df_chart_melted, x="年", y="金額 (百万円)", color="指标" if "指标" in df_chart_melted.columns else "指標", markers=True)
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)