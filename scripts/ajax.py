import math
import os
import json

from flask import Flask, request
from pivot_builder import generate_table
from generate_json import generate_json
from matplotlib_charts import create_pie_chart, create_bar_chart

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/map', methods=['POST'])
def handler1():
	payload=request.data
	json_request = json.loads(payload)
	jreturn=generate_json(json_request,1000)
	return jreturn, 200, {'Content-Type': 'application/JSON'}


@app.route('/', methods=['POST'])
def handler2():
  payload = request.data
  json_request = json.loads(payload) ## json_request will have all of the form data from form.html, in json format obviously
  
  html = generate_table(json_request)
  
  return html , 200, {'Content-Type': 'html'}



@app.route("/pie/young.png")
def pie_chart_young():
    return create_pie_chart('young')

@app.route("/pie/old.png")
def pie_chart_old():
    return create_pie_chart('old')

@app.route("/pie/hitrun.png")
def pie_chart_hitrun():
    return create_pie_chart('hitrun')

@app.route("/pie/fatality.png")
def pie_chart_fatality():
    return create_pie_chart('fatality')

@app.route("/pie/light.png")
def pie_chart_light():
    return create_pie_chart('light')

@app.route("/pie/young_crashtype.png")
def young_crashtype():
    return create_bar_chart()


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8765)