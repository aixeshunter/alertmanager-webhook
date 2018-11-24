from flask import Flask
from flask import request
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import jsonify
import os


DB_PATH = os.environ.get('DB_PATH', '/var/lib/alerts/alert.db')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
db = SQLAlchemy(app)

TIME_SEC = 24 * 60 * 60
RESOLVED = "resolved"
resource_type = {
    "node": "node"
}


class Alerts(db.Model):

    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alertname = db.Column(db.String(64), unique=False, nullable=False)
    resource = db.Column(db.String(64), unique=False, nullable=False)
    message = db.Column(db.Text, unique=False, nullable=False)
    hash_id = db.Column(db.String(64), unique=True, nullable=False)
    severity = db.Column(db.String(64),nullable=False)
    resource_type = db.Column(db.String(64),nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, alertname, resource, message, hash_id, severity, resource_type, start, end):
        self.alertname = alertname
        self.resource = resource
        self.message = message
        self.hash_id = hash_id
        self.severity = severity
        self.resource_type = resource_type
        self.start = start
        self.end = end

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'alertname': self.alertname,
            'severity': self.severity,
            'resource_type': self.resource_type,
            'resource': self.resource,
            'message': self.message,
            'hash_id': self.hash_id,
            'start': self.start,
            'end': self.end
        }

    def __repr__(self):
        return '<Alerts %r>' % self.hash_id


def query_hash_id(hash_id):
    data = Alerts.query.filter_by(hash_id=hash_id).first()

    return data


def query_alerts(page, per_page, start, end):
    try:
        alert = Alerts.query.order_by(Alerts.start.desc())
        if start:
            start = datetime.utcfromtimestamp(float(start))
            alert = alert.filter(Alerts.start > start)

        if end:
            end = datetime.utcfromtimestamp(float(end))
            alert = alert.filter(Alerts.end < end)

        a = alert.paginate(page, per_page, error_out=False)
        alerts = [i.serialize for i in a.items]
    except Exception as e:
        raise e

    pagination = {
        "page": a.page,
        "pages": a.pages,
        "per_page": a.per_page,
        "total": a.total
    }

    return alerts, pagination


@app.route("/alerts_history", methods=['GET'])
def alerts_history():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start = request.args.get('start', type=str)
    end = request.args.get('end', type=str)
    alerts, pagination = query_alerts(page, per_page, start, end)

    return jsonify({"alerts": alerts, "pagination": pagination}), 200


@app.route('/alerts',methods=['POST'])
def send():
    try:
        if request.method == 'POST':
            post_data = request.get_json()
            alert_data(post_data)
    except Exception as e:
        logging.error("Storing alerts failed: %s", e)
        return "Error", 500

    return "OK", 200


def alert_data(data):
    alerts_list = []
    if "alerts" in data:
        for i in data["alerts"]:
            try:
                if i.get("status") != RESOLVED:
                    continue

                hash_str = hash_value(i["labels"], i["startsAt"])
                if hash_str and not query_hash_id(hash_str):
                    instance = i["labels"]["instance"].split(':')[0]
                    alerts_list.append(handle_data(i, instance, hash_str))
            except Exception as e:
                logging.error("Storing alerts failed: %s", e)

    insert_data(alerts_list)


def handle_data(alert, resource, hash_str):
    alerts = Alerts(resource=resource,
                    hash_id=hash_str,
                    severity=alert["labels"]["severity"],
                    resource_type=alert["labels"]["resource_type"],
                    alertname=alert["labels"]['alertname'],
                    start=time_format(alert["startsAt"]),
                    message=alert["annotations"]["message"],
                    end=time_format(alert["endsAt"]))
    return alerts


def time_format(times_str):
    times_f = times_str.split(".")[0]
    return datetime.strptime(times_f, '%Y-%m-%dT%H:%M:%S')


def insert_data(alerts):
    db.session.add_all(alerts)
    db.session.commit()
    logging.info("Inserting data to sqlite succeed.")


def hash_value(labels, starts):
    hash_str = ''
    if labels.get('resource_type') == resource_type["node"]:
        hash_str = labels.get("alertname", '') + labels.get("instance", "") + starts

    return hash(hash_str)


if __name__ == '__main__':
    db.create_all()
    port = os.environ.get('PORT', 5000)
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port)
