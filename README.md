# Raspberry Pi Monitoring

Docker Compose monitoring stack for a Raspberry Pi.

## Services

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- node_exporter: host network on port 9100

## Setup

Create the local environment file:

```sh
cp .env.example .env
```

Edit `.env` and set a Grafana admin password.

Start the stack:

```sh
docker compose up -d
```

## Files

- `docker-compose.yml`: service definitions
- `prometheus/prometheus.yml`: Prometheus scrape configuration
- `grafana/provisioning/`: Grafana datasource and dashboard provisioning
- `grafana/dashboards/raspi-overview.json`: Raspberry Pi dashboard
