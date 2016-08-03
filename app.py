#!flask/bin/python
from flask import Flask, request, g, jsonify
import sys
import MySQLdb

app = Flask(__name__)
NUM_TABLES=256
DEFAULT_TTL=86400

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = MySQLdb.connect(host='127.0.0.1', user='root', db='sessions');
        g.db.autocommit = True
    return g.db
    
@app.route('/api/v1.0/sessions/<string:key>', methods=['GET'])
def get_session(key):
    query = ( 'SELECT k, v as v FROM sessions_' + str(hash(key) % NUM_TABLES) + 
    ' WHERE k = %s and UNIX_TIMESTAMP() < UNIX_TIMESTAMP(ts) + expiration ' +
    'ORDER BY ts DESC LIMIT 1' )
    cursor = get_db().cursor()
    cursor.execute(query, (key,))
    if cursor.rowcount == 0:
        return jsonify({}), 404
    entries = cursor.fetchall()
    cursor.close()
    return jsonify(entries)

@app.route('/api/v1.0/sessions', methods=['POST', 'PUT'])
def post_session():
    cursor = get_db().cursor()
    args = request.get_json()
    query = 'INSERT INTO sessions_' + str(hash(args['key']) % NUM_TABLES) + \
    ' (k, v, expiration) VALUES (%(key)s, %(value)s, ' + str(DEFAULT_TTL) + ')'
    cursor.execute(query, args)
    get_db().commit()
    cursor.close()
    return jsonify(args)

@app.route('/api/v1.0/sessions/<string:key>', methods=['POST', 'PUT'])
def put_session():
    cursor = get_db().cursor()
    args = request.get_json()
    query = 'INSERT INTO sessions_' + str(hash(args['key']) % NUM_TABLES) + \
    ' (k, v, expiration) VALUES (%(key)s, %(value)s, ' + str(DEFAULT_TTL) + ')'
    cursor.execute(query, args)
    get_db().commit()
    cursor.close()
    return jsonify(args)

@app.route('/api/v1.0/sessions/<string:key>', methods=['DELETE'])
def delete_session(key):
    query = 'DELETE FROM sessions_' + str(hash(key) % NUM_TABLES) + \
    ' WHERE k = %s'
    cursor = get_db().cursor()
    cursor.execute(query, (key,))
    get_db().commit()
    cursor.close()
    return jsonify({key: 'deleted ok'})

if __name__ == '__main__':
    if len(sys.argv) > 1 and int(sys.argv[1]) > 0:
        port = int(sys.argv[1])
    else:
        port=5000
    app.run(debug=False, port=port)
    
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()
