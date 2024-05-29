const AWS = require('aws-sdk');
const utils = require('utils');

AWS.config.update({region: 'eu-north-1'});

const dynamodb = new AWS.DynamoDB.DocumentClient();

const tradeTable = 'trade-log';

//------------mainfunction--------------
// NEED TO FIX THIS LIMITTING 
async function getTradeLog(){
    const params = {
        TableName: tradeTable,
        Limit: 100,
        ScanIndexForward: false
    };

    const data = await dynamodb.scan(params).promise();
    if (!data) {
        return utils.buildResponse(503, 'Error getting trade log');
    } else {
        const sortedItems = data.Items.sort((a, b) => b.day - a.day);
        const recentItems = sortedItems.slice(0, 90);
        return utils.buildResponse(200, recentItems);
    }
}

async function addTradeLog(tradeLogInfo){
    const day = tradeLogInfo.day;
    const energyBought = tradeLogInfo.energyBought;
    const energySold = tradeLogInfo.energySold;
    const earnings = tradeLogInfo.earnings;

    if (!day || !energyBought || !energySold || !earnings) {
        return utils.buildResponse(401, 'Invalid trade log');
    }

    if (typeof day !== 'number' || typeof energyBought !== 'number' || typeof energySold !== 'number' || typeof earnings !== 'number') {
        return utils.buildResponse(401, 'Invalid trade log');
    }

    const params = {
        TableName: tradeTable,
        Item: {
            day: day,
            energyBought: energyBought,
            energySold: energySold,
            earnings: earnings
        }
    };
    try {
        await dynamodb.put(params).promise();
        return utils.buildResponse(200, 'Trade log added');
    } catch (error) {
        console.error('Error adding trade log: ', error);
        return utils.buildResponse(500, 'Error adding trade log');
    }
}

module.exports = {
    addTradeLog,
    getTradeLog
};