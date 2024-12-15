use('aasd');

db.recruiters.insertOne({
    "_id": ObjectId("674aff48c8c935e125c12345"),
    "name": "John",
    "surname": "Wick"
});

db.jobOffers.insertOne({
    "_id": ObjectId("674aff48c8c935e125c43939"),
    "name": "test jo 1",
    "description": "testowe description 1",
    "status": 0,
    "applications": [],
    "recruiter_id" : ObjectId("674aff48c8c935e125c12345"),
    "best_candidate_id": "null", 
    "max_number_of_candidates": 2  
});

db.recruitmentInstructions.insertOne({
    "_id": ObjectId("674aff48c8c935e125c43951"),
    "job_offer_id": ObjectId("674aff48c8c935e125c43939"),
    "stage_types": [1, 2, 3],
    "stage_priorities": [1, 1, 2]
});

db.jobOffers.insertOne({
    "_id": ObjectId("674aff48c8c935e125c43333"),
    "name": "test jo 2",
    "description": "testowe description 2",
    "status": 0,
    "applications": [],
    "recruiter_id" : ObjectId("674aff48c8c935e125c12345"),
    "best_candidate_id": "null", 
    "max_number_of_candidates": 2  
});

db.recruitmentInstructions.insertOne({
    "_id": ObjectId("674aff48c8c935e125c43555"),
    "job_offer_id": ObjectId("674aff48c8c935e125c43333"),
    "stage_types": [2, 1 ],
    "stage_priorities": [1, 1]
});