
## Requirements
:warning: `fountain-flow` is currently work in progress. Breaking changes may occur.

Running `fountain-flow` requires:

* Python 3.12 (tested under Python 3.12.3)


## ⛲パッケージインストール
アプリケーションに必要なパッケージをインストールするためには以下のコマンドを実行します:

```sh
# install packages
pip install -r requirements.txt
```

## アプリケーションの実行
アプリケーションを実行するためには、以下のコマンドを実行します。
環境情報はdatabase.yamlで設定します。

```sh
# fountain-flowを実行する
# 環境を指定して実行する場合（例: mysql環境で実行）
bin/fountain-flow run --env mysql

# 環境を指定せずに実行する場合 (default環境)
bin/fountain-flow run
```

## 定義(data.yaml)の生成
fountain-flowではデータ生成のための定義ファイル(data.yaml)の設定が必要です。定義ファイルは手動で作成するほか、定義を生成するコマンドを実行することで、def/data.yamlに雛形が作成されます。

```sh
bin/fountain-flow create-def path/to/ddl1.sql path/to/ddl2.sql
```

コマンドの使用方法やオプションについての詳細は、以下のコマンドでヘルプを表示できます。
```sh
# ヘルプメッセージを表示
bin/fountain-flow -help
```

## アプリケーション設定

`fountain-flow`は以下の3つの設定ファイルを持ちます。
- **ファイルパス**: 
  - `config/database.yaml`
  - `config/settings.yaml`
  - `definition/data.yaml`
  
以下に、 `database.yaml`, `settings.yaml`, `data.yaml` のファイルの構造と使用方法について説明します。


## `database.yaml` 

### 概要

database.yamlでは`fountain-flow`の接続先のデータベースの設定を行います。

### 設定ファイルの項目

以下の項目が設定ファイルに含まれます：
- `環境名`: 接続先データベースの環境名（必須）。
  - **`type`**: DBを指定します（任意）。選択肢は`postgres`, `mysql`, `redshift`, `redshift_serverless`, `dynamodb`。指定されない場合は`postgres`が設定される。
  - **`host`**: データベースサーバーのホスト名またはIPアドレス（必須）。
  - **`port`**: データベースサーバーのポート番号（必須）。PostgreSQLのデフォルトポートは5432。`postgres`, `mysql`のみ。
  - **`dbname`**: 接続するデータベースの名前（必須）。
  - `user`: データベースへの接続に使用するユーザー名（必須）。`postgres`, `mysql`のみ。
  - **`password`**: 上記ユーザーのパスワード（必須）。`postgres`, `mysql`のみ。
  - **`region`**: 接続先のAWSリージョンを指定します。`redshift`, `redshift_serverless`, `dynamodb`のみ。
  - **`profile`**: 接続に使用する認証情報のプロファイルを指定します。`redshift`, `redshift_serverless`, `dynamodb`のみ。指定しない場合はdefalutプロファイルが使用されます。
  - **`bucket_name`**: CSVロードの際にCSVファイルをアップロードするS3バケット名を指定します。`redshift`, `redshift_serverless`, `dynamodb`のみ。
  - **`object_key`**: CSVロードの際にアップロードするオブジェクトキーを指定します。`redshift`, `redshift_serverless`, `dynamodb`のみ。
  - **`iam_role`**: CSVロードの際に使用するIAMロールを指定します。`redshift`, `redshift_serverless`のみ。あらかじめ接続先のRedshiftにIAMロールを関連付ける必要あり。

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

settings.yamlではアプリケーションのデータ生成とログ出力の設定を行います。

### 設定ファイルの項目

- **`method`**: データ生成モード（必須）。選択肢は`database`, `csv`, `json`です。`json`は`dynamodb`のみで使用できます。
  `database`は生成したデータをINSERTで直接データベースに挿入します。`csv`は指定したフォルダにcsvファイルとしてデータを生成します。`json`は指定したフォルダにjsonl形式のファイルとしてデータを生成します。また、続けて生成したcsvファイル, jsonファイルからデータベースにデータをロードすることも可能です。
