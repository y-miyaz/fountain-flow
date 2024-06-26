## ⛲ 概要 ⛲

`fountain-flow`は負荷試験向けのデータ生成ツールです。簡単な操作で、設定したルールに従ったデータの大量生成、DBへのデータ投入が可能です。

### ユースケース
`fountain-flow`は以下のようなケースでの利用を想定しています。

- アプリケーションのパフォーマンステスト
- DBのパフォーマンスチューニング
- DBのスケーラビリティテスト
- プロトタイプ・製品のデモンストレーション

:warning:`fountain-flow`はDBの破壊的操作が可能なため、稼働中の本番環境への利用は推奨しません。

### 基本機能
`fountain-flow`は以下の機能を提供します。

- データ生成定義からのDBへの直接データ投入
- データ生成定義からのCSVファイル, jsonファイル出力
- CSV ファイル, jsonファイルからのデータロード

## 動作要件

:warning:`fountain-flow`は進行中のプロジェクトです。変更が行われる可能性があります.

### 動作環境

- Python 3.12 (tested under Python 3.12.3)
- pip (tested under pip 24.0)

### 対応する DB

| データベース               | CSV 対応 | INSERT コマンド対応 |
| -------------------------- | -------- | ------------------- |
| Postgres                   | ○        | ○                   |
| Mysql                      | ○        | ○                   |
| Oracle Database            | ☓        | ☓                   |
| Microsoft SQL Server       | ☓        | ☓                   |
| MariaDB                    | ☓        | ☓                   |
| Amazon RDS                 | ○        | ○                   |
| Amazon RDS serverless      | ○        | ○                   |
| Amazon Redshift            | ○        | ○                   |
| Amazon Redshift Serverless | ○        | ○                   |
| Cassandra                  | ☓        | ☓                   |
| MongoDB                    | ☓        | ☓                   |
| Amazon Dynamo DB           | ○        | ○                   |
| Amazon Neptune             | ☓        | ☓                   |
| Snowflake                  | ☓        | ☓                   |
| IBM Db2                    | ☓        | ☓                   |
| Google BigQuery            | ☓        | ☓                   |
| Apache Hive                | ☓        | ☓                   |
| SQLite                     | ☓        | ☓                   |

## パッケージインストール

アプリケーションに必要なパッケージをインストールするためには以下のコマンドを実行します:

```sh
# install packages
pip install -r requirements.txt
```

## アプリケーションの実行

アプリケーションを実行するためには、以下のコマンドを実行します。
環境情報は database.yaml で設定します。

```sh
# fountain-flowを実行する
# 環境を指定して実行する場合（例: mysql環境で実行）
bin/fountain-flow run --env mysql

# 環境を指定せずに実行する場合 (default環境)
bin/fountain-flow run
```

## 定義(data.yaml)の生成

fountain-flow ではデータ生成のためのデータ定義ファイル(data.yaml)の設定が必要です。定義ファイルは手動で作成するほか、定義を生成するコマンドを実行することで、def/data.yaml に雛形が作成されます。

```sh
bin/fountain-flow create-def path/to/ddl1.sql path/to/ddl2.sql
```

コマンドの使用方法やオプションについての詳細は、以下のコマンドでヘルプを表示できます。

```sh
# ヘルプメッセージを表示
bin/fountain-flow -help
```

## アプリケーション設定

`fountain-flow`は以下の 3 つの設定ファイルを持ちます。

- **ファイルパス**:
  - `config/database.yaml`
  - `config/settings.yaml`
  - `definition/data.yaml`

以下に、 `database.yaml`, `settings.yaml`, `data.yaml` のファイルの構造と使用方法について説明します。

## `database.yaml`

### 概要

database.yaml では`fountain-flow`の接続先のデータベースの設定を行います。

### 設定ファイルの項目

以下の項目が設定ファイルに含まれます：

- `環境名`: 接続先データベースの環境名（必須）。
  - **`type`**: DB を指定します（任意）。選択肢は`postgres`, `mysql`, `rds`, `redshift`, `redshift_serverless`, `dynamodb`。指定されない場合は`postgres`が設定される。
  - **`host`**: データベースサーバーのホスト名、クラスタ名、ワークグループ名、またはIPアドレス（必須）。
  - **`port`**: データベースサーバーのポート番号（必須）。PostgreSQL のデフォルトポートは 5432。`postgres`, `mysql`のみ。
  - **`dbname`**: 接続するデータベースの名前（必須）。
  - `user`: データベースへの接続に使用するユーザー名（必須）。`postgres`, `mysql`のみ。
  - **`password`**: 上記ユーザーのパスワード（必須）。`postgres`, `mysql`のみ。
  - **`region`**: 接続先の AWS リージョンを指定します。`rds`, `redshift`, `redshift_serverless`, `dynamodb`のみ。
  - **`profile`**: 接続に使用する認証情報のプロファイルを指定します。`rds`, `redshift`, `redshift_serverless`, `dynamodb`のみ。指定しない場合は defalut プロファイルが使用されます。
  - **`bucket_name`**: CSV ロードの際に CSV ファイルをアップロードする S3 バケット名を指定します。`rds`, `redshift`, `redshift_serverless`, `dynamodb`のみ。
  - **`object_key`**: CSV ロードの際にアップロードするオブジェクトキーを指定します。`rds`, `redshift`, `redshift_serverless`, `dynamodb`のみ。
  - **`iam_role`**: CSV ロードの際に使用する IAM ロールを指定します。`redshift`, `redshift_serverless`のみ。あらかじめ接続先の Redshift に IAM ロールを関連付ける必要あり。

