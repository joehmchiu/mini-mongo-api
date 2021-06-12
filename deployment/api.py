import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
from bson import ObjectId
import json

user='[your mongodb username]'
token='[the mongodb token]'
url = 'mongodb+srv://%s:%s@cluster0.scnxl.mongodb.net/foo?retryWrites=true&w=majority' % (user, token)
app = Flask(__name__)
client = pymongo.MongoClient(url)
api = '/api/v1/users/'
# Database
db = client.get_database('foo')
# Table
tab = db.users

t0 = time.time()
err = { "error": "ID not exists" }
res = { "result": "ID not exists" }

def diff(t1,t2): return "%s sec" % str(t2-t1)
def fill(o,t1,t2):
    o["real"] = diff(t1,t2)
    o["uptime"] = diff(t0,t2)
    return o

@app.route(api, methods=['GET'])
def all():

    t1 = time.time()
    res = tab.aggregate([
        { "$match": {} },
        { "$project": { "_id":{"$toString":"$_id" },"name":1, "email":1,"gender":1,"mobile":1,"created":1,"update":1 } }
    ])
    t2 = time.time()

    rec = [r for r in res]
    output = {
        "list": rec,
        "count": len(rec)
    }

    output = fill(output, t1, t2)
    return jsonify(output)

@app.route(api+'<id>', methods=['GET'])
def read(id):

    t1 = time.time()
    if len(id) != 24:
        output = { "error": "Invalid ID hex string" }
        return jsonify(output)

    res = tab.aggregate([
        { "$match": {'_id':ObjectId(id)} },
        { "$project": { "_id":{"$toString":"$_id" },"name":1, "email":1,"gender":1,"mobile":1,"created":1,"update":1 } }
    ])
    # res = tab.find({'_id':ObjectId(id)}, {'_id': False})
    if res:
        t2 = time.time()
        rec = [r for r in res]
        output = {
                'id': id,
                'list' : rec,
                'count': len(rec)
            }
    else:
        output = res

    output = fill(output, t1, t2)
    return jsonify(output)

@app.route(api, methods=['POST'])
def create():

    go = True
    t1 = time.time()
    try:
        # data = request.get_json(force=True)
        data = request.get_json()
        print(data)
    except Exception as e:
        output = { 'error' : '%s' % str(e) }
        return jsonify(output)


    try:
        res = tab.insert(data)
    except Exception as e:
        output = { 'error' : '%s' % str(e) }
        return jsonify(output)

    if isinstance(res, list):
        # Return list of Id of the newly created item
        output = { "record": [str(v) for v in res], 'result' : "User created successfully" }
    else:
        # Return Id of the newly created item
        output = { "id": str(res), 'result' : "User created successfully" }

    t2 = time.time()
    output = fill(output, t1, t2)

    return jsonify(output)

@app.route(api+'<id>', methods=['PUT'])
def update(id):

    go = True
    t2 = time.time()

    if len(id) != 24:
        output = { "error": "Invalid ID hex string" }
        return jsonify(output)

    try:
        data = request.get_json(force=True)
    except Exception as e:
        output = { 'error' : '%s' % str(e) }
        return jsonify(output)


    tab.update_one({'_id': ObjectId(id)}, {"$set": data}, upsert=True)
    # tab.replace_one({"_id":id}, data, True)
    output = { 'result' : "%s updated successfully" % id }

    try:
        s = tab.find_one({'_id' : ObjectId(id)})
        if s:
            output = {
                    'id': id,
                    'name' : s['name'],
                    'gender' : s['gender'],
                    'mobile' : s['mobile'],
                    'email' : s['email']
                }
        else:
            output = res
            go = False

    except Exception as e:
        output = { 'error': str(e) }

    t1 = time.time()
    output = fill(output, t1, t2)

    return jsonify(output)

@app.route(api+'<id>', methods=['DELETE'])
def delete(id):
    go = True

    if len(id) != 24:
        output = { "error": "Invalid ID hex string" }
        return jsonify(output)

    try:
        s = tab.find_one({'_id' : ObjectId(id)})
        if s:
            output = {
                    'id': id,
                    'name' : s['name'],
                    'gender' : s['gender'],
                    'mobile' : s['mobile'],
                    'email' : s['email']
                }
        else:
            output = res
            go = False

    except Exception as e:
        output = { 'error': str(e) }

    if go:
        tab.delete_one({'_id' : ObjectId(id)})
        output = { 'result' : "%s deleted" % id }
        output["id"] = id

    return jsonify(output)

@app.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    # Message to the user
    message = {
        "error": "This route is currently not supported. Please refer API documentation."
    }
    # Making the message looks good
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 404
    # Returning the object
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8600, debug=True)

