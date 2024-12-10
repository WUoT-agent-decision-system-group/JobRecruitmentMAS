use('aasd');

const stageIdentifier = Number('{{STAGE_IDENTIFIER}}');
const stageResult = parseFloat('{{STAGE_RESULT}}');

db.recruitmentStages.updateOne(
    {identifier: stageIdentifier},
    {$set: {result: stageResult, status: 3}}
);