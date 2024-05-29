const AWS = require('aws-sdk');
const utils = require('utils');

// set the region
AWS.config.update({region: 'eu-north-1'});

const dynamodb = new AWS.DynamoDB.DocumentClient();

const usageTable = 'usage-log';

//------------mainfunction--------------
async function getUsageLog(){
    const params = {
        TableName: usageTable,
        Limit: 90
        // at maximum we take the most recent 90 entries
    };
    const result = await dynamodb.scan(params).promise();
    if (!result) {
        return utils.buildResponse(503, 'Error getting usage log');
    } else {
        return utils.buildResponse(200, result.Items);
    }
}

async function addUsageLog(usageLogInfo){
    const day = usageLogInfo.day;
    let energyUsed = usageLogInfo.energyUsed;

    if (!day || !energyUsed) {
        return utils.buildResponse(401, 'Invalid usage log');
    }

    if (typeof day !== 'number' || typeof energyUsed !== 'number') {
        return utils.buildResponse(401, 'Invalid usage log');
    }

    energyUsed = parseFloat(energyUsed.toFixed(2));

    const params = {
        TableName: usageTable,
        Item: {
            day: day,
            energyUsed: energyUsed
        }
    };

    try {
        await dynamodb.put(params).promise();
        return utils.buildResponse(200, 'Usage log added');
    } catch (error) {
        console.error('Error adding usage log: ', error);
        return utils.buildResponse(500, 'Error adding usage log');
    }
}

module.exports = {
    getUsageLog,
    addUsageLog
}