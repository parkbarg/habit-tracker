## Q. 外側にもう1つトランザクションを張るとは？
- テストのコードが自分で`BEGIN`〜`ROLLBACK`を張ること
  - conftest.pyの`transaction = connection.begin()`がこれ
- 何の外側か → アプリ（Session）のトランザクションの外側
  - 外側: テストのコードの`BEGIN`〜`ROLLBACK`
  - 内側: Sessionの`SAVEPOINT`〜`RELEASE SAVEPOINT`
- 目的: アプリの`commit()`を受け止めつつ、最後に全部取り消す
  - 本番コードは変えない
  - テストごとにデータが消える

## Q. テスト用のセッションを作ればいいのでは？
- 実際にテスト用セッション（`db_session`）は作っている
- ただしセッションを分けるだけではデータは消えない
  - `commit()`は本物の`COMMIT`を送る
  - 確定したものは後から`rollback()`しても戻らない
- だから外側のトランザクションに参加させたセッションを作る
- 他の方法との比較
  - 毎回`TRUNCATE`/`DELETE`: 遅い、消し忘れが起きる
  - 毎回テーブル作り直し: もっと遅い
  - アプリで`commit()`しない: 本番コードをテストの都合で変えることになる

## Q. 接続を2本にする（`connect()`を2回）のでは？
- 包む対象は接続ではなくトランザクション
  - 接続: PythonとPostgreSQLの通信路
  - トランザクション: その通信路の上の「全部確定 or 全部取り消し」の区間
- 入れ子は同じ接続の上で重ねる
  - 別の接続は無関係な別のお客さん
  - 別の接続で`COMMIT`したものは外側の`ROLLBACK`で消えない
- `bind=connection`でSessionに同じ接続を使わせる
- SQLAlchemy 2.0の`Connection`に`.connect()`はない

## Q. ふつうのセッション作成のコードは？
- `db/session.py`
  - `engine = create_engine(...)`: DBの場所を覚える、接続の貸し出し係
  - `SessionLocal = sessionmaker(bind=engine)`: セッションの工場
  - `db = SessionLocal()`: セッションを1つ作る
- `connect()`も`begin()`も自分では書かない

## Q. 「engineから接続を借りる」とは？
- 接続を張るのは遅い（ネットワーク、認証）
- engineは張った接続を捨てずに取っておく（コネクションプール）
  - 使うとき: 空いている接続を借りる
  - `close()`: 切らずにengineへ返す

## Q. なぜ`return db`ではなく`yield db`？
- やりたいこと: 作る → APIで使う → APIの後でclose
- `return`だと関数が終わり、後でcloseできない
- `yield`は「渡して一時停止」
  - FastAPIがレスポンス後に続き（`finally`の`close()`）を実行する

## Q. commitの前にcloseすればいいのでは？
- commitせずcloseすればデータは捨てられる（考え方は正しい）
- ただし`commit()`を書くのはテストではなく本番のAPI
  - 本番では保存したいので消せない
  - テストからは止められない
- 「本番はcommitさせる」と「テストでは後から取り消す」を両立したい
  - → 外側のトランザクション

## Q. なぜdbを返す（渡す）必要があるの？
- 渡す相手はAPI（エンドポイント）
  - `db: Session = Depends(get_db)`でFastAPIが引数に入れる
- APIの中で`SessionLocal()`を直接呼ばない理由
  - 全APIに作る・try・closeを書くことになる
  - テストで差し替えられない
- `app.dependency_overrides[get_db] = lambda: db_session`
  - APIは外から受け取るだけなので、中身が変わっても気づかない

## Q. engineからセッションを作るってこと？
- 本番: `bind=engine`
  - SQLを送るときにセッションが自動で接続を借りる
- テスト: `bind=connection`
  - テストのコードが先に借りて`BEGIN`済みの接続を渡す

| | 本番 | テスト |
|---|---|---|
| `bind=` | `engine` | `connection` |
| 接続を借りる人 | セッション（自動） | テストのコード（手動） |
| `BEGIN`を送る人 | セッション（自動） | テストのコード（手動、外側） |
| `commit()`で送るもの | `COMMIT` | `RELEASE SAVEPOINT` |

## Q. ふつうはセッションを作ってbeginする？
- そうだが`begin`は自分で書かない
  - 最初にSQLを送るときセッションが自動で`BEGIN`（autobegin）
- テストではこれを先に手動でやっておく
  - セッションは`BEGIN`の代わりに`SAVEPOINT`を作る
  - `join_transaction_mode="create_savepoint"`の意味

