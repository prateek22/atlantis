# alert functions

from .models import alerts
from .osqueryResponses import *
from .settings import *
import elasticsearch, time

def check_alerts(address, alert_query):

    src_alerts = alerts.objects.filter(src_ip=address)
    dest_alerts = alerts.objects.filter(dest_ip=address)

    for row in src_alerts:
        fields = ', '.join(ALERT_UPDATE_FIELDS)
        alert_query["queries"]["alert|src|" + row.uid] = PROC_PORT_QUERY.format(port=row.src_port, fields=fields)
    for row in dest_alerts:
        fields = ', '.join(ALERT_UPDATE_FIELDS)
        alert_query["queries"]["alert|dest|" + row.uid] = PROC_PORT_QUERY.format(port=row.dest_port, fields=fields)

    src_alerts.delete()
    dest_alerts.delete()

    return alert_query


def update_elastic(direction, uid, results):

    es = elasticsearch.Elasticsearch(ES_CONN_STRING)
    body = {"doc":{}}

    for field in ALERT_UPDATE_FIELDS:
        field = field.split('.')[1]
        body['doc'][direction + '_' + field] = results[field]

    for i in (range(3)):
        alert = es.search(q="alert_uid: {}".format(uid))
        if len(alert['hits']['hits']):
            alert = alert['hits']['hits'][0]
            es.update(index=alert['_index'], doc_type=alert['_type'], id=alert['_id'], body=body)
            break
        else:
            time.sleep(2)