| 項目名      | 説明                                                                   | postgres | mysql | rds | redshift | redshift_serverless | dynamodb |
| ----------- | ---------------------------------------------------------------------- | -------- | ----- | --- | -------- | ------------------- | -------- |
| host        | データベースサーバーのホスト名                       | ◯（ホスト名、IPアドレス）        | ◯ （ホスト名、IPアドレス）    | ◯（クラスタ名）   | ◯（クラスタ名）        | ◯（ワークグループ名）                  | ☓        |
| port        | データベースサーバーのポート番号 | ◯        | ◯     | ☓   | ☓        | ☓                   | ☓        |
| dbname      | 接続するデータベースの名前                                             | ◯        | ◯     | ◯   | ◯        | ◯                   | ☓        |
| user        | データベースへの接続に使用するユーザー名                               | ◯        | ◯     | ☓   | ☓        | ☓                   | ☓        |
| password    | 上記ユーザーのパスワード                                               | ◯        | ◯     | ☓   | ☓        | ☓                   | ☓        |
| region      | 接続先の AWS リージョン                                                | ☓        | ☓     | ◯   | ◯        | ◯                   | ◯        |
| profile     | 接続に使用する認証情報のプロファイル                                   | ☓        | ☓     | ◯   | ◯        | ◯                   | ◯        |
| bucket_name | CSV ファイルをアップロードする S3 バケット名          | ☓        | ☓     | ◯   | ◯        | ◯                   | ◯        |
| object_key  | CSVアップロードするオブジェクトキー                       | ☓        | ☓     | ◯   | ◯        | ◯                   | ◯        |
| iam_role    | CSV ロードの際に使用する IAM ロール                                    | ☓        | ☓     | ☓   | ◯        | ◯                   | ☓        |

### 注意事項

