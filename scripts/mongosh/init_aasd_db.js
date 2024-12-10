use('aasd');

db.jobOffers.insertOne({
    "_id": ObjectId("674aff48c8c935e125c43939"),
    "name": "test jo",
    "description": "testowe description",
    "status": 0,
    "applications": []
});

db.recruitmentInstructions.insertOne({
    "_id": ObjectId("674aff48c8c935e125c43951"),
    "job_offer_id": ObjectId("674aff48c8c935e125c43939"),
    "stage_types": [1, 2, 3],
    "stage_priorities": [1, 1, 2]
});
