var AWS = require('aws-sdk');
AWS.config.update({region: "us-east-1"});


exports.handler = (event, context, callback) => {

    var documentClient = new AWS.DynamoDB.DocumentClient();

    var dataZone = event.key1;
    var dataMin = event.key2;
    var dataMax = event.key3;
    var params = {};
    //console.log(event);

    if( dataZone === '' && dataMin === '' && dataMax === ''){

	params = { 
		TableName : 'TelemetryData'
		};

    }else if ( dataZone !== '' && dataMin === '' && dataMax === '') {

	params = { 
		TableName : 'TelemetryData', 
		FilterExpression : "#ZoneID = :ZoneID", 
		ExpressionAttributeNames: {
                "#ZoneID": "ZoneID"
            	},
            	ExpressionAttributeValues : { 
			":ZoneID": dataZone,
            	}};

    }else if ( dataZone === '' && dataMin !== '' && dataMax !== '') {

            params = { 
		TableName : 'TelemetryData', 
		FilterExpression : '#cat BETWEEN :cat and :dog', 
		ExpressionAttributeNames: {
                	'#cat': 'timestamp',
            },
            	ExpressionAttributeValues : { 
			':cat': dataMin, 
			':dog': dataMax,
            }};

    }else if ( dataZone !== '' && dataMin !== '' && dataMax !== '') {

            params = { 
		TableName : 'TelemetryData', 
		FilterExpression : 
            		'#ZoneID = :ZoneID and #cat BETWEEN :cat and :dog', 
	        ExpressionAttributeNames: {
                	'#cat': 'timestamp', 
			"#ZoneID": "ZoneID"
            		},
            	ExpressionAttributeValues : { 
			":ZoneID": dataZone, 
			':cat': dataMin, 
			':dog': dataMax,
            	}};
   
    }
    
    documentClient.scan(params, function(err, data) {
        
        
        if (err) { 
		const response = { statusCode: 403, headers:{
                        'Content-Type': 'application/json'
                    },
                    body: 'Unuable to update data, error: ${err}',
                    };
            callback(err, response);
        }
        else{ 
		var newData = data.Items.map((item, index) =>{
                
               	return{ 'item': index, 'zoneID' : item.ZoneID,
                    	//'nodeId' : item.Payload.sensorID,
                    	'timestamp': item.timestamp,
                    	//'dateDone': item.Payload.createdate, 'hourDone': 
                    	//item.Payload.hour, 'timestampDone': 
                    	//item.Payload.timestamp,
                    	'dataVariables' : item.Payload.dataNode, 
                    	'variables': item.Payload.variables
               };
            });

            const response = { 
			statusCode: 200, 
			headers:{ 
                        	'Content-Type': 'application/json'
                        },
                    	body: newData
                    	};
            callback(null,response);
      }
    });
};
