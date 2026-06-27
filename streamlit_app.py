import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# ページの設定
st.set_page_config(page_title="タスク優先順位マトリクス", layout="wide", page_icon="🎯")

st.title("🎯 タスク優先順位マトリクス (重要度 × 緊急度)")
st.write("タスクの状態（未着手・着手中）によって、マトリクス上の点の色が自動で変わります。")

# --- Supabaseの初期化 ---
@st.cache_resource
def init_supabase() -> Client:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- データ操作用関数 ---
def load_data():
    """Supabaseから全タスクを取得してDataFrameにする"""
    response = supabase.table("tasks").select("*").order("created_at").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        # 万が一status列がない場合のセーフティ
        if "status" not in df.columns:
            df["status"] = "Todo"
        return df
    else:
        return pd.DataFrame(columns=["id", "task", "importance", "urgency", "is_completed", "status"])

# 最新データの読み込み
df_all = load_data()

# グラフや一覧に使うデータの分類
df_active = df_all[df_all["status"].isin(["Todo", "In Progress"])].reset_index(drop=True)
df_completed = df_all[df_all["status"] == "Done"].reset_index(drop=True)


# --- 画面を2カラムに分割（元のシンプルなレイアウト） ---
col_input, col_graph = st.columns([1, 1.5])

# --- 左カラム: タスクの追加と一覧・操作 ---
with col_input:
    st.subheader("➕ 新しいタスクを追加")
    
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("タスク名", placeholder="例: お風呂掃除")
        importance = st.slider("重要度 (1: 低 〜 10: 高)", min_value=1, max_value=10, value=5)
        urgency = st.slider("緊急度 (1: 低 〜 10: 高)", min_value=1, max_value=10, value=5)
        submit_button = st.form_submit_button("タスクを追加")
        
        if submit_button:
            if task_name.strip() == "":
                st.error("タスク名を入力してください。")
            else:
                # 新規タスクは初期状態 'Todo' (未着手) で保存
                supabase.table("tasks").insert({
                    "task": task_name,
                    "importance": importance,
                    "urgency": urgency,
                    "status": "Todo",
                    "is_completed": False
                }).execute()
                st.toast(f"「{task_name}」を追加しました！")
                st.rerun()

    st.write("---")
    st.subheader("📋 現在のタスク一覧")
    
    if df_active.empty:
        st.info("現在タスクはありません。上のフォームから追加してください。")
    else:
        for idx, row in df_active.iterrows():
            # 綺麗なカード型の枠の中にタスクを並べる
            with st.container(border=True):
                # 状態に合わせてアイコンと文字を変える
                status_label = "🔴 未着手" if row['status'] == "Todo" else "🔵 着手中"
                st.write(f"**{row['task']}** *({status_label})*")
                st.caption(f"重要度: {row['importance']} / 緊急度: {row['urgency']}")
                
                # 操作ボタンを横並びにする（3分割）
                c1, c2, c3 = st.columns(3)
                
                # 1. 状態切り替えボタン
                if row['status'] == "Todo":
                    if c1.button("⚡ 着手する", key=f"start_{row['id']}", use_container_width=True):
                        supabase.table("tasks").update({"status": "In Progress"}).eq("id", row['id']).execute()
                        st.rerun()
                else:
                    if c1.button("📥 戻す", key=f"back_{row['id']}", use_container_width=True):
                        supabase.table("tasks").update({"status": "Todo"}).eq("id", row['id']).execute()
                        st.rerun()
                
                # 2. 完了ボタン（押すと画面から消えて履歴へ）
                if c2.button("完了 🎉", key=f"done_{row['id']}", type="primary", use_container_width=True):
                    supabase.table("tasks").update({"status": "Done", "is_completed": True}).eq("id", row['id']).execute()
                    st.toast(f"「{row['task']}」を完了しました！")
                    st.rerun()
                
                # 3. 削除ボタン（完全に消去）
                if c3.button("🗑️ 削除", key=f"del_{row['id']}", use_container_width=True):
                    supabase.table("tasks").delete().eq("id", row['id']).execute()
                    st.rerun()

# --- 右カラム: グラフ表示 ---
with col_graph:
    st.subheader("📊 タスク位置のマトリクス")
    
    if not df_active.empty:
        # 🚀 color="status" を指定して、状態ごとにピンの色を自動で分ける
        fig = px.scatter(
            df_active,
            x="urgency",
            y="importance",
            text="task",
            color="status",
            # 🚀 未着手を赤、着手中を青に指定（もし黄色がよければ "#FFC107" に変更してください）
            color_discrete_map={"Todo": "#FF4B4B", "In Progress": "#0080FF"},
            labels={"urgency": "緊急度 ➔", "importance": "重要度 ➔", "status": "状態"},
            range_x=[0.5, 10.5],
            range_y=[0.5, 10.5],
        )
        
        fig.update_traces(
            marker=dict(size=14, line=dict(width=1.5, color='DarkSlateGrey')),
            textposition="middle right", 
            textfont=dict(size=12)
        )
        
        fig.add_hline(y=5.5, line_dash="dash", line_color="rgba(128, 128, 128, 0.5)")
        fig.add_vline(x=5.5, line_dash="dash", line_color="rgba(128, 128, 128, 0.5)")
        
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=1, dtick=1),
            yaxis=dict(tickmode='linear', tick0=1, dtick=1),
            width=750,  
            height=550, 
            margin=dict(l=20, r=20, t=20, b=20),
            # グラフの上に「Todo」「In Progress」の色の凡例を横並びで表示
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=False)
        
        st.markdown("""
        **【マトリクスの見方】**
        | 象限 | 特徴 | 対応の目安 |
        |---|---|---|
        | **🔥 I. 緊急かつ重要** (右上) | すぐにやるべき最優先タスク | **すぐ実行** |
        | **📈 II. 重要だが未緊急** (左上) | 将来のために計画的に進める | **計画** |
        | **⚡ III. 緊急だが非重要** (右下) | 他人に任せる、または効率化する | **他人に任せる** |
        | **🍵 IV. 優先度：低** (左下) | 後回しにする、またはやめる | **後回し・削除** |
        """)
    else:
        st.info("表示するタスクがありません。")

# --- 画面下部: 完了したタスクの履歴表示 ---
st.write("---")
st.subheader("🎉 完了済みのタスク履歴")

if df_completed.empty:
    st.caption("完了したタスクはまだありません。1つずつ片付けていきましょう！")
else:
    for idx, row in df_completed.iterrows():
        st.write(f"✅ ~~{row['task']}~~ *(重要度: {row['importance']} / 緊急度: {row['urgency']})*")
    
    if st.button("履歴をすべてクリア", type="secondary"):
        supabase.table("tasks").delete().eq("status", "Done").execute()
        st.rerun()
