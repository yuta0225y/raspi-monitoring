# Raspberry Pi Monitoring

Docker Compose monitoring stack for a Raspberry Pi using Prometheus, Grafana, and node_exporter.

This repository keeps the monitoring configuration in Git so the stack can be restored or updated easily after changing hosts, rebuilding the Pi, or editing dashboards.

## Stack

- Prometheus collects metrics and stores 30 days of time series data.
- Grafana provides a pre-provisioned datasource and Raspberry Pi dashboard.
- node_exporter exposes host metrics from the Raspberry Pi.

## Repository Layout

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

## Requirements

- Raspberry Pi or Linux host
- Docker
- Docker Compose plugin

Check Docker Compose:

```sh
docker compose version
```

## Setup

Clone the repository:

```sh
git clone git@github.com:yuta0225y/raspi-monitoring.git
cd raspi-monitoring
```

Create a local environment file:

```sh
cp .env.example .env
```

Edit `.env` and set the Grafana admin user and password:

```env
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=change-me
```

Review the node_exporter target in `prometheus/prometheus.yml`. For example:

```yaml
targets:
  - 192.168.0.19:9100
```

Update this value to match the host running node_exporter before starting the stack.

Start the stack:

```sh
docker compose up -d
```

## Access

Open these from a browser on the same network:

- Grafana: `http://<raspberry-pi-ip>:3000`
- Prometheus: `http://<raspberry-pi-ip>:9090`
- node_exporter metrics: `http://<raspberry-pi-ip>:9100/metrics`

The Grafana datasource and dashboard are provisioned automatically from `grafana/provisioning/` and `grafana/dashboards/`.

## Operations

View running containers:

```sh
docker compose ps
```

View logs:

```sh
docker compose logs -f
```

Restart the stack:

```sh
docker compose restart
```

Stop the stack:

```sh
docker compose down
```

Update images:

```sh
docker compose pull
docker compose up -d
```

## Updating From Git

On the Raspberry Pi:

```sh
cd ~/monitoring
git pull --ff-only
docker compose up -d
```

## Data And Secrets

The repository tracks configuration only. Local runtime data and secrets are intentionally excluded:

- `.env` is ignored and should contain local Grafana credentials.
- Prometheus data is stored in the `prometheus_data` Docker volume.
- Grafana data is stored in the `grafana_data` Docker volume.

Use `.env.example` as the template for required environment variables.
