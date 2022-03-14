# Node secrets
ENROLL_SECRET = "password"
LOGSTASH_SECRET = "password"

# Elasticsearch
ES_PORT = "9200"
ES_IP = "localhost"
ES_CONN_STRING = ["{}:{}".format(ES_IP, ES_PORT)]

# Logging
LOG_OUTPUT_FILE = './osquery.log'

# Alert update fields
ALERT_UPDATE_FIELDS = ['p.pid', 'p.cmdline', 'p.uid', 'p.parent']
