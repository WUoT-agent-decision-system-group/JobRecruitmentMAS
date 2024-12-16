use('aasd');

const stageIdentifier = ObjectId('{{STAGE_IDENTIFIER}}'); 
const stageResult = parseFloat('{{STAGE_RESULT}}');

db.recruitmentStages.updateOne(
    { _id: stageIdentifier }, 
    { $set: { result: stageResult, status: 3 } }
);