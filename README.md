## **FOUNTAIN-FLOW**
### **Generating large datasets for performance testing**
![fountain-flow](https://github.com/user-attachments/assets/cd799b9d-6a9f-4deb-9288-524ddcbba767)

`fountain-flow`は負荷試験向けのデータ生成ツールです。設定したデータ生成ルールに従い、データ生成からDBへのデータ投入までの機能を一気通貫で提供します。

### ユースケース
`fountain-flow`は以下のようなケースでの利用を想定しています。

- アプリケーションのパフォーマンステスト
- DBのパフォーマンスチューニング
- DBのスケーラビリティテスト
- プロトタイプ・製品のデモンストレーション

:warning:`fountain-flow`はDBの破壊的操作を含むため、稼働中の本番環境への利用は推奨しません。

### 基本機能
`fountain-flow`は以下の機能を提供します。

- データ生成定義からDBへ直接データを投入
- データ生成定義からCSVファイル, JSONLファイルへのデータ出力
- CSVファイル, JSONLファイルからのデータロード

## 動作要件

:warning:`fountain-flow`は進行中のプロジェクトです。動作要件は変更が行われる可能性があります.

### 動作環境

- Python 3.12 (tested under Python 3.12.3)
- pip (tested under pip 24.0)

### 対応DB
`fountain-flow`は主にAWSのデータベースに対応しています。

| データベース               | CSV形式の出力・ロード | JSON形式の出力・ロード |DBへのINSERT |
| -------------------------- | -------- | -------- | ------------------- |
| Postgres                   | ○        | ☓        | ○                   |
| Mysql                      | ○        | ☓       | ○                   |
| Oracle Database            | ☓       | ☓        | ☓                   |
| Microsoft SQL Server       | ☓       | ☓        | ☓                   |
| MariaDB                    | ☓       | ☓        | ☓                   |
| Amazon RDS                 | ○        | ☓        | ☓                   |
| Amazon RDS serverless      | ○        | ☓        | ☓                   |
| Amazon Redshift            | ○        | ☓        | ○                   |
| Amazon Redshift Serverless | ○        | ☓        | ○                   |
| Cassandra                  | ☓       | ☓        | ☓                   |
| MongoDB                    | ☓       | ☓        | ☓                   |
| Amazon Dynamo DB           | ☓        | ○        | ○                   |
| Amazon Neptune             | ☓       | ☓        | ☓                   |
| Snowflake                  | ☓       | ☓        | ☓                   |
| IBM Db2                    | ☓       | ☓        | ☓                   |
| Google BigQuery            | ☓       | ☓        | ☓                   |
| Apache Hive                | ☓       | ☓        | ☓                   |
| SQLite                     | ☓       | ☓        | ☓                   |

## パッケージインストール

fountain-flowに必要なパッケージをインストールするためには以下のコマンドを実行します。

```sh
# install packages
pip install -r requirements.txt
```

## アプリケーションの実行

fountain-flowを実行するためには、以下のコマンドを実行します。

```sh
# fountain-flowを実行する
bin/fountain-flow cli
```

database.yamlで定義した接続環境を選択します。
(database.yamlの設定方法は`database.yaml`の節を参照)

```sh
[?] 接続環境を選んでください(database.yaml): 
   default
 > postgres
   mysql
   rds
   redshift_serverless
   redshift
   dynamodb
```
```sh
[?] Please select the data config (/def): 
 > data_dynamodb.yaml
   data.yaml
```
### 処理選択メニュー

実行したい処理を選択します。
| 処理名               | 説明
| -------------------------- | -------- |
| Truncate Table                   | 対象のテーブルをTRUNCATEします。        |
| Generate Data & Insert Records                      | データ生成とデータのINSERTを行います。        |
| Generate Data & File Output            | データ生成とファイル出力を行います。       |
| Load File       | 対象のテーブルに対してファイルをロードします。       |
| Switch Env                    | 接続環境を切り替えます。       |
| Switch Data Confg                    | データ定義を切り替えます。       |
| Exit                 | CLIを終了します。        |

```sh
[?] 選択肢を選んでください(env=postgres): 
 > Truncate Table
   Generate Data & Insert Records
   Generate Data & File Output
   Load File
   Switch Env
   Switch Data Config
   Exit
```
### Truncate Table

data.yamlで定義したテーブルを指定して、truncateを実行します。
`Exit`を選択すると、`処理選択メニュー`に戻ります。

```
[?] Please select the table name to truncate.(data.yaml): 
 > products
   Exit
```

`y`または`Y`の入力でtruncateを実行します。
それ以外の場合は、`処理選択メニュー`に戻ります。

```
Do you want to truncate table 'products'? (y/N): y
```

```
xxxx-xx-xx xx:xx:xx,xxx - INFO - Table 'products' has been truncated.
```

### Generate Data & Insert Records

data.yamlで定義したテーブルを指定して、データの作成及びデータのINSERTを行います。
`Exit`を選択すると、`処理選択メニュー`に戻ります。
```
[?] Please select the table name for the INSERT operation.(data.yaml): 
 > products
   Exit
```

`y`または`Y`の入力でデータの作成及びデータのINSERTを実行します。
それ以外の場合は、`処理選択メニュー`に戻ります。

```
Start data generation and insersion (y/N): y
```
```
Inserting data: 100%|████████████████████████████████████████████████████████████████████████████████████████████████| 10000/10000
xxxx-xx-xx xx:xx:xx,xxx - INFO - Data insertion completed: '10000' records were inserted into the table 'products'.
```

### Generate Data & File Output

data.yamlで定義したテーブルを指定して、データの作成及びファイル出力を行います。
`Exit`を選択すると、`処理選択メニュー`に戻ります。
```
[?] Please select the table name for file creation.(data.yaml): 
 > products
   Exit
```

`y`または`Y`の入力でデータの作成及びデータのファイル出力を実行します。
それ以外の場合は、`処理選択メニュー`に戻ります。
```
Start data generation and file output
table name: 'products
row count: '10000'
(y/N): y
```

出力先のファイルがフルパスで表示されます。


```
xxxx-xx-xx xx:xx:xx,xxx - INFO - Data generation completed: '10000' records were written to the file '/xxxx/xxxx/xxxx/xxxx/fountain-flow/data/xxxxxxxxxxxxxx_products.csv'.
```

### Load File

data.yamlで定義したテーブルを指定して、データの作成及びファイル出力を行います。
`Exit`を選択すると、`処理選択メニュー`に戻ります。
```
[?] Please select the table name to load into the database.(data.yaml): 
 > products
   Exit
```

`fountain-flow/data`配下のファイルの一覧を表示されます。
ロードするファイルを選択します。
`Exit`を選択すると、`処理選択メニュー`に戻ります。

```
[?] Please select the file to load into the database.(/data): 
   20240809120716_products.csv
   20240713220501_products.csv
   20240713220142_products.csv
 > 20240809122933_products.csv
   Exit
```

CSVファイルの場合はヘッダを含むかどうかを選択します。
ヘッダを含む場合は、`y`または`Y`を入力してください。ヘッダを含まない場合はそれ以外の文字を入力してください。

```
Does the CSV file include headers? (y/N): y
```

ロードに成功すると、指定したファイルのロードが完了した以下のメッセージが表示されます。

```
xxxx-xx-xx xx:xx:xx,xxx - INFO - Successfully load '/xxxx/xxxx/xxxx/xxxx/fountain-flow/data/20240809122933_products.csv' into 'products'.
```

### Switch Env

`database.yaml`で定義したDB定義の中から接続する環境を選択します。

```sh
[?] Please select the connection environment (database.yaml): 
 > default
   postgres
   mysql
   rds
   redshift_serverless
   redshift
   dynamodb
```
### Switch Data Config

`/def`配下のファイルからデータ生成で使用するデータ定義ファイルを選択します。
```sh
[?] Please select the data config (/def): 
 > data_dynamodb.yaml
   data.yaml
```

### Exit

CLIを終了します。

```sh
[?] Please select an option (env=postgres, data_config=data.yaml): 
   Truncate Table
   Generate Data & Insert Records
   Generate Data & File Output
   Load File
   Switch Env
   Switch Data Config
 > Exit

xxxx-xx-xx xx:xx:xx,xxx - INFO - Exiting fountain-flow.
```
### データ生成ルール(data.yaml)の生成

fountain-flow ではデータ生成のためのデータ定義ファイル(`data.yaml`)の設定が必要です。定義ファイルは手動で作成するほか、create-defコマンドを使用することで、テーブルの定義から定義の雛形が`def/data.yaml`として作成されます。

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
  - `def/data.yaml`

以下に、 `database.yaml`, `settings.yaml`, `data.yaml` のファイルの構造と使用方法について説明します。

## `database.yaml`

### 概要

`database.yaml` では`fountain-flow`の接続先のデータベースの設定を行います。

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
  - **`secret_arn`**: DBに接続する認証情報を指定します。`rds`のみ。

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
| secret_arn    | DB接続に使用する認証情報                                    | ☓        | ☓     | ◯   | ☓        | ☓                   | ☓        |

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

rds:
  type: rds
  region: ap-northeast-1
  profile: default
  host: arn:aws:rds:ap-northeast-1:xxxxxxxxxxxx:cluster:database-1
  dbname: postgres
  secret_arn: arn:aws:secretsmanager:ap-northeast-1:xxxxxxxxxxxx:secret:rds-db-credentials/cluster-xxxxxxxxxxxxpostgres/xxxxxxxxxxxx
  bucket_name: redshift-load-bucket-001
  object_key: csv_load/data.csv
  iam_role: arn:aws:iam::xxxxxxxxxxxx:role/rds-csv-load-role

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
  bucket_name: dynamodb-xxxxxxxxxxxx-load-bucket-001
  object_key: json_load/data.json
  source_table: products_source

```

## `settings.yaml`

### 概要

settings.yaml ではアプリケーションのデータ生成とログ出力の設定を行います。

### 設定ファイルの項目

- **`database`**: INSERTモードのデータ生成設定。
  - **`batch_size`**: 1 度にコミットするレコードの数。デフォルトは`100`。
  - **`commit_interval`**: トランザクションをコミットする時間間隔（msec）。デフォルトは`100`。
- **`csv`**: CSVモードのデータ生成設定。
  - **`delimiter`**: CSV ファイル内の区切り文字。デフォルトは`,`。
  - **`include_headers`**: CSV ファイルに列ヘッダーを含めるかどうかを指定します。必要な場合は`true`、不要な場合は`false`を設定します。デフォルトは`true`。
  - **`batch_size`**: CSV ファイルに 1 度に書き込むレコード数。デフォルトは`100000`。
- **`json`**: JSONモードのデータ生成設定。
  - **`batch_size`**: JSON ファイルに 1 度に書き込むレコード数。デフォルトは`100000`。
- **`level`**: ログレベルの設定で、「DEBUG」、「INFO」、「WARNING」、「ERROR」のいずれかを設定できます。デフォルトは`INFO`。

### 設定例

```yaml
settings:
  data_generation:
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
