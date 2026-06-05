import streamlit as st
import pandas as pd
import plotly.express as px

# ページの設定
st.set_page_config(page_title="タスク優先順位マトリクス", layout="wide", page_icon="🎯")

st.title("🎯 タスク優先順位マトリクス (重要度 × 緊急度)")
st.write("タスクを10段階の重要度と緊急度で可視化し、取り組むべき優先順位を明確にするアプリです。")

# 1. セッション状態でタスクデータを保持（初回のみサンプルデータを投入）
if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(
        [
            {"task": "最優先の顧客対応", "importance": 9, "urgency": 10},
            {"task": "週次レポートの提出", "importance": 6, "urgency": 8},
            {"task": "新規プロジェクトの企画", "importance": 8, "urgency": 3},
            {"task": "デスクの片付け", "importance": 2, "urgency": 4},
        ]
    )

# 画面を2カラムに分割 (左: 入力と一覧、右: グラフ)
col_input, col_graph = st.columns([1, 1.5])

# --- 左カラム: タスクの追加と完了操作 ---
with col_input:
    st.subheader("➕ 新しいタスクを追加")
    
    # フォームを使って入力情報をまとめる
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("タスク名", placeholder="例: 提案書の作成")
        importance = st.slider("重要度 (1: 低 〜 10: 高)", min_value=1, max_value=10, value=5)
        urgency = st.slider("緊急度 (1: 低 〜 10: 高)", min_value=1, max_value=10, value=5)
        submit_button = st.form_submit_button("タスクを追加")
        
        if submit_button:
            if task_name.strip() == "":
                st.error("タスク名を入力してください。")
            else:
                # 新しいタスクをデータフレームに追加
                new_row = pd.DataFrame([{"task": task_name, "importance": importance, "urgency": urgency}])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_row], ignore_index=True)
                st.toast(f"「{task_name}」を追加しました！")
                st.rerun()

    st.write("---")
    st.subheader("✅ 現在のタスク (完了したらボタンを押す)")
    
    if st.session_state.tasks.empty:
        st.info("現在タスクはありません。上のフォームから追加してください。")
    else:
        # タスク一覧をループで表示し、横に完了ボタンを配置
        # ループ中に要素を削除するとバグるため、コピーに対してループを回す
        for idx, row in st.session_state.tasks.copy().iterrows():
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{row['task']}** \n*(重要度: {row['importance']} / 緊急度: {row['urgency']})*")
            
            # タスクごとにユニークなキーを持つ完了ボタンを作成
            if c2.button("完了", key=f"del_{idx}", type="primary"):
                st.session_state.tasks = st.session_state.tasks.drop(idx).reset_index(drop=True)
                st.toast(f"「{row['task']}」を完了しました！ 🎉")
                st.rerun()

# --- 右カラム: マトリクス図の可視化 ---
with col_graph:
    st.subheader("📊 タスク位置のマトリクス")
    
    if not st.session_state.tasks.empty:
        # Plotlyで散布図を作成
        fig = px.scatter(
            st.session_state.tasks,
            x="urgency",
            y="importance",
            text="task",  # グラフ上にタスク名を表示
            labels={"urgency": "緊急度 ➔", "importance": "重要度 ➔"},
            range_x=[0.5, 10.5],
            range_y=[0.5, 10.5],
        )
        
        # プロットの見た目を調整（ドットを大きく、テキストを上部に）
        fig.update_traces(
            marker=dict(size=14, color='#FF4B4B', line=dict(width=2, color='DarkSlateGrey')),
            textposition="top center",
            textfont=dict(size=12)
        )
        
        # 4象限（マトリクス）に分けるための補助線を中央（5.5）に引く
        fig.add_hline(y=5.5, line_dash="dash", line_color="rgba(128, 128, 128, 0.5)")
        fig.add_vline(x=5.5, line_dash="dash", line_color="rgba(128, 128, 128, 0.5)")
        
        # 目盛りを1〜10に固定し、グラフのレイアウトを調整
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=1, dtick=1),
            yaxis=dict(tickmode='linear', tick0=1, dtick=1),
            height=600,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        # 4象限のエリア名（目安ラベル）を背景に追加
        fig.add_annotation(x=9.5, y=9.5, text="🔥 Ⅰ. 緊急かつ重要", showarrow=False, font=dict(color="gray"))
        fig.add_annotation(x=1.5, y=9.5, text="📈 Ⅱ. 重要だが未緊急", showarrow=False, font=dict(color="gray"))
        fig.add_annotation(x=9.5, y=1.5, text="⚡ Ⅲ. 緊急だが非重要", showarrow=False, font=dict(color="gray"))
        fig.add_annotation(x=1.5, y=1.5, text="☕ Ⅳ. 優先度：低", showarrow=False, font=dict(color="gray"))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("表示するタスクがありません。")
