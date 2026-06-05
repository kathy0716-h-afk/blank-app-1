import streamlit as st
import pandas as pd
import plotly.express as px

# ページの設定
st.set_page_config(page_title="タスク優先順位マトリクス", layout="wide", page_icon="🎯")

st.title("🎯 タスク優先順位マトリクス (重要度 × 緊急度)")
st.write("タスクを10段階の重要度と緊急度で可視化し、取り組むべき優先順位を明確にするアプリです。")

# 1. セッション状態の初期化
# 未完了タスク
if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(
        [
            {"task": "最優先の顧客対応", "importance": 9, "urgency": 10},
            {"task": "週次レポートの提出", "importance": 6, "urgency": 8},
            {"task": "新規プロジェクトの企画", "importance": 8, "urgency": 3},
            {"task": "デスクの片付け", "importance": 2, "urgency": 4},
        ]
    )

# 完了済みタスクを保存する箱
if "completed_tasks" not in st.session_state:
    st.session_state.completed_tasks = pd.DataFrame(columns=["task", "importance", "urgency"])

# 画面を2カラムに分割 (左: 入力と一覧、右: グラフ)
col_input, col_graph = st.columns([1, 1.5])

# --- 左カラム: タスクの追加と完了操作 ---
with col_input:
    st.subheader("➕ 新しいタスクを追加")
    
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("タスク名", placeholder="例: 提案書の作成")
        importance = st.slider("重要度 (1: 低 〜 10: 高)", min_value=1, max_value=10, value=5)
        urgency = st.slider("緊急度 (1: 低 〜 10: 高)", min_value=1, max_value=10, value=5)
        submit_button = st.form_submit_button("タスクを追加")
        
        if submit_button:
            if task_name.strip() == "":
                st.error("タスク名を入力してください。")
            else:
                new_row = pd.DataFrame([{"task": task_name, "importance": importance, "urgency": urgency}])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_row], ignore_index=True)
                st.toast(f"「{task_name}」を追加しました！")
                st.rerun()

    st.write("---")
    st.subheader("✅ 現在のタスク (完了したらボタンを押す)")
    
    if st.session_state.tasks.empty:
        st.info("現在タスクはありません。上のフォームから追加してください。")
    else:
        for idx, row in st.session_state.tasks.copy().iterrows():
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{row['task']}** \n*(重要度: {row['importance']} / 緊急度: {row['urgency']})*")
            
            if c2.button("完了", key=f"del_{idx}", type="primary"):
                completed_row = st.session_state.tasks.iloc[[idx]]
                st.session_state.completed_tasks = pd.concat(
                    [st.session_state.completed_tasks, completed_row], ignore_index=True
                )
                st.session_state.tasks = st.session_state.tasks.drop(idx).reset_index(drop=True)
                st.toast(f"「{row['task']}」を完了しました！ 🎉")
                st.rerun()

# --- 🔄 修正：右カラム（グラフ表示）を調整 ---
with col_graph:
    st.subheader("📊 タスク位置のマトリクス")
    
    if not st.session_state.tasks.empty:
        # 🚀 【追加】グラフの上に凡例（象限ラベル）を表示
        st.markdown("""
        **【マトリクスの見方】**
        | 象限 | 特徴 | 対応の目安 |
        |---|---|---|
        | **🔥 I. 緊急かつ重要** (右上) | すぐにやるべき最優先タスク | **すぐ実行** |
        | **📈 II. 重要だが未緊急** (左上) | 将来のために計画的に進める | **計画** |
        | **⚡ III. 緊急だが非重要** (右下) | 他人に任せる、または効率化する | **他人に任せる** |
        | **☕ IV. 優先度：低** (左下) | 後回しにする、またはやめる | **後回し・削除** |
        """)
        
        fig = px.scatter(
            st.session_state.tasks,
            x="urgency",
            y="importance",
            text="task",
            labels={"urgency": "緊急度 ➔", "importance": "重要度 ➔"},
            range_x=[0.5, 10.5],
            range_y=[0.5, 10.5],
        )
        
        fig.update_traces(
            marker=dict(size=14, color='#FF4B4B', line=dict(width=2, color='DarkSlateGrey')),
            # 🚀 【変更】textpositionを"top center"から"middle right"に変更し、点との重なりを解消
            textposition="middle right", 
            textfont=dict(size=12)
        )
        
        fig.add_hline(y=5.5, line_dash="dash", line_color="rgba(128, 128, 128, 0.5)")
        fig.add_vline(x=5.5, line_dash="dash", line_color="rgba(128, 128, 128, 0.5)")
        
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=1, dtick=1),
            yaxis=dict(tickmode='linear', tick0=1, dtick=1),
            height=600,
            # グラフの余白を少し調整
            margin=dict(l=20, r=20, t=20, b=20)
        )
