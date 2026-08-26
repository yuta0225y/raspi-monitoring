# AGENTS.md

このリポジトリで作業するエージェント向けのメモです。

## 目的

このリポジトリは Raspberry Pi 上で動かす監視スタックの設定を管理します。

- Docker Compose で Prometheus、Grafana、node_exporter を起動します。
- SwitchBot exporter で CO2、温度、湿度、バッテリー残量を Prometheus 形式に変換します。
- Grafana の datasource と dashboard は provisioning で自動設定します。
- Raspberry Pi 側の実行ディレクトリは `/home/pi/monitoring` です。

## 作業方針

- 設定変更はできるだけ小さく保ちます。
- README と実際の設定がずれないようにします。
- `.env` や認証情報、トークン、秘密鍵はコミットしません。
- Docker volume の中身や実行時データは Git 管理しません。
- 公開リポジトリとして見られる前提で、個人情報や不要なローカル情報を増やさないようにします。

## 重要なファイル

- `docker-compose.yml`: サービス定義
- `prometheus/prometheus.yml`: scrape 対象と Prometheus 設定
- `grafana/provisioning/datasources/prometheus.yml`: Grafana datasource 設定
- `grafana/provisioning/dashboards/dashboards.yml`: Grafana dashboard provisioning 設定
- `grafana/dashboards/raspi-overview.json`: Grafana dashboard JSON
- `switchbot-exporter/app.py`: SwitchBot API からメトリクスを取得する exporter
- `.env.example`: 必要な環境変数のテンプレート
- `.gitignore`: コミットしないローカルファイルの定義

## 検証コマンド

ローカルまたは Raspberry Pi 上で、変更内容に応じて確認します。

```sh
docker compose config
```

```sh
python3 -m py_compile switchbot-exporter/app.py
```

```sh
docker compose ps
```

```sh
docker compose logs -f
```

Prometheus の設定を変更した場合は、スタック起動後に Prometheus の targets 画面で scrape 状態を確認します。

```text
http://<raspberry-pi-ip>:9090/targets
```

Grafana の dashboard を変更した場合は、Grafana 画面で dashboard が読み込まれることを確認します。

```text
http://<raspberry-pi-ip>:3000
```

SwitchBot exporter を変更した場合は、`/metrics` が Prometheus 形式で返ることを確認します。

```text
http://<raspberry-pi-ip>:8000/metrics
```

## Raspberry Pi への反映

GitHub に push したあと、Raspberry Pi 側で更新します。

```sh
cd ~/monitoring
git pull --ff-only
docker compose up -d
```

## 注意点

- `prometheus/prometheus.yml` の node_exporter target は環境依存です。
- `.env.example` にはダミー値だけを書きます。
- SwitchBot API token/secret は `.env` にだけ置きます。
- CO2センサーが30分更新の場合、Prometheus scrape は5分以上の間隔で十分です。
- `latest` タグを使っているため、イメージ更新時は挙動が変わる可能性があります。
- 既存の dashboard JSON は Grafana が出力する大きな JSON なので、不要な整形変更は避けます。
