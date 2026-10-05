# TODO

TDDで1項目ずつ進める。1サイクル = 1チェックボックス。
進め方・テスト方針は `CLAUDE.md`、仕様は `docs/` を正とする。

テストレベルの表記:

- **[Setup]** 環境構築。振る舞いではないためテストは作らない（または動作確認のみ）
- **[Unit]** 外部依存なしのロジック
- **[Integration]** `HTTP → FastAPI → SQLAlchemy → PostgreSQL` を実際に通す
- **[Component]** Vitest + Vue Test Utils（fetchはテスト側で差し替える）
- **[E2E]** Playwright。主要ユーザーフローのみ

---

## 確定事項（docsの未定義・差異に対する決定）

docsと差異がある場合、実装ではここの決定を優先する。

- [x] **Backendのディレクトリ構成**: 既存のuv srcレイアウト `backend/src/backend/` を使用する（`docs/02` の `backend/app/` には変更しない）
- [x] **存在しない日のRecord DELETE**: Recordが存在しなくても `204`（冪等）。ただし `goal_id` 自体が存在しない場合は `404`
- [x] **全目標の月次集計**: 記録0件のGoalも必ず含め、`success=0, partial=0, failure=0, days_in_month=対象月の日数` を返す
- [x] **FrontendのURLクエリの年月**: 未指定・不正値の場合は現在の年月へフォールバックし、可能ならURLクエリも現在の年月に正規化する
- [x] **Backend APIの `year`/`month` 範囲**: `month` は1〜12、`year` は1〜9999を有効とし、範囲外は `422`
- [x] **Integration Test用DB**: 同じPostgreSQLサービス内に `habit_tracker`（開発用）と `habit_tracker_test`（テスト用）の2DBを用意する。Integration Testは必ず `habit_tracker_test` を使い、開発用DBを変更しない
- [x] **README.md**: 旧仕様のREADMEは使用しない。新仕様に合わせて後で書き直す（空のREADMEを最終状態にはしない）

---

## Phase 0: 開発環境

- [x] [Setup] `docker-compose.yml` に `db`（PostgreSQL, named volume）を追加し起動できる（`habit_tracker` と `habit_tracker_test` の2DB）
- [x] [Setup] backend の依存追加（SQLAlchemy, Alembic, psycopg, pydantic-settings, pytest, httpx）
- [x] [Setup] `core/config.py` で DB接続URLを環境変数から読み込む
- [x] [Setup] pytest の土台: `habit_tracker_test` へ接続し、テストごとにデータを分離するfixture、FastAPI `TestClient` fixture
- [x] [Setup] `docker-compose.yml` に `backend`（Uvicorn, port 8000）を追加し、`db` サービス名で接続できる

## Phase 1: Status Enum・日付ロジック（Backend Unit）

- [x] [Unit] `Status` Enum が `SUCCESS=1`, `PARTIAL=2`, `FAILURE=3` を持つ
- [ ] [Unit] 対象年月の日数を返す（31日月 / 30日月）
- [ ] [Unit] 2月の日数を返す（平年28日 / うるう年29日 / 100年・400年ルール）
- [ ] [Unit] 対象年月の初日・末日（記録検索の範囲）を返す

## Phase 2: DBモデル・マイグレーション

- [ ] [Integration] Alembic 初期マイグレーションで `goals` / `habit_records` が作成される（`alembic upgrade head` がテストDBで通る）
- [ ] [Integration] `goals` は `lower(name)` のUNIQUE INDEXにより大文字・小文字違いの同名を拒否する
- [ ] [Integration] `habit_records` は `(goal_id, record_date)` のUNIQUE制約で同一日の2件目を拒否する
- [ ] [Integration] `habit_records.status` は `CHECK(status IN (1,2,3))` で範囲外を拒否する
- [ ] [Integration] `goals` を削除すると `ON DELETE CASCADE` で `habit_records` も削除される

## Phase 3: Goal API

### POST /api/goals

- [ ] [Integration] 目標名を送ると `201` と `id, name, created_at, updated_at` を返す
- [ ] [Integration] 前後の空白を除去して保存する（`"  SC勉強  "` → `"SC勉強"`）
- [ ] [Integration] 空文字・空白のみの目標名は `422`
- [ ] [Integration] 30文字は登録でき、31文字は `422`（trim後の文字数で判定）
- [ ] [Integration] 既存と同名は `409`
- [ ] [Integration] 大文字・小文字だけ異なる同名は `409`（`abc` と `ABC`）
- [ ] [Integration] trim後に既存と同名になる場合は `409`

### GET /api/goals

