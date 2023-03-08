#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Copyright 2023 Adam Ahmed
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import datetime, flask, logging
from flask import abort, Flask, has_request_context, redirect, request, Response, send_from_directory, url_for
import json
from flask.logging import default_handler

# This logging code is modified from a flask documenation by Pallets, retrieved on 2023-03-05 from flask.palletsprojects.com
# Documentation here:
# https://flask.palletsprojects.com/en/2.2.x/logging/
class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '%(asctime)s %(levelname)s %(url)s - %(funcName)s - %(message)s', "%Y-%m-%dT%H:%M:%S"
)
default_handler.setFormatter(formatter)

app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        self.last_modified = datetime.datetime.utcnow()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry
        self.last_modified = datetime.datetime.utcnow()

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = dict()
        self.last_modified = datetime.datetime.utcnow()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def get_last_modified(self):
        return self.last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')

    def world(self):
        return self.space

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()          

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Redirect to /static/index.html'''
    return redirect(url_for('static', filename='index.html'))

@app.route("/favicon.ico")
def favicon():
    '''Return static/favicon.ico'''
    return send_from_directory('static', 'favicon.ico')

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''Update world entities'''
    response_status = 400
    response_error = {'error': {'code': 1, 'message': 'Could not perform update'}}
    request_post_json = {}
    # Parse incoming request JSON
    try:
        request_post_json = flask_post_json()
    except Exception as e:
        app.logger.error(f'Failed to parse request JSON - [{e}]')
        response_error['error']['code'] = response_status
        response_error['error']['message'] = str(e)
        return Response(response=json.dumps(response_error), status=response_status, mimetype='application/json')
    
    # Update world with request JSON
    did_update = False
    if request.method == 'PUT':
        myWorld.set(entity, request_post_json)
        response_status = 200
        did_update = True
    elif request.method == 'POST':
        for key in request_post_json:
            myWorld.update(entity, key, request_post_json[key])
        response_status = 200
        did_update = True
    else:
        app.logger.error(f'Unknown method [{request.method}]')
        response_status=405

    if did_update:
        new_entity = myWorld.get(entity)
        return Response(response=json.dumps(new_entity), status=response_status, mimetype='application/json')
    else:
        return Response(status=response_status)

@app.route("/world", methods=['POST','GET'])    
def world():
    '''Return the current world'''
    # TODO Should I set Headers?
    rsp = Response(response=json.dumps(myWorld.world()), status=200, mimetype='application/json')
    rsp.headers['Last-Modified'] = myWorld.get_last_modified()
    return rsp

@app.route("/entity/<entity>")    
def get_entity(entity):
    '''Return the entity from the world'''
    entity_data = myWorld.get(entity)
    if entity_data == {}:
        app.logger.warning(f'Unknown entity [{entity}], returning empty JSON')
    return entity_data

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world'''
    myWorld.clear()
    # # TODO Should I set Headers?
    return myWorld.world()

if __name__ == "__main__":
    app.run()