- **RDSでCSVロードを実行する**
  - RDSにCSVファイルをインポートする際は、RDSからS3上のファイルにアクセスします。そのため、RDSからS3に接続できるように、VPCエンドポイントを作成します。
  - RDSからS3にアクセスする権限(AmazonS3FullAccessで動作を確認)をRDSクラスタの「接続とセキュリティ > IAMロールの管理」から付与してください。
  参照: [RDS CSVロード](https://docs.aws.amazon.com/ja_jp/AmazonRDS/latest/AuroraUserGuide/USER_PostgreSQL.S3Import.html#aws_s3.table_import_from_s3)
- **RedshiftでCSVロードを実行する**
  - RedshiftにCSVファイルをインポートする際は、COPYコマンドを実行するために IAMロールを作成し、対象のRedshiftの関連付けられたIAMロールとして指定する必要があります。設定後、対象のIAMロールのArnを設定ファイルの`iam_role`で設定してください。
    参照: [Redshift CSVロード](https://docs.aws.amazon.com/ja_jp/redshift/latest/dg/copy-parameters-data-source-s3.html)

### 環境設定

設定ファイルでは、異なる環境ごとのデータベース接続設定を定義できます。

- `default`: デフォルト設定(必須)。
- その他任意の環境の設定が可能です

### データベースの切り替え方法

アプリケーション起動時のオプション`--env`で、環境を指定することにより、接続データベースを切り替えることができます。オプションを設定しない場合は`defalut`の設定が適用されます。

```sh
# run fountain-flow with option
python app.py --env mysql
```

### 設定例

```yaml
default:
  type: postgres
  host: localhost
  port: 5432
  dbname: postgres
  user: postgres
  password: postgres

postgres:
  type: postgres
  host: localhost
  port: 5432
  dbname: postgres
  user: postgres
  password: postgres

mysql:
  type: mysql
  host: localhost
  port: 3306
  dbname: mysql
  user: root
  password: mysqlroot

redshift_serverless:
  type: redshift_serverless
  region: ap-northeast-1
  profile: default
  host: redshift-workgroup
  dbname: dev
  bucket_name: redshift-load-bucket-001
  object_key: csv_load/data.csv
  iam_role: arn:aws:iam::xxxxxxxxxxxx:role/redshift-load-role

redshift:
  type: redshift
  region: ap-northeast-1
  profile: default
  host: redshift-cluster
  dbname: dev
  bucket_name: redshift-load-bucket-001
  object_key: csv_load/data.csv
  iam_role: arn:aws:iam::xxxxxxxxxxxx:role/redshift-load-role

dynamodb:
  type: dynamodb
  region: ap-northeast-1
  profile: default
  bucket_name: dynamodb-load-bucket-001
  object_key: json_load/data.json
  source_table: products_source
```

## `settings.yaml`

### 概要

settings.yaml ではアプリケーションのデータ生成とログ出力の設定を行います。

### 設定ファイルの項目

- **`method`**: データ生成モード（必須）。選択肢は`database`, `csv`, `json`です。`json`は`dynamodb`のみで使用できます。
  `database`は生成したデータを INSERT で直接データベースに挿入します。`csv`は指定したフォルダに csv ファイルとしてデータを生成します。`json`は指定したフォルダに jsonl 形式のファイルとしてデータを生成します。また、続けて生成した csv ファイル, json ファイルからデータベースにデータをロードすることも可能です。
- **`database`**: データベースモードのデータ生成設定。
  - **`batch_size`**: 1 度にコミットするレコードの数。デフォルトは`100`。
  - **`commit_interval`**: トランザクションをコミットする時間間隔（msec）。デフォルトは`100`。
- **`csv`**: CSV モードのデータ生成設定。
  - **`file_path`**: CSV ファイルが出力されるディレクトリ。app.py があるフォルダを起点に相対パスを指定します。デフォルトは`data`。
  - **`delimiter`**: CSV ファイル内の区切り文字。デフォルトは`,`。
  - **`include_headers`**: CSV ファイルに列ヘッダーを含めるかどうかを指定します。必要な場合は`true`、不要な場合は`false`を設定します。デフォルトは`true`。
  - **`batch_size`**: CSV ファイルに 1 度に書き込むレコード数。デフォルトは`100000`。
- **`json`**: JSON モードのデータ生成設定。
  - **`file_path`**: JSON ファイルが出力されるディレクトリ。app.py があるフォルダを起点に相対パスを指定します。デフォルトは`data`。
  - **`batch_size`**: JSON ファイルに 1 度に書き込むレコード数。デフォルトは`100000`。
- **`level`**: ログレベルの設定で、「DEBUG」、「INFO」、「WARNING」、「ERROR」のいずれかを設定できます。デフォルトは`INFO`。

### 設定例

```yaml
settings:
  data_generation:
    method: database
    database:
      batch_size: 10000
      commit_interval: 100
    csv:
      file_path: data
      delimiter: ","
      include_headers: false
      batch_size: 100000
    json:
      file_path: data
      batch_size: 100000
  logging:
    level: INFO
```

## `data.yaml`

### 概要

`data.yaml` では、データ生成対象の複数テーブルに対するデータ生成定義を行います。テーブル名、生成する行数、そしてそれぞれの列のデータ型と生成方法を指定します。
:warning: また、以下の制約を持ちます。

- ユニークキーは考慮しない
- `integer`, `float`, `string`, `timestamp`, `boolean`, `list`, `json`以外の型は対象外
- `list`, `json`は`dynamodb`のみで使用できます。

### 設定ファイルの項目

- **`tables`**: データを生成するテーブルのリスト（必須）。
  - **`name`**: テーブル名（必須）。
  - **`row_count`**: テーブルに生成する行数（必須）。
  - **`columns`**: テーブルの列のリスト（指定したテーブルのカラムはすべて設定する必要があります）（必須）。
    - **`name`**: 列名（必須）。
    - **`type`**: 列のデータ型（`integer`, `float`, `string`, `timestamp`, `boolean`）（必須）。
    - **`generation`**: データの生成方法を定義（必須）。
      - **`method`**: 生成方法（`sequence` または `random`）（必須）。
      - **`start`**: 生成の開始値（`sequence` および `random` で `values` が設定されない場合に使用される）(任意, `type`: `timestamp`では必須)。
      - **`end`**: 生成の終了値（`sequence` および `random` で範囲を定義する場合に必要）(任意、`type`: `timestamp`では必須)。
      - **`values`**: 生成するデータの選択リスト（`sequence` および`random` で使用可能）(任意)。
      - **`interval`**: 生成される値の間隔。`type`: `integer`, `float`, `timestamp`で秒として設定（`sequence` で使用）(任意)。
      - **`decimal_places`**: 浮動小数点桁数。`type`: `float`のみで設定可能。（`sequence` および`random` で使用可能）(任意)。
      - **`foreign_table`**: 外部参照テーブル。外部のテーブルのレコードをデータソースとして利用する。（`sequence` および`random` で使用可能）(任意)。
      - **`foreign_key`**: 外部キー。外部のテーブルのレコードをデータソースとして利用する。（`sequence` および`random` で使用可能）(任意)。
      - **`struct`**: json のデータ構造を定義します。`type`: `json`のみで設定可能。
      - **`size`**: リストのサイズを定義します。`type`: `list`のみで設定可能。
      - **`inner_type`**: リスト内の型を定義します。`type`: `list`のみで設定可能。

### データ型と生成設定の対応表

| type      | method   | start | end | values | interval | decimal_places | foreign_table | foreign_key | struct | size | inner_type |
| --------- | -------- | ----- | --- | ------ | -------- | -------------- | ------------- | ----------- | ------ | ---- | ---------- |
| integer   | sequence | △     | △   | △      | △        | ☓              | △             | △           | ☓      | ☓    | ☓          |
| integer   | random   | ◯\*   | ◯\* | ◯\*    | △        | ☓              | △             | △           | ☓      | ☓    | ☓          |
| float     | sequence | △     | △   | △      | △        | △              | △             | △           | ☓      | ☓    | ☓          |
| float     | random   | ◯\*   | ◯\* | ◯\*    | △        | △              | △             | △           | ☓      | ☓    | ☓          |
| string    | sequence | ☓     | ☓   | △      | ☓        | ☓              | △             | △           | ☓      | ☓    | ☓          |
| string    | random   | ◯\*   | ◯   | ◯      | △        | ☓              | △             | △           | ☓      | ☓    | ☓          |
| timestamp | sequence | ◯\*   | △   | ◯\*    | △        | ☓              | △             | △           | ☓      | ☓    | ☓          |
| timestamp | random   | ◯\*   | ◯\* | ◯\*    | △        | ☓              | △             | △           | ☓      | ☓    | ☓          |
| boolean   | sequence | ☓     | ☓   | △      | ☓        | ☓              | △             | ☓           | ☓      | ☓    | ☓          |
| boolean   | random   | ☓     | ☓   | △      | ☓        | ☓              | △             | ☓           | ☓      | ☓    | ☓          |
| json      |  ☓        | ☓     | ☓   | ☓      | ☓        | ☓              | ☓             | ☓           | ◯      | ☓    | ☓          |
| list      |  ☓        | ☓     | ☓   | ☓      | ☓        | ☓              | ☓             | ☓           | ☓      | ◯    | ◯          |

- **◯ 必須**: この項目は設定が必須です。
- **△ 設定可能**: この項目は任意で設定可能です。
- **☓ 設定不可**: この項目は設定できません。

\*1 `random`は`start`と`end`もしくは`values`どちらかを設定する必要があります。
\*2 `timestamp`型の`sequence`は`start`もしくは`values`どちらかを設定する必要があります。
\*3 `values`, `end`以外について設定可能項目を設定していない場合はデフォルト値が設定されます。
\*4 `foreign_table`, `foreign_key`が設定されている場合は、外部参照のテーブルのレコードを`values`として使用します。
\*5 `values`が設定されている場合は、`start`, `end`, `interval`は適用されません。

### 設定例1

```yaml
tables:
  - name: products
    row_count: 100000
    columns:
      - name: product_id
        type: integer
        generation:
          method: sequence
          start: 1
      - name: product_type
        type: string
        generation:
          method: sequence
          foreign_table: type
          foreign_key: name
      - name: value
        type: float
        generation:
          method: random
          start: 0.0
          end: 10000.0
          decimal_places: 4
      - name: is_fragile
        type: boolean
        generation:
          method: sequence
          values: [True, False, True]
      - name: created_at
        type: timestamp
        generation:
          method: sequence
          start: "2024-01-01 00:00:00"
          end: "2024-12-31 23:59:59"
          interval: 10
```

### 設定例2(Dynamo DB)

```yaml
tables:
- name: products_source
  row_count: 100000
  columns:
  - name: product_id
    type: integer
    generation:
      method: sequence
      start: 1
  - name: product_type
    type: string
    generation:
      method: sequence
  - name: value
    type: float
    generation:
      method: random
      start: 0.0
      end: 10000.0
  - name: is_fragile
    type: integer
    generation:
      method: sequence
      values: [0, 1]
  - name: created_at
    type: timestamp
    generation:
      method: sequence
      start: '2020-01-01 00:00:00'
      end: '2020-02-01 23:59:59'
      interval: 60
  - name: options
    type: json
    struct:
      - name: name
        type: string
        generation:
          method: sequence
          values: ["sample01", "sample02", "sample03"]
      - name: place_id
        type: integer
        generation:
          method: sequence
          start: 1
      - name: places
        type: list
        size: 10
        inner_type: integer
        generation:
          method: sequence
          start: 1
```