- [ ] [Integration] 0件のとき `200` と空配列を返す
- [ ] [Integration] 登録順（`created_at ASC`, 同値時 `id ASC`）で返す

### GET /api/goals/{goal_id}

- [ ] [Integration] 存在する目標を `200` で返す
- [ ] [Integration] 存在しない `goal_id` は `404`

### PATCH /api/goals/{goal_id}

- [ ] [Integration] 目標名を変更し `200` で返す。`updated_at` が更新される
- [ ] [Integration] 変更時も trim・1〜30文字の検証を行う（不正は `422`）
- [ ] [Integration] 他の目標と同名（大文字・小文字無視）への変更は `409`
- [ ] [Integration] 自分自身の名前の大文字・小文字だけを変える変更は成功する
- [ ] [Integration] 存在しない `goal_id` は `404`

### DELETE /api/goals/{goal_id}

- [ ] [Integration] 目標を削除し `204`。以後 `GET` は `404`
- [ ] [Integration] 削除した目標の記録も削除される
- [ ] [Integration] 存在しない `goal_id` は `404`

## Phase 4: HabitRecord API

### PUT /api/goals/{goal_id}/records/{date}

- [ ] [Integration] 記録がない日に `status` を送ると作成し、`200` と `goal_id, record_date, status` を返す
- [ ] [Integration] 既に記録がある日に別の `status` を送ると置換する（2件にならない）
- [ ] [Integration] `status` が `1,2,3` 以外（`0`, `4` など）は `422`
- [ ] [Integration] 未来日も保存できる
- [ ] [Integration] 不正な日付文字列（`2026-02-30` など）は `422`
- [ ] [Integration] 存在しない `goal_id` は `404`

### DELETE /api/goals/{goal_id}/records/{date}

- [ ] [Integration] 記録を削除し `204`（空白に戻る）
- [ ] [Integration] 記録がない日の削除も `204`（冪等）
- [ ] [Integration] 存在しない `goal_id` は `404`

### GET /api/goals/{goal_id}/records?year=&month=

- [ ] [Integration] 対象月の記録だけを日付順で返す（前月末・翌月初の記録は含めない）
- [ ] [Integration] 記録がない月は空配列
- [ ] [Integration] 他の目標の記録は含めない
- [ ] [Integration] `year`/`month` 欠落・範囲外（`month` 1〜12, `year` 1〜9999）は `422`
- [ ] [Integration] 存在しない `goal_id` は `404`

## Phase 5: Monthly Summary

- [ ] [Unit] 記録のstatus一覧から `success / partial / failure` 件数を集計する（空白は数えない）
- [ ] [Integration] `GET /api/monthly-summaries/{goal_id}` が対象月の件数と `days_in_month` を返す
- [ ] [Integration] 単一集計: 対象月以外の記録を数えない
- [ ] [Integration] 単一集計: 記録0件の月は `0/0/0` と日数を返す
- [ ] [Integration] 単一集計: 存在しない `goal_id` は `404`
- [ ] [Integration] `GET /api/monthly-summaries` が全目標分の集計を返す
- [ ] [Integration] 全体集計: 記録0件の目標も `0/0/0` と `days_in_month` で含める
- [ ] [Integration] 両API: `year`/`month` 欠落・範囲外（`month` 1〜12, `year` 1〜9999）は `422`

## Phase 6: Frontend 土台

- [ ] [Setup] Vue 3 + TypeScript + Vite + Vue Router + Vitest の雛形を `frontend/` に作成
- [ ] [Setup] `docker-compose.yml` に `frontend`（port 5173）を追加
- [ ] [Setup] Backend の CORS で Vue開発サーバーのoriginだけ許可する
- [ ] [Setup] `types/goal.ts`, `types/record.ts` に型と Status 定義を置く

## Phase 7: Frontend ロジック（Unit）

- [ ] [Unit] URLクエリから年月を読み取る（未指定・不正値は現在の年月へフォールバック）
- [ ] [Component] 未指定・不正値のURLクエリを現在の年月に正規化する
- [ ] [Unit] 前月・翌月を計算する（1月→前年12月、12月→翌年1月）
- [ ] [Unit] 月曜始まりのカレンダーセル配列を作る（当月の日付のみ、前後は空セル）
- [ ] [Unit] カレンダーは常に42セル（6週）になる
- [ ] [Unit] 目標一覧と全体集計を `goal_id` で結合する
- [ ] [Unit] 件数表示を `18 / 31` 形式に整形する

## Phase 8: API クライアント（`src/api`）

