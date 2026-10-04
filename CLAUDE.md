# Habit Tracker Development Rules

## Source of truth

仕様は `docs/` 配下のMarkdownファイルを唯一の正として扱う。

実装前に必ず以下を確認すること。

- `docs/01_habit_tracker_requirements_ui.md`
- `docs/02_habit_tracker_architecture.md`
- `docs/03_habit_tracker_database_design.md`
- `docs/04_habit_tracker_rest_api_design.md`

仕様と実装が矛盾する場合、勝手に仕様変更せず指摘すること。

## Development style

このプロジェクトはTDDで開発する。

必ず以下の順番で進める。

1. `TODO.md` から今回実装する小さな振る舞いを1つ選ぶ
2. 適切なテストレベルを決める
3. その振る舞いを表すテストを書く
4. テストが意図した理由で失敗することを確認する（Red）
5. テストを通すための最小限の実装を行う（Green）
6. 全テストを実行する
7. 必要な場合のみリファクタリングする（Refactor）
8. 再度全テストを実行する
9. `TODO.md` の該当項目を完了にする
10. 今回の変更内容を説明して停止する

一度に複数機能を実装しない。

次のTODOへ勝手に進まない。

## Testing strategy

テストは以下を使い分ける。

### Unit Test

外部依存を持たないロジックを対象とする。

例:

- バリデーション
- 日付計算
- 月の日数計算
- 集計ロジック
- utility
- 純粋なserviceロジック

DBやHTTPを大量にMockして無理にUnit Test化しない。

### Integration Test

BackendのAPIではIntegration Testを中心とする。

可能な限り以下の経路を実際に通してテストする。

`HTTP → FastAPI → SQLAlchemy → PostgreSQL`

以下のようなものを対象とする。

- GoalのCRUD
- HabitRecordのCRUD
- DB制約
- 重複チェック
- REST APIのレスポンス
- Monthly Summary API

内部実装そのものではなく、外部から観測できる振る舞いをテストする。

### E2E Test

FrontendとBackendが接続された後に、Playwrightで重要なユーザーフローをテストする。

例:

- 目標を登録できる
- 目標を編集できる
- 目標を削除できる
- カレンダーから○△×を登録できる
- ステータスを変更できる
- 空白に戻せる
- 月を切り替えられる

細かいバリデーションをすべてE2Eでテストしない。

すべての機能にUnit / Integration / E2Eを全部書く必要はない。

その振る舞いを最も適切に保証できるテストレベルを選択する。

## Implementation policy

- 必要以上の抽象化をしない
- 将来必要になるかもしれない機能を先回りして実装しない
- docsに存在しない機能を追加しない
- 最小限のコードでテストを通す
- マジックナンバーを避ける
- ステータス値は定義されたEnumを使用する
- DB制約で保証できるものはDB制約も使用する
- APIはRESTリソース単位で分離する
- 画面専用の巨大なAPIを作らない

## Backend

Backend:

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

Testing:

- pytest

## Frontend

Frontend:

- Vue 3
- TypeScript
- Composition API
- `<script setup lang="ts">`
- Vue Router
- native fetch
- CSS
- Piniaは使用しない

Testing:

- Vitest
- Vue Test Utils

コンポーネントの責務を小さく保つ。

## E2E

E2E Testing:

- Playwright

主要なユーザーフローのみを対象とする。

## Communication

各TDDサイクルの開始時に以下を説明する。

- 今回実装する振る舞い
- 使用するテストレベル
- なぜそのテストレベルなのか
- 最初に作成するテスト
- 変更予定ファイル

各TDDサイクル終了時に以下を説明する。

- 追加したテスト
- 実装した内容
- テスト結果
- 今回のTDDで学ぶべきポイント

そのTODOが完了したら停止する。

次のTODOには進まない。
