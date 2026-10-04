# Habit Tracker - 技術構成・アーキテクチャ

MVPの技術スタック、責務分離、開発環境を定義する。

**Version 1.0 | 2026-10-04**

## 1. 技術スタック

| レイヤ | 採用技術 | 方針 |
| --- | --- | --- |
| Frontend | Vue 3 + TypeScript | Composition API / `<script setup lang="ts">` |
| Routing | Vue Router | 年月をURLクエリで保持 |
| State | Vue標準機能 | Piniaは使わない |
| HTTP | `fetch` | Axiosは使わない |
| Styling | Plain CSS | UIライブラリ・Tailwindは使わない |
| Backend | FastAPI + Python | REST API |
| ORM | SQLAlchemy | DBアクセス層として使用 |
| Migration | Alembic | スキーマ変更を履歴管理 |
| Database | PostgreSQL | 永続化 |
| Runtime | Docker Compose | frontend / backend / db をまとめて起動 |

## 2. システム構成

```text
PC Browser
    |
    v
Vue 3 + TypeScript
    |
    | fetch / JSON
    v
FastAPI (REST API)
    |
    | SQLAlchemy
    v
PostgreSQL
```

- フロントエンドは表示・入力・画面遷移を担当する。
- バックエンドはバリデーション、CRUD、月次集計、DBアクセスを担当する。
- DBは目標と日別記録の永続化のみを担当する。
- 月次集計ロジックはVueではなくFastAPI側に置く。

## 3. フロントエンド設計方針

- Vue Routerを使用し、トップは `/`、目標画面は `/goals/:goalId` とする。
- 選択年月は `?year=2026&month=10` のようにURLクエリへ保存する。
- Piniaは使用しない。画面固有の状態は `ref` / `computed`、親子連携は `props` / `emit` で扱う。
- API通信は標準`fetch`を利用し、必要に応じて `src/api` 配下に薄い関数をまとめる。
- 複数の独立したRESTリソースが必要な画面では `Promise.all` で並列取得してよい。
- APIレスポンスは `data` で包まず、リソースそのものをJSONとして返す。

### 推奨フロントエンド構成

```text
frontend/src/
├── api/
│   ├── goals.ts
│   ├── records.ts
│   └── summaries.ts
├── components/
│   ├── AppHeader.vue
│   ├── MonthSwitcher.vue
│   ├── GoalTable.vue
│   ├── GoalFormModal.vue
│   ├── DeleteConfirmModal.vue
│   ├── StatusCards.vue
│   ├── HabitCalendar.vue
│   ├── RecordEditModal.vue
│   └── ToastContainer.vue
├── views/
│   ├── GoalListView.vue
│   └── GoalDashboardView.vue
├── router/
│   └── index.ts
├── types/
│   ├── goal.ts
│   └── record.ts
├── App.vue
└── main.ts
```

## 4. バックエンド設計方針

- RESTリソース単位でAPIを分離する。画面専用の巨大なdashboard APIは作らない。
- Pydanticスキーマで入力・出力を型付けする。
- SQLAlchemyモデルとAPIスキーマを分離する。
- Statusは `1=SUCCESS`、`2=PARTIAL`、`3=FAILURE` のEnumとしてコード上で管理する。
- 同じ目標・同じ日付の記録は1件だけとする。
- 空白は `status=0` ではなく「レコードなし」として表現する。

### 推奨バックエンド構成

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── goals.py
│   │   ├── records.py
│   │   └── summaries.py
│   ├── models/
│   │   ├── goal.py
│   │   └── habit_record.py
│   ├── schemas/
│   │   ├── goal.py
│   │   ├── habit_record.py
│   │   └── summary.py
│   ├── services/
│   │   ├── goal_service.py
│   │   ├── record_service.py
│   │   └── summary_service.py
│   ├── db/
│   │   ├── session.py
│   │   └── base.py
│   └── core/
│       ├── config.py
│       └── enums.py
└── alembic/
```

## 5. Docker Compose

| Service | 役割 | 開発時の代表ポート |
| --- | --- | ---: |
| frontend | Vue開発サーバー | 5173 |
| backend | FastAPI / Uvicorn | 8000 |
| db | PostgreSQL | 5432 |

- `docker compose up` で3サービスを起動できる状態を目標とする。
- DBデータはnamed volumeで保持する。
- バックエンドは`db`サービス名をホスト名として接続する。
- 開発時のCORSはVue開発サーバーのoriginだけ許可する。

## 6. 認証の拡張方針

MVPでは認証を実装しない。将来、一般ユーザー対応へ拡張するときにユーザー登録・ログインを追加し、`goals` に `user_id` を追加してユーザー単位でデータを分離する。現段階では将来拡張を理由に認証コードを先行実装しない。

## 7. 実装順序

1. Docker ComposeでVue / FastAPI / PostgreSQLを起動する。
2. SQLAlchemyモデルとAlembic初期マイグレーションを作成する。
3. Goal REST APIを実装する。
4. HabitRecord REST APIを実装する。
5. Monthly Summary REST APIを実装する。
6. Vue Routerと月クエリ管理を実装する。
7. トップ画面を実装する。
8. ダッシュボードとカレンダーを実装する。
9. 登録・編集・削除・日付編集モーダルを実装する。
10. トースト、エラー処理、最終UI調整を行う。
