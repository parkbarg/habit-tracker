# Habit Tracker - REST API設計

Goal・HabitRecord・MonthlySummaryを分離したREST APIを定義する。

**Version 1.0 | 2026-10-04**

## 1. API設計原則

- 画面単位で必要データを全部まとめるdashboard APIは作らない。
- Goal、HabitRecord、MonthlySummaryを独立したリソースとして扱う。
- レスポンスは`data`キーでラップせず、配列またはオブジェクトを直接返す。
- MVPでは認証ヘッダーは不要。
- APIプレフィックスは `/api` とする。

## 2. Goal API

| Method | Path | 用途 | 主な結果 |
| --- | --- | --- | --- |
| GET | `/api/goals` | 目標一覧取得 | `200 + Goal[]` |
| POST | `/api/goals` | 目標登録 | `201 + Goal` |
| GET | `/api/goals/{goal_id}` | 単一目標取得 | `200 + Goal` |
| PATCH | `/api/goals/{goal_id}` | 目標名変更 | `200 + Goal` |
| DELETE | `/api/goals/{goal_id}` | 目標完全削除 | `204` |

### `POST /api/goals`

Request:

```json
{
  "name": "SC勉強"
}
```

Response `201 Created`:

```json
{
  "id": 1,
  "name": "SC勉強",
  "created_at": "2026-10-04T17:00:00+09:00",
  "updated_at": "2026-10-04T17:00:00+09:00"
}
```

同名（大文字・小文字無視）の目標が存在する場合は `409 Conflict`。1〜30文字などの入力不正は `422 Unprocessable Entity`。

## 3. HabitRecord API

| Method | Path | 用途 | 主な結果 |
| --- | --- | --- | --- |
| GET | `/api/goals/{goal_id}/records?year={y}&month={m}` | 対象月の日別記録取得 | `200 + HabitRecord[]` |
| PUT | `/api/goals/{goal_id}/records/{date}` | ○△×を作成または置換 | `200 + HabitRecord` |
| DELETE | `/api/goals/{goal_id}/records/{date}` | 空白へ戻す | `204` |

### `PUT /api/goals/{goal_id}/records/{date}`

Request:

```json
{
  "status": 1
}
```

Response `200 OK`:

```json
{
  "goal_id": 1,
  "record_date": "2026-10-08",
  "status": 1
}
```

- PUTは同一 `(goal_id, date)` に対するupsertとして扱う。
- `status` は `1`, `2`, `3` のみ受け付ける。
- 未来日も受け付ける。
- 空白は `status=0` で送らずDELETEを使用する。

### `GET records` の例

```json
[
  {"goal_id": 1, "record_date": "2026-10-01", "status": 1},
  {"goal_id": 1, "record_date": "2026-10-02", "status": 2},
  {"goal_id": 1, "record_date": "2026-10-03", "status": 3}
]
```

## 4. Monthly Summary API

集計は画面表示用の派生リソースとして独立させる。GoalやHabitRecordのレスポンスには混ぜない。

| Method | Path | 用途 |
| --- | --- | --- |
| GET | `/api/monthly-summaries?year={y}&month={m}` | 全目標の月次集計を取得（トップ画面用） |
| GET | `/api/monthly-summaries/{goal_id}?year={y}&month={m}` | 1目標の月次集計を取得（ダッシュボード用） |

### 全目標の月次集計

```json
[
  {
    "goal_id": 1,
    "success": 18,
    "partial": 4,
    "failure": 3,
    "days_in_month": 31
  },
  {
    "goal_id": 2,
    "success": 12,
    "partial": 6,
    "failure": 7,
    "days_in_month": 31
  }
]
```

### 単一目標の月次集計

```json
{
  "goal_id": 1,
  "success": 18,
  "partial": 4,
  "failure": 3,
  "days_in_month": 31
}
```

## 5. 画面ごとのAPI呼び出し

### トップ画面

```text
GET /api/goals
GET /api/monthly-summaries?year=2026&month=10
```

Vue側では2リクエストを `Promise.all` で並列取得し、`goal_id` で結合して表を描画する。

### 目標ダッシュボード

```text
GET /api/goals/1
GET /api/goals/1/records?year=2026&month=10
GET /api/monthly-summaries/1?year=2026&month=10
```

3リクエストは独立しているため並列取得できる。これによりAPIの責務を分けつつ、待ち時間を抑える。

## 6. HTTPステータス

| Status | 用途 |
| --- | --- |
| `200 OK` | 取得・更新成功 |
| `201 Created` | 目標登録成功 |
| `204 No Content` | 削除成功 |
| `404 Not Found` | 存在しない`goal_id`など |
| `409 Conflict` | 目標名重複 |
| `422 Unprocessable Entity` | FastAPIの入力バリデーションエラー |
| `500 Internal Server Error` | 想定外のサーバーエラー |

## 7. フロントエンドのエラー処理

- `fetch` の `response.ok` を確認し、失敗時はレスポンス内容をトーストへ渡す。
- 成功時も「登録しました」「保存しました」等のトーストを右下に表示する。
- トーストは数秒後に自動で消え、手動で閉じられる。
