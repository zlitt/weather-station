from flask import Flask, request, jsonify
from redis import StrictRedis
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object('config')

@app.after_request
def crossdomain(response):
    origin = request.headers.get('origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = app.config['ALLOWED_ORIGIN']
    return response

r = None
def get_redis():
    global r
    if r is None:
        r = StrictRedis()
    return r

def decode(data):
    res = []
    for d in data:
        ob = {}
        for k in d:
            if k == b'date':
                v = str(d[k], 'utf-8')
            else:
                v = float(d[k])
            ob[str(k, 'utf-8')] = v
        if ob:
            res.append(ob)
    return res


def load_data():
    p = get_redis().pipeline()
    now = datetime.now()
    now -= timedelta(0, 60 * (now.minute % 5))
    for m in range(60 * 24, -1, -5):
        d = now - timedelta(0, 60 * m)
        key = d.strftime('%Y.%m.%d.%H.%M')
        p.hgetall('toaster.%s' % key)
    data = p.execute()
    return decode(data)

@app.route('/data')
def get_data():
    return jsonify({'data': load_data()})
