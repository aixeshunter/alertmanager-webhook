## Alertmanager Webhook

To store `resolved` status alerts in linux sqlite3 database by python flask framework.

### API

#### alerts ['POST']

The interface used by Alertmanager webhook.

##### Configuration
```bash
route:
  routes:
  - receiver: 'webhook'
    group_wait: 30s
    group_interval: 1m
    repeat_interval: 1h
    match_re:
      key: ${value}
    continue: true
 ...

receivers
- name: 'webhook'
  webhook_configs:
  - url: 'http://alertmanager-webhook:5000/alerts'
    send_resolved: true
```

#### alerts_history ['GET']

##### Parameters
| Name          | type     | default |
| ------------  | -------- | ------------|
| page          | int      | 1 |
| per_page      | int      | 20 |
| start         | str      | \ |
| end           | str      | \ |


The value be returned order by start time.

* Demo

Request
```bash
curl -g -i -X GET -H "Accept: application/json"  "http://alertmanager-webhook:5000/alerts_history?page=1&per_page=20&start=1542963638&end=1542965018"
```

Response
```json
{
  "alerts": [
    {
      "alertname": "NodeCPUUsageOvercommit",
      "end": "Fri, 23 Nov 2018 10:24:42 GMT",
      "hash_id": "-2466042037021245317",
      "id": 1,
      "message": "High CPU Usage in Node",
      "resource": "192.168.0.2",
      "resource_type": "node",
      "severity": "critical",
      "start": "Fri, 23 Nov 2018 09:20:12 GMT"
    },
    {
        ...
    }],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 20,
    "total": 4
  }
}
```

### ENV

| Name          | type     | default |
| ------------  | -------- | ------------|
| PORT          | int      | 5000 |
| DB_PATH       | str      | '/var/lib/alerts/alert.db' |
| HOST          | str      | '0.0.0.0' |


### table `alerts`

| Name          | type     | default |
| ------------  | -------- | ------------|
| id            | int      | autoincrement |
| alertname     | str      | \ |
| resource      | str      | \ |
| message      | text      | \ |
| hash_id      | str      | \ |
| severity      | str      | \ |
| start      | datetime      | datetime.datetime|
| end      | datetime      | datetime.datetime |


### Troubleshooting

#### alert uniqueness

I found that `resolved` alerts will be sent repeatedly, so I used some return `values` to do hash.

Like some alerts' info about `Node`, I used `alertname`， `instance`, `startsAt` this three value to do hash and achieve alert uniqueness.

```python
def hash_value(labels, starts):
    hash_str = labels.get("alertname", '') + labels.get("instance", "") + starts

    return hash(hash_str)
```

### Version

`v1.0`