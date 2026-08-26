# Raspberry Pi Monitoring

Raspberry Pi を Prometheus、Grafana、node_exporter で監視するための Docker Compose 構成です。

このリポジトリでは監視設定を Git で管理します。Raspberry Pi の再セットアップ、ホスト移行、ダッシュボード編集後の復元や更新をしやすくするための構成です。

## 構成

- Prometheus: メトリクスを収集し、30日分の時系列データを保存します。
- Grafana: Prometheus datasource と Raspberry Pi 用 dashboard を自動設定します。
- node_exporter: Raspberry Pi ホストのメトリクスを公開します。

## ディレクトリ構成

```text
.
|-- docker-compose.yml
|-- prometheus/
|   `-- prometheus.yml
`-- grafana/
    |-- dashboards/
    |   `-- raspi-overview.json
    `-- provisioning/
        |-- dashboards/
        |   `-- dashboards.yml
        `-- datasources/
            `-- prometheus.yml
```

## 必要なもの

- Raspberry Pi または Linux ホスト
- Docker
- Docker Compose plugin

Docker Compose が使えるか確認します。

```sh
docker compose version
```

## セットアップ

リポジトリを clone します。

```sh
git clone git@github.com:yuta0225y/raspi-monitoring.git
cd raspi-monitoring
```

ローカル用の環境変数ファイルを作成します。

```sh
cp .env.example .env
```

`.env` を編集し、Grafana の管理ユーザー名とパスワードを設定します。

```env
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=change-me
```

`prometheus/prometheus.yml` の node_exporter の接続先を確認します。例:

```yaml
targets:
  - 192.168.0.19:9100
```

起動前に、この値を node_exporter が動いているホストのアドレスに合わせて変更してください。

スタックを起動します。

```sh
docker compose up -d
```

## アクセス

同じネットワーク上のブラウザからアクセスします。

- Grafana: `http://<raspberry-pi-ip>:3000`
- Prometheus: `http://<raspberry-pi-ip>:9090`
- node_exporter メトリクス: `http://<raspberry-pi-ip>:9100/metrics`

Grafana の datasource と dashboard は `grafana/provisioning/` と `grafana/dashboards/` から自動で読み込まれます。

## 操作

コンテナの状態確認:

```sh
docker compose ps
```

ログ確認:

```sh
docker compose logs -f
```

再起動:

```sh
docker compose restart
```

停止:

```sh
docker compose down
```

イメージ更新:

```sh
docker compose pull
docker compose up -d
```

## Git から更新する

Raspberry Pi 側で実行します。

```sh
cd ~/monitoring
git pull --ff-only
docker compose up -d
```

## データと秘密情報

このリポジトリでは設定ファイルのみを管理します。ローカルの実行データや秘密情報は Git 管理しません。

- `.env` は Git 管理対象外です。Grafana の認証情報など、ローカル環境用の値を入れます。
- Prometheus のデータは Docker volume `prometheus_data` に保存されます。
- Grafana のデータは Docker volume `grafana_data` に保存されます。

必要な環境変数は `.env.example` をテンプレートとして確認できます。
