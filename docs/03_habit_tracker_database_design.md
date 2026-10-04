# Habit Tracker - データベース設計

PostgreSQLに保存するMVPデータモデルと制約を定義する。

**Version 1.0 | 2026-10-04**

## 1. ER概要

```text
goals (1) -------- (N) habit_records
  id                    goal_id
                        record_date
                        status
```

日の種類・祝日・ユーザー情報はMVPでは保持しない。

## 2. `goals` テーブル

| 列 | 型 | NULL | 制約・用途 |
| --- | --- | :---: | --- |
| `id` | BIGSERIAL / BIGINT | NO | Primary Key |
| `name` | VARCHAR(30) | NO | 前後空白除去後、1〜30文字 |
| `created_at` | TIMESTAMPTZ | NO | 登録順表示に使用 |
| `updated_at` | TIMESTAMPTZ | NO | 更新日時 |

- 一覧の並び順は `created_at ASC`（同値時は `id ASC`）。
- 目標名は大文字・小文字を区別せず重複禁止。
- PostgreSQLでは `lower(name)` に対するUNIQUE INDEXを作る。アプリ側では保存前にtrimする。

```sql
CREATE UNIQUE INDEX uq_goals_name_lower
ON goals (lower(name));
```

## 3. `habit_records` テーブル

| 列 | 型 | NULL | 制約・用途 |
| --- | --- | :---: | --- |
| `id` | BIGSERIAL / BIGINT | NO | Primary Key |
| `goal_id` | BIGINT | NO | FK → `goals.id`, `ON DELETE CASCADE` |
| `record_date` | DATE | NO | 記録対象日 |
| `status` | SMALLINT | NO | `1=○`, `2=△`, `3=×` |
| `created_at` | TIMESTAMPTZ | NO | 作成日時 |
| `updated_at` | TIMESTAMPTZ | NO | 更新日時 |

- `(goal_id, record_date)` にUNIQUE制約を付け、1目標・1日につき1記録だけにする。
- `status` には `CHECK(status IN (1, 2, 3))` を付ける。
- 空白はレコードを保存しない。空白へ変更した場合は該当レコードをDELETEする。
- 未来日もDATEとして通常どおり保存できる。

```sql
UNIQUE (goal_id, record_date)
CHECK (status IN (1, 2, 3))
```

## 4. ステータス定義

| DB値 | Backend Enum | 意味 | UI |
| --- | --- | --- | --- |
| `1` | `SUCCESS` | 達成 | セル全体を薄い緑 |
| `2` | `PARTIAL` | 一部達成 | セル全体を薄い黄 |
| `3` | `FAILURE` | 未達 | セル全体を薄い赤 |
| レコードなし | - | 空白 / 未設定 | 白 |

## 5. 月次集計

月次集計は保存せず、`habit_records` からFastAPI側で算出する。分母は常に対象年月の日数であり、空白数や現在日には依存しない。

```text
success_count = status=1 の件数
partial_count = status=2 の件数
failure_count = status=3 の件数
days_in_month = 対象年月の日数
```

例：2026年10月なら、記録が○18件・△4件・×3件・空白6日でも表示は「○ 18/31、△ 4/31、× 3/31」とする。

## 6. 削除ルール

- 目標削除は物理削除。論理削除・アーカイブはMVPでは行わない。
- `goals` 削除時は `ON DELETE CASCADE` で `habit_records` も削除する。
- 日別記録を空白に戻す場合は `habit_records` の該当行だけ削除する。

## 7. Alembic方針

- 初期マイグレーションで `goals` と `habit_records` を作成する。
- 制約・インデックスもAlembicで管理する。
- 将来認証を追加するときは `users` テーブルを追加し、`goals.user_id` を追加する新規マイグレーションを作る。
