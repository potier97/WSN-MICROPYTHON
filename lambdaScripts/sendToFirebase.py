import json
import urllib3

def lambda_handler(event, context):
    #print(event)

    nodo01 = event["node01"]
    if '""' in nodo01:
        nodo01 = nodo01.replace("''", "'")

    nodo01 = json.loads(nodo01.replace("'", '"'))
    nodo02 = json.loads(event["node02"].replace("'", '"'))
    nodo03 = json.loads(event["node03"].replace("'", '"'))
    nodo04 = json.loads(event["node04"].replace("'", '"'))
    nodo05 = json.loads(event["node05"].replace("'", '"'))

    data = [{
	'zone': 'invernadero',
	'nodeId': nodo01["S"],
        'humedad_ambiente' : nodo01["H"],
	'temperatura_ambiente' : nodo01["T"]
    },{
        'zone': 'airelibre',
	'nodeId': nodo02["S"],
	'humedad_ambiente' : nodo02["H"],
	'temperatura_ambiente' : nodo02["T"]
     },{
        'zone': 'invernadero',
	'nodeId': nodo03["S"],
	'humedad_ambiente' : nodo03["H"],
        'temperatura_ambiente' : nodo03["T"]
     },{
        'zone': 'airelibre',
	'nodeId': nodo04["S"],
	'humedad_ambiente' : nodo04["H"],
	'temperatura_ambiente' : nodo04["T"]
     },{
        'zone': 'invernadero',
	'nodeId': nodo05["S"],
	'humedad_ambiente' : nodo05["H"],
        'temperatura_ambiente' : nodo05["T"]
     }]

    #print(data)

    url = "https://<YOUR-FIREBA-ID>.firebaseio.com/<YOUR-COLLECTION.NAME>.json"
    http = urllib3.PoolManager()

    response = http.request('POST',
                        url,
			body = json.dumps(data),
			headers = {'Content-Type': 'application/json'},
                        retries = False)

    return {
	'statusCode': 200,
	'body': json.dumps('Good')
	}
