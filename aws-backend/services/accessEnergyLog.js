const AWS = require('aws-sdk');
const utils = require('utils');

// set the region
AWS.config.update({region: 'eu-north-1'});

// create the dynamodb object
const dynamodb = new AWS.DynamoDB.DocumentClient();

// choose the db table to use
const energyTable = 'energy-log';

//------------mainfunction--------------
async function getEnergyLog() {
    const params = {
        TableName: energyTable,
        Limit: 90
        // at maximum we take the most recent 90 entries
    };
    const result = await dynamodb.scan(params).promise();
    if (!result) {
        return utils.buildResponse(503, 'Error getting energy log');
    } else {
        return utils.buildResponse(200, result.Items);
    }
}

async function addEnergyLog(energyLogInfo) {
    const day = energyLogInfo.day;
    const avgSunIrradiance = energyLogInfo.avgSunIrradiance;
    const energyProduced = energyLogInfo.energyProduced;

    if (!day || !avgSunIrradiance || !energyProduced) {
        return utils.buildResponse(401, 'Invalid energy log');
    }

    if (typeof day !== 'number' || typeof avgSunIrradiance !== 'number' || typeof energyProduced !== 'number') {
        return utils.buildResponse(401, 'Invalid energy log');
    }

    const params = {
        TableName: energyTable,
        Item: {
            day: day,
            avgSunIrradiance: avgSunIrradiance,
            energyProduced: energyProduced
        }
    };

    try {
        await dynamodb.put(params).promise();
        return utils.buildResponse(200, 'Energy log added');
    } catch (error) {
        console.error('Error adding energy log: ', error);
        return utils.buildResponse(500, 'Error adding energy log');
    }
}

module.exports = {
    addEnergyLog,
    getEnergyLog
};