## Q. なぜ`RELEASE SAVEPOINT`を送る？
- 始めた人が終わらせる
  - 外側の`BEGIN` → テストのコードが`ROLLBACK`
  - `SAVEPOINT` → セッションが`RELEASE`
- `COMMIT`は今のトランザクションを全部確定する
  - 内側だけ確定はできない
  - 送ると外側ごと確定し、データが残る
- `RELEASE SAVEPOINT`は「区切りの中はOK」と記録するだけ
  - 外側は続いている → 最後の`ROLLBACK`で全部消える

## 実際のSQLログ（`echo=True`で確認）
- ① ふつう（`get_db`と同じ）→ 終了後1件（残る）
  ```sql
  BEGIN (implicit)                      -- セッションが自動で
  INSERT INTO demo_goals ...
  COMMIT                                -- アプリのcommit()
  ```
- ② テスト（`db_session`と同じ）→ 途中1件見える、終了後0件（消える）
  ```sql
  BEGIN (implicit)                      -- 外側: connection.begin()
  SAVEPOINT sa_savepoint_1              -- 内側: セッションが作る
  INSERT INTO demo_goals ...
  RELEASE SAVEPOINT sa_savepoint_1      -- アプリのcommit()
  SAVEPOINT sa_savepoint_2              -- 次のSQL用に自動で新しい区切り
  SELECT count(*) FROM demo_goals       -- 1件見える
  ROLLBACK TO SAVEPOINT sa_savepoint_2  -- session.close()
  ROLLBACK                              -- 外側: transaction.rollback()
  ```
- ②に`COMMIT`は一度も出てこない
- 外側の`BEGIN`〜`ROLLBACK`が全体を包んでいる

## Q. セッションの外にトランザクションは存在できる？
- できる。トランザクションはPostgreSQLの機能
  - PostgreSQLに届くのは`BEGIN`/`COMMIT`などのSQLだけ
  - 誰が送ったか（Session、`connection.begin()`、psql）は区別しない
- 接続さえあればセッションなしで張れる
- Sessionは`BEGIN`/`COMMIT`を代わりに送る便利係

## Q. じゃあなぜセッションを作る？
- セッションの仕事は大きく2つ
  1. オブジェクトとDBの行をつなぐ
     - `db.add(goal)`からINSERTを作る
     - 行を`Goal`オブジェクトにする
     - 変更を覚えてUPDATEを作る
  2. トランザクションを代わりに管理する（自動`BEGIN`、`commit()`で`COMMIT`）
- テストで作る理由: APIが`Session`を受け取る前提
  - `db.add()`などを呼ぶので、Connectionを渡すとエラー
- fixtureでの分担
  - 接続: 外側のトランザクション（最後に消すため）
  - セッション: その接続の上に作ってAPIに渡す（1の役と`SAVEPOINT`の管理）

## Q. コードにトランザクションが見えないのはなぜ？
- 書かれていないだけで、必ず存在する
  - 最初のSQLで自動`BEGIN`（autobegin）
  - `commit()`はトランザクションを終わらせる命令
  - `commit()`の後、次のSQLで新しいトランザクションが自動で始まる
- PostgreSQLではSQLは必ずトランザクションの中で動く
  - `BEGIN`なしの1文も、その1文だけのトランザクションになる

## Q. Connectionだけで操作するとトランザクションを使わない？
- 使う。使っていないのはセッション
- SQLAlchemy 2.0ではConnectionも自動`BEGIN`する
  - `connection.commit()`しないと保存されない
  - commitせずに閉じると`ROLLBACK`
  - SQLログでも`BEGIN (implicit)` → `SELECT` → `ROLLBACK`を確認

| | トランザクション | オブジェクトとして扱う |
|---|---|---|
| Connection | 使う（自動BEGIN、`commit()`でCOMMIT） | できない（SQL文字列と行だけ） |
| Session | 使う（自動BEGIN、`commit()`でCOMMIT） | できる（`Goal`オブジェクト） |

## Q. `BEGIN`はトランザクションのこと？
- `BEGIN`はトランザクションを始める合図
- トランザクション = `BEGIN`から`COMMIT`/`ROLLBACK`までの区間全体
  - `BEGIN`: 始まり
  - `COMMIT`: 終わり（全部確定）
  - `ROLLBACK`: 終わり（全部取り消し）
- たとえ: トランザクション = 1枚の伝票
  - `BEGIN` = 書き始める、`COMMIT` = 提出、`ROLLBACK` = 破り捨てる
- `transaction = connection.begin()`
  - `BEGIN`を送り、始まった区間を表すオブジェクトを返す
  - `transaction.rollback()`でその区間を終わらせる
