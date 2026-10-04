## TDDの進め方
- 1チェックボックス = 1サイクル
  - 次のTODOへ勝手に進まない
- テストレベルを振る舞いごとに選ぶ
  - Unit: 外部依存なしのロジック
  - Integration: API〜DBを実際に通す
  - E2E: 主要フローのみ
- 仕様の未定義は先に確定させる
  - 確定事項はTODO.mdに記録

## Setupタスクの完了条件
- テストの代わりに観察できる結果で判断
  - コンテナがhealthyになる
  - 必要なDBが存在する
  - 作り直してもデータが残る
- 確認できるまで完了にしない

## Docker ComposeのPostgreSQL
- named volumeでデータを保持
  - `down` では消えない
  - `down -v` で消える
- `pg_isready`でhealthcheck
- postgres:18はvolumeを`/var/lib/postgresql`にマウント

## 初期化SQL
- `/docker-entrypoint-initdb.d`に置く
- volumeが空の初回起動時だけ実行
  - 変更を反映するには`down -v`が必要
- テスト用DBを同じサービス内に作成
  - 開発用DBを壊さない

## uvでの依存追加
- 実行時の依存は`uv add`
  - SQLAlchemy, Alembic, psycopg, pydantic-settings
- 開発時の依存は`uv add --dev`
  - pytest, httpx（TestClientが使う）
  - 本番の実行環境には入らない
- 完了条件は観察できる結果
  - 各パッケージをimportできる
  - `pytest`が起動する（0件はexit 5）
- 非推奨の警告は仕様を変えずに報告
  - 例: TestClientのhttpx → httpx2

## 設定値の管理（core/config.py）
- 設定値はハードコードせず環境変数から読む
  - 開発・Docker・テストで接続先が変わってもコードはそのまま
    - ローカル: `localhost:5432/habit_tracker`
    - Docker: `db:5432/habit_tracker`
    - テスト: `localhost:5432/habit_tracker_test`
  - パスワードをGitの履歴に残さない
- 重要な設定にはデフォルト値を持たせない
  - 設定漏れで黙って開発用DBにつながる事故を防ぐ
  - 起動時に`ValidationError`で止まる
- pydantic-settingsの`BaseSettings`
  - `database_url: str` → 環境変数`DATABASE_URL`を読む（大文字・小文字は区別しない）
  - 型検証と必須チェックが自動で行われる
- `settings`はimport時に作られる
  - テストでは読み込む前に`DATABASE_URL`をテスト用DBに向ける
- Setupタスクの確認方法
  - 自前のロジックがなければテストは書かない（確かめられるのはライブラリの動作だけ）
  - コマンドで「設定あり → 読める」「未設定 → エラー」を観察する
  - `VAR=値 コマンド`、`env -u VAR コマンド`で1回だけ環境変数を変えられる

## DBセッション管理（db/session.py）
- `engine`: DBへの接続口
  - URLから作る。実際の接続は最初のSQL実行時
  - コネクションプールで接続を使い回す
  - アプリ全体で1つ
- `SessionLocal`: Sessionを作る工場
  - Session = DB操作の作業単位（トランザクションを持つ）
  - 1リクエストに1つ作る（共有すると状態が混ざる）
- `get_db()`: FastAPIの依存関数
  - `Depends(get_db)`でエンドポイントに渡す
  - `yield`の前が準備、後が後片付け
  - `finally`で例外時も必ず`close()`
- 関数に分けておくとテストで差し替えられる

## Sessionとトランザクションの違い
- トランザクション: DB（PostgreSQL）の機能
  - 「全部確定 or 全部取り消し」の単位
  - `BEGIN`〜`COMMIT`/`ROLLBACK`の短い区間
- Session: SQLAlchemy（Python側）の機能
  - DB操作の窓口。読み込んだオブジェクトも覚えている
  - 寿命は1リクエスト（作成〜`close()`）
  - トランザクションの開始・確定を代わりに行う
- 1つのSessionの中でトランザクションが何回も起きる
  - `commit()`/`rollback()`で終わり、次のSQLで自動的に新しく始まる
- たとえ: Session = 銀行の窓口担当、トランザクション = 1枚の伝票
- テストでは外側にもう1つトランザクションを張る
  - Sessionのcommitは内側（SAVEPOINT）の確定だけ
  - 最後に外側ごと取り消す

## pytestの土台（conftest.py）
- conftest.py
  - pytestがテストより先に自動で読み込む
  - fixtureは引数名を書くだけで使える（import不要）
- 接続先の固定
  - backendのimport前に`setdefault`で`DATABASE_URL`を設定
  - `# noqa: E402`: import位置のルールを意図的に破る印
  - DB名がテスト用でなければ`pytest.exit`で止める（ルールをコードで強制）
- `db_session`: ロールバックでデータを分離
  - テスト全体を外側のトランザクションで包む
  - `create_savepoint`: アプリのcommitはSAVEPOINT止まり
  - 終了時にROLLBACKして変更が全部消える
  - テーブル作り直しより速く、消し忘れもない
- `client`: HTTPでアプリを呼ぶ
  - `dependency_overrides`で`get_db`を`db_session`に差し替え
  - 本番コードを変えずに接続方法だけ入れ替える
  - `TestClient`はサーバーを起動せずにリクエストできる
  - 終了時に`clear()`して次のテストに残さない
- Setupタスクの確認
  - 一時テストで観察し、確認後に消す

## backendコンテナ（Dockerfile / compose）
- Dockerfileは依存→ソースの順にCOPY
  - 依存のレイヤーがキャッシュされる
  - ソースだけ変えたときのビルドが速い
  - `uv sync --frozen`: uv.lockどおりに入れる
  - `--no-dev`: pytestなどは入れない
- コンテナからDBへは`db`で接続
  - コンテナ内の`localhost`は自分自身
  - composeのサービス名がホスト名になる
- `depends_on`+`service_healthy`
  - DBが接続を受け付けてから起動する
- 開発用の設定
  - `src`をマウント + `--reload`で変更が即反映
  - `.dockerignore`で`.venv`をビルドに含めない
- Setupタスクの確認
  - 確認用APIは足さず`/openapi.json`の応答を見る
  - コンテナ内でアプリの`engine`を使い接続確認
  - ホストからも`curl`（ポート公開の確認）
