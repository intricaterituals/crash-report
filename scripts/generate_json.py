from pivot_builder import read_csv

import json

csvfile = 'crashes.csv'

def generate_json(json_request,maxgiven):

    data = read_csv(csvfile)
    XY=[]
    json_output={}
    
    i=1
    while i<len(data[1]):
        XY.append([data[1][i][0],data[1][i][1]])
        i+=1




    json_output["max"]=maxgiven

    datar=[]
    for coord in XY:
        datar.append({"lng":float(coord[0]),"lat":float(coord[1]),"count":1})

    json_output["data"]=datar

    json_data=json.dumps(json_output)
    return json_data
