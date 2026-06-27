# 🎯 タスク優先順位マトリクス (重要度 × 緊急度)

StreamlitとSupabaseを利用した、仕事やタスクの優先順位を明確にするためのWebアプリケーションです。タスクを「重要度」と「緊急度」の10段階で評価し、2軸のマトリクス（アイゼンハワーマトリクス）上に自動で可視化します。さらに、進捗ステータス（未着手・着手中）に応じてプロットの色がリアルタイムに変化するため、今どのタスクに集中すべきかが一目でわかります。

---

## 🔗 アプリURL
このURLで試すことができます（スリープ状態のときは青色の起動ボタンを押してください）：
https://blank-app-6qh97cuy4dj.streamlit.app/

---

## 🌟 主な機能
* **2軸マトリクスの自動可視化**: 入力された重要度と緊急度（1〜10）を元に、Plotlyを用いて4象限のマトリクス図へリアルタイムにプロットします。
* **進捗ステータス連動の色分け**: タスクの状態が「未着手」なら赤色、「着手中」なら青色にプロットが変化し、優先度と進捗を同時に俯瞰できます。
* **クラウドデータ永続化**: バックエンドにSupabase（PostgreSQL）を採用しているため、ブラウザを閉じたりアプリが休止状態になったりしても、データが消えずに保存されます。
* **完了タスクの履歴管理**: 完了したタスクはマトリクスから消去され、画面下部に「完了済みのタスク履歴」として打ち消し線付きで蓄積されます（一括クリアも可能）。

---

## 🛠 セットアップ方法

### 1. 依存ライブラリのインストール
Python環境がインストールされていることを確認し、必要なライブラリをインストールしてください。

```bash
pip install streamlit pandas plotly supabase
```

### 2. Supabaseの準備
Supabaseのプロジェクトを作成し、SQL Editorで以下のスクリプトを実行して `tasks` テーブルを作成してください。（※RLSはオフの状態で実行してください）

```sql
create table tasks (
  id bigint generated always as identity primary key,
  task text not null,
  importance integer not null,
  urgency integer not null,
  status text default 'Todo' not null,
  is_completed boolean default false not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

### 3. Streamlit Secrets（環境変数）の設定
ローカル環境で実行する場合は、プロジェクトのルートディレクトリに `.streamlit/secrets.toml` ファイルを作成し、Supabaseの接続情報を記述してください。
（※Streamlit Community Cloudにデプロイする場合は、管理画面の「Secrets」に入力してください）

```toml
SUPABASE_URL = "[https://あなたのプロジェクトID.supabase.co](https://あなたのプロジェクトID.supabase.co)"
SUPABASE_KEY = "あなたのanon_publicキー"
```

### 4. アプリの起動
以下のコマンドでアプリを起動します。

```bash
streamlit run app.py
```

---

## 📊 データの仕組み
このアプリは **Supabase (PostgreSQL)** を使用してタスクデータを一元管理しています。

* **`tasks` テーブル**:
    * `id`: タスクを一意に識別するID（自動採番）
    * `task`: タスク名（文字列）
    * `importance` / `urgency`: 重要度・緊急度の数値（1〜10の整数）
    * `status`: 進捗状態（`Todo`：未着手 / `In Progress`：着手中 / `Done`：完了）
    * `is_completed`: 完了フラグ（真偽値）
    * `created_at`: 作成日時

---

## 💻 使用技術（WebAPIの活用）
このアプリは、以下の外部サービス、WebAPI、およびライブラリを連携させて動作しています。
* **Frontend / UI**: Streamlit
* **Visualization**: Plotly Express (インタラクティブなグラフ描画API)
* **Data Handling**: Pandas (データの表形式への変換・加工)
* **Database (Backend)**: Supabase (データの永続保存のためのクラウド接続API / PostgreSQL)

---

## 💡 今後のロードマップ（カスタマイズ例）
* **デッドライン（期限日）機能**: タスクに期限を設定し、期日が迫ると緊急度が自動で上がる仕組みの導入。
* **マトリクスの背景色塗り分け**: 4つの象限（「緊急かつ重要」など）のエリアを直感的に分かりやすく色付けする。
* **バブルチャート化**: タスクの「所要時間」を入力項目に加え、作業が重いタスクほどプロットの円が大きく膨らむ機能の追加。
