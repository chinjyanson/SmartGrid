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
        ProjectionExpression: 'dayID, avgSunIrradiance, energyProduced',
        // Limit: 90,
    };
    const result = await dynamodb.scan(params).promise();
    if (!result) {
        return utils.buildResponse(503, 'Error getting energy log');
    } else {
        return utils.buildResponse(200, result.Items);
    }
}

async function addEnergyLog(energyLogInfo) {
    const dayID = energyLogInfo.dayID;
    const avgSunIrradiance = energyLogInfo.avgSunIrradiance;
    const energyProduced = energyLogInfo.energyProduced;
    const addedAt = Math.floor(Date.now() / 1000);
    const expiresAt = addedAt + (500 * 60);

    if (!dayID || !avgSunIrradiance || !energyProduced) {
        return utils.buildResponse(401, 'Invalid energy log');
    }

    if (typeof dayID !== 'number' || typeof avgSunIrradiance !== 'number' || typeof energyProduced !== 'number') {
        return utils.buildResponse(401, 'Invalid energy log');
    }

    const params = {
        TableName: energyTable,
        Item: {
            dayID: dayID,
            avgSunIrradiance: avgSunIrradiance,
            energyProduced: energyProduced,
            addedAt: addedAt,
            expiresAt: expiresAt
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