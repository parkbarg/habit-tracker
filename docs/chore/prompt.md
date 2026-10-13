## TODO.md
`habit-tracker/docs/` 配下の仕様書をすべて読んでください。

このHabit Trackerを、私がテスト駆動開発を学びながら、一つずつ実装していきたいです。

私はTDD初心者です。

まず実装はしないでください。
最初に、このプロジェクト全体の開発TODOとテスト戦略を作成してください。

## 目的

以下の3種類のテストを適切に使い分けながら開発したいです。

- Unit Test
- Integration Test
- E2E Test

すべての機能に3種類すべてを書く必要はありません。
その振る舞いを最も適切に保証できるテストレベルを選んでください。

## TODOの作成ルール

TODOは実装順に並べてください。

1つのTODOは、できるだけ小さな振る舞いにしてください。

悪い例:

- Goal機能を作る
- Backendを完成させる
- Dashboardを作る

良い例:

- 正常な目標名でGoalを登録できる
- 空文字の目標名を拒否できる
- 31文字以上の目標名を拒否できる
- 登録済みGoal一覧を取得できる

各TODOには必ず以下を書いてください。

### TODO名
何を実現するタスクなのか

### テストレベル
以下から選択してください。

- Unit
- Integration
- E2E
- 必要なら複数

### なぜそのテストレベルなのか
初心者にも分かるように簡潔に説明してください。

### Red
最初にどんな失敗テストを書くか

### Green
テストを通すために最低限何を実装するか

### Refactor
Green後に必要なら何を整理するか

### 完了条件
何を確認できればそのTODOを完了とするか

## テスト方針

基本方針は以下にしてください。

### Unit Test

以下のような、外部依存のないロジックに使う。

- バリデーション
- 日付計算
- 月の日数計算
- statusの変換
- 集計ロジック
- utility / serviceの純粋なロジック

DBやHTTPを無理にMockしてUnit Test化しないでください。

### Integration Test

BackendではIntegration Testを中心にしてください。

以下の連携を実際に確認したいです。

FastAPI
→ SQLAlchemy
→ テスト用PostgreSQL

APIのCRUDについては、可能な限りHTTPリクエストからテストしてください。

例:

POST /api/goals
→ FastAPI
→ SQLAlchemy
→ PostgreSQL
→ Response

Mockだらけのテストにはしないでください。

### E2E Test

FrontendとBackendが接続された後に導入してください。

Playwrightを使う想定です。

重要なユーザーフローだけE2Eにしてください。

例:

- UIから目標を登録できる
- UIから目標を編集できる
- UIから目標を削除できる
- カレンダーから○△×を登録できる
- 空白に戻せる
- 月を切り替えられる

細かいバリデーションをすべてE2Eで確認しないでください。

## 開発順序

依存関係を考えて、

環境構築
↓
Backend
↓
Frontend
↓
E2E

を基本にしてください。

ただし、より良い順序がある場合は理由を説明してください。

## 重要

- `docs/` を仕様の唯一の正とする
- docsにない機能を勝手に追加しない
- まだコードを変更しない
- TODOだけを作る
- TODOはチェックボックス形式にする
- 各TODOに Unit / Integration / E2E の分類を付ける
- 私がTDD初心者なので、なぜそのテストを書くのかも説明する
- 一度に巨大な機能を扱わず、小さなRed → Green → Refactorに分割する

最後に、

1. 全TODO
2. テスト全体戦略
3. 最初に取り組むTODO
4. その最初のTODOで最初に書くテスト

を提示してください。

実装はせず、そこで停止してください。

## TODO.md1
`habit-tracker/docs/` 配下の仕様書をすべて読んでください。

このプロジェクトを、TDDを学びながら一つずつ開発したいです。
私はTDD初心者です。

まだ実装はしないでください。

まず `TODO.md` を作成してください。

TODOは実装順に、小さな振る舞い単位まで分解してください。

各TODOには以下を記載してください。

- 実装する振る舞い
- テスト種別: Unit / Integration / E2E
- なぜそのテスト種別なのか
- Redで最初に書くテスト
- Greenで最低限実装する内容
- 完了条件

テスト方針は以下です。

- 純粋なロジックや計算はUnit Test
- FastAPI → SQLAlchemy → PostgreSQLを通るAPIはIntegration Test
- Vue → FastAPI → PostgreSQLを実際のブラウザ操作で確認する主要フローはE2E Test
- BackendのCRUDを無理にMockしてUnit Testにしない
- すべての機能にUnit / Integration / E2Eを全部書く必要はない
- E2Eは重要なユーザーフローだけにする

使用予定:

Backend:
- pytest

Frontend:
- Vitest
- Vue Test Utils

E2E:
- Playwright

仕様の唯一の正は `docs/` としてください。
docsに存在しない機能を追加しないでください。

TODOは依存関係を考慮して実装順に並べてください。

最初は、

環境構築
→ Backend
→ Frontend
→ E2E

を基本としてください。

今回はTODOの作成だけ行ってください。
コードは変更しないでください。

最後に「最初に取り組むTODO」を1つだけ教えて、停止してください。