- [ ] [Unit] `api/goals.ts`: 一覧・取得・登録・変更・削除が正しいメソッド/パス/ボディで `fetch` する
- [ ] [Unit] `api/records.ts`: 月取得・PUT・DELETE が正しいパスで `fetch` する
- [ ] [Unit] `api/summaries.ts`: 全体・単一の集計を正しいクエリで取得する
- [ ] [Unit] `response.ok` が false のとき、レスポンス内容を含むエラーを投げる

## Phase 9: 共通コンポーネント

- [ ] [Component] `AppHeader`: 「Habit Tracker」を表示し、クリックでトップへ遷移する
- [ ] [Component] `AppHeader`: 目標名が渡されたとき「Habit Tracker / 目標名」と表示する
- [ ] [Component] `MonthSwitcher`: `< 2026年10月 >` 形式で表示する
- [ ] [Component] `MonthSwitcher`: 左右矢印で前月・翌月を emit する
- [ ] [Component] `ToastContainer`: メッセージを右下に表示し、数秒後に自動で消える
- [ ] [Component] `ToastContainer`: 閉じるボタンで手動で消せる

## Phase 10: トップ画面

- [ ] [Component] `GoalTable`: 列順「目標名 → ○ → △ → × → ⋮」で行を表示する
- [ ] [Component] `GoalTable`: 0件でも空の表（ヘッダー）を表示する
- [ ] [Component] `GoalTable`: 行クリックで `goal_id` を emit する
- [ ] [Component] `GoalTable`: `⋮` メニューから「編集」「削除」を emit する
- [ ] [Component] `GoalListView`: URLクエリの年月で目標一覧と全体集計を取得して表示する
- [ ] [Component] `GoalListView`: 月切り替えでURLクエリが変わり再取得する
- [ ] [Component] `GoalListView`: 行クリックで `/goals/:goalId` へ年月クエリを引き継いで遷移する

## Phase 11: 目標の登録・編集・削除

- [ ] [Component] `GoalFormModal`: 目標名を入力して送信を emit する
- [ ] [Component] `GoalFormModal`: 編集時は既存の目標名を初期表示する
- [ ] [Component] 登録成功で一覧を再取得し「目標を登録しました」をトースト表示する
- [ ] [Component] 編集成功で「変更を保存しました」をトースト表示する
- [ ] [Component] APIエラー（409/422など）時にエラー内容をトースト表示する
- [ ] [Component] `DeleteConfirmModal`: 確認後のみ削除を emit し、キャンセルでは何もしない
- [ ] [Component] 削除成功で一覧から消え「目標を削除しました」をトースト表示する

## Phase 12: 目標ダッシュボード

- [ ] [Component] `StatusCards`: ○(緑系)・△(黄系)・×(赤系)の3枚を「件数 / 日数」で表示する
- [ ] [Component] `HabitCalendar`: 「月 火 水 木 金 土 日」の曜日ヘッダーと当月の日付を表示する
- [ ] [Component] `HabitCalendar`: 記録の status に応じてセル背景を緑/黄/赤/白にする（文字・バッジは出さない）
- [ ] [Component] `HabitCalendar`: 日付セルクリックで日付を emit し、空セルはクリック不可
- [ ] [Component] `GoalDashboardView`: 目標・月の記録・単一集計を並列取得して表示する
- [ ] [Component] `GoalDashboardView`: 月切り替えでURLクエリが変わり再取得する

## Phase 13: 日付編集モーダル

- [ ] [Component] `RecordEditModal`: 「○ / △ / × / 空白」を選べ、現在の状態が初期選択される
- [ ] [Component] `RecordEditModal`: 選択しただけでは emit せず、「保存」で確定を emit する
- [ ] [Component] `RecordEditModal`: 「キャンセル」で変更せず閉じる
- [ ] [Component] ○△×の保存で PUT を呼び、カレンダーとカードを更新し「記録を保存しました」を表示する
- [ ] [Component] 空白の保存で DELETE を呼び、セルが白に戻る
- [ ] [Component] 保存失敗時に「保存に失敗しました」を表示する

## Phase 14: E2E（主要フローのみ）

- [ ] [Setup] Playwright を導入し、docker compose 起動環境に対して実行できる
- [ ] [E2E] 目標を登録できる
- [ ] [E2E] 目標を編集できる
- [ ] [E2E] 目標を削除できる
- [ ] [E2E] カレンダーから○△×を登録できる
- [ ] [E2E] 登録済みのステータスを変更できる
- [ ] [E2E] 空白に戻せる
- [ ] [E2E] 月を切り替えられる（トップ → ダッシュボードで年月が引き継がれる）
