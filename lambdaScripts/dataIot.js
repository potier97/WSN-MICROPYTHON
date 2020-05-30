'use strict';
var AWS = require("aws-sdk");
AWS.config.update({region: 'us-east-1'});

exports.handler = async (event) => {

    var dynamodb = new AWS.DynamoDB.DocumentClient();


    //console.log(event); console.log(typeof(event));

    var Node1 = event.node01;
    var Node2 = event.node02;
    var Node3 = event.node03;
    var Node4 = event.node04;
    var Node5 = event.node05;

    //console.log(Node1);
    //console.log(Node3);
    //console.log(Node2);
    //console.log(Node4); console.log(Node5);

    var NodeFixed = Node1.replace("0''}", "0'}")

    var data1 = NodeFixed.replace(/'/g, '"');

    var data2 = Node2.replace(/'/g, '"');
    var data3 = Node3.replace(/'/g, '"');
    var data4 = Node4.replace(/'/g, '"');
    var data5 = Node5.replace(/'/g, '"');

    var dataNode1 = JSON.parse(data1);
    var dataNode2 = JSON.parse(data2);
    var dataNode3 = JSON.parse(data3);
    var dataNode4 = JSON.parse(data4);
    var dataNode5 = JSON.parse(data5);

    var temNode1 = dataNode1.T;
    var humNode1 = dataNode1.H;
    var idNode1 = dataNode1.S;

    //console.log(idNode1);

    var temNode2 = dataNode2.T;
    var humNode2 = dataNode2.H;
    var idNode2 = dataNode2.S;

    //console.log(idNode2);

    var temNode3 = dataNode3.T;
    var humNode3 = dataNode3.H;
    var idNode3  = dataNode3.S;

    var temNode4 = dataNode4.T;
    var humNode4 = dataNode4.H;
    var idNode4 = dataNode4.S;

    var temNode5 = dataNode5.T;
    var humNode5 = dataNode5.H;
    var idNode5 = dataNode5.S;

    var now = +new Date;
    var n = now.toString();
    //console.log(typeof(n))

    var now2 = +new Date;
    var nn = now2.toString();
    //console.log(typeof(n))

    try{
        var paramsInvernadero = await { 
		TableName:"TelemetryData",
            	Item:{
                	"ZoneID" : "invernadero", 
			"timestamp": n, 
			"Payload" :{ 
                    		"ZoneID" : "invernadero", 
				"dataNode" :[
                            		{ 
					"sensorID" : idNode1, 
					"NodoID" : "1", 
                                	"humedad_ambiente" : humNode1,
                                	 "temperatura_ambiente" : temNode1
                             		},
                             		{ 
					"sensorID" : idNode3, 
					"NodoID" : "3", 
                                	"humedad_ambiente" : humNode3, 
                                	"temperatura_ambiente" : temNode3
                            		},
                             		{ 
					"sensorID" : idNode5, 
					"NodoID" : "5", 
                                	"humedad_ambiente" : humNode5, 
                                	"temperatura_ambiente" : temNode5
                            		}
                        	], 
				"variables" :[ 
					"humedad_ambiente", 
                        		"temperatura_ambiente"
					 ]
                		}
            		}
        	};
        await dynamodb.put(paramsInvernadero).promise();

        var paramsAirelibre = await { 
		TableName:"TelemetryData", 
		Item:{ 
                	"ZoneID" : "airelibre", 
			"timestamp": nn, 
			"Payload" :{
                    		"ZoneID" : "airelibre", 
				"dataNode" :[ 
					{ 
					"sensorID" : idNode2, 
					"NodoID" : "2",
                                	"humedad_ambiente" : humNode2, 
                                	"temperatura_ambiente" : temNode2
                            		},
                             		{ 
					"sensorID" : idNode4, 
					"NodoID" : "4", 
                                	"humedad_ambiente" : humNode4, 
                                	"temperatura_ambiente" : temNode4
                            		}
                        	], 
				"variables" :[ 
					"humedad_ambiente", 
                        		"temperatura_ambiente" 
					]
                		}
            		}
        	};
        await dynamodb.put(paramsAirelibre).promise();

    }catch(err){
            console.log('This is the err: ', err)
    }

    const response = { 
		statusCode: 200, 
		body: JSON.stringify('Insert Data succesful'),
            };
            return response;
};
