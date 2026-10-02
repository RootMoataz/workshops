"""Notice Board API: AWS Lambda behind an API Gateway HTTP API, storing notices in MongoDB Atlas."""
import json
import os

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient

# Created once per container so warm invocations reuse the connection.
client = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=5000)
notices = client[os.environ.get("MONGO_DB", "noticeboard_db")]["notices"]

HEADERS = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}


def respond(status, body):
    return {"statusCode": status, "headers": HEADERS, "body": json.dumps(body)}


def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method")
    notice_id = (event.get("pathParameters") or {}).get("id")
    try:
        body = json.loads(event["body"]) if event.get("body") else {}
    except ValueError:
        return respond(400, {"error": "Body must be valid JSON"})

    try:
        object_id = ObjectId(notice_id) if notice_id else None
    except InvalidId:
        return respond(400, {"error": "Invalid notice id"})

    try:
        if method == "GET" and not object_id:
            return respond(200, [serialize(n) for n in notices.find().sort("_id", -1)])
        if method == "GET":
            notice = notices.find_one({"_id": object_id})
            return respond(200, serialize(notice)) if notice else respond(404, {"error": "Notice not found"})
        if method == "POST" and not object_id:
            title = str(body.get("title", "")).strip()
            if not title:
                return respond(400, {"error": "title is required"})
            notice = {"title": title, "content": str(body.get("content", ""))}
            notice["_id"] = notices.insert_one(notice).inserted_id
            return respond(201, serialize(notice))
        if method == "PUT" and object_id:
            changes = {k: str(body[k]) for k in ("title", "content") if k in body}
            if not changes:
                return respond(400, {"error": "Nothing to update"})
            result = notices.update_one({"_id": object_id}, {"$set": changes})
            if not result.matched_count:
                return respond(404, {"error": "Notice not found"})
            return respond(200, {"message": "Notice updated successfully"})
        if method == "DELETE" and object_id:
            result = notices.delete_one({"_id": object_id})
            if not result.deleted_count:
                return respond(404, {"error": "Notice not found"})
            return respond(200, {"message": "Notice deleted successfully"})
        return respond(400, {"error": "Unsupported route"})
    except Exception:
        # Details stay in CloudWatch; the client gets no internals.
        print("unhandled error", flush=True)
        import traceback
        traceback.print_exc()
        return respond(500, {"error": "Internal server error"})