- **`database`**: データベースモードのデータ生成設定。
  - **`batch_size`**: 1度にコミットするレコードの数。デフォルトは`100`。
  - **`commit_interval`**: トランザクションをコミットする時間間隔（msec）。デフォルトは`100`。
- **`csv`**: CSVモードのデータ生成設定。
  - **`file_path`**: CSVファイルが出力されるディレクトリ。app.pyがあるフォルダを起点に相対パスを指定します。デフォルトは`data`。
  - **`delimiter`**: CSVファイル内の区切り文字。デフォルトは`,`。
  - **`include_headers`**: CSVファイルに列ヘッダーを含めるかどうかを指定します。必要な場合は`true`、不要な場合は`false`を設定します。デフォルトは`true`。
  - **`batch_size`**: CSVファイルに1度に書き込むレコード数。デフォルトは`100000`。
- **`json`**: JSONモードのデータ生成設定。
  - **`file_path`**: JSONファイルが出力されるディレクトリ。app.pyがあるフォルダを起点に相対パスを指定します。デフォルトは`data`。
  - **`batch_size`**: JSONファイルに1度に書き込むレコード数。デフォルトは`100000`。
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
      delimiter: ','
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

`data.yaml` では、データ生成対象の複数テーブルに対するデータ生成設定を行います。テーブル名、生成する行数、そしてそれぞれの列のデータ型と生成方法を指定します。
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
      - **`struct`**: jsonのデータ構造を定義します。`type`: `json`のみで設定可能。
      - **`size`**: リストのサイズを定義します。`type`: `list`のみで設定可能。
      - **`inner_type`**: リスト内の型を定義します。`type`: `list`のみで設定可能。

### データ型と生成設定の対応表

| type      | method    | start | end | values | interval | decimal_places | foreign_table | foreign_key | struct | size | inner_type |
|-----------|-----------|-------|-----|--------|----------|----------------|---------------|-------------|--------|------|------------|
| integer   | sequence  | △     | △   | △      | △        | ✗              | △             | △           | ✗      | ✗    | ✗          |
| integer   | random    | ◯*    | ◯*  | ◯*     | △        | ✗              | △             | △           | ✗      | ✗    | ✗          |
| float     | sequence  | △     | △   | △      | △        | △              | △             | △           | ✗      | ✗    | ✗          |
| float     | random    | ◯*    | ◯*  | ◯*     | △        | △              | △             | △           | ✗      | ✗    | ✗          |
| string    | sequence  | ✗     | ✗   | △      | ✗        | ✗              | △             | △           | ✗      | ✗    | ✗          |
| string    | random    | ◯*    | ◯   | ◯      | △        | ✗              | △             | △           | ✗      | ✗    | ✗          |
| timestamp | sequence  | ◯*    | △   | ◯*     | △        | ✗              | △             | △           | ✗      | ✗    | ✗          |
| timestamp | random    | ◯*    | ◯*  | ◯*     | △        | ✗              | △             | △           | ✗      | ✗    | ✗          |
| boolean   | sequence  | ✗     | ✗   | △      | ✗        | ✗              | △             | ✗           | ✗      | ✗    | ✗          |
| boolean   | random    | ✗     | ✗   | △      | ✗        | ✗              | △             | ✗           | ✗      | ✗    | ✗          |
| json      |           | ✗     | ✗   | ✗      | ✗        | ✗              | △             | ✗           | ◯      | ✗    | ✗          |
| list      |           | ✗     | ✗   | ✗      | ✗        | ✗              | △             | ✗           | ✗      | ◯    | ◯          |


- **◯ 必須**: この項目は設定が必須です。
- **△ 設定可能**: この項目は任意で設定可能です。
- **✗ 設定不可**: この項目は設定できません。

\*1 `random`は`start`と`end`もしくは`values`どちらかを設定する必要があります。
\*2 `timestamp`型の`sequence`は`start`もしくは`values`どちらかを設定する必要があります。
\*3 `values`, `end`以外について設定可能項目を設定していない場合はデフォルト値が設定されます。
\*4 `foreign_table`, `foreign_key`が設定されている場合は、外部参照のテーブルのレコードを`values`として使用します。
\*5 `values`が設定されている場合は、`start`, `end`, `interval`は適用されません。

### 設定例

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