# Notice Board - Moataz Hikal

A small full-stack Notice Board: a React (Vite) single-page app on S3, a Python Lambda behind an API Gateway HTTP API, and MongoDB Atlas for storage. Deployed by hand through the AWS CLI following `ASSIGNMENT-Version1-DeployWith_AwsGui.md`.

| Part | Where |
|------|-------|
| Frontend (S3 static website) | http://moataz-hikal-notice-board-site.s3-website-us-east-1.amazonaws.com |
| API (HTTP API, `$default` stage) | https://7j6fvhcmcg.execute-api.us-east-1.amazonaws.com |
| Lambda | `moataz-hikal-notice-board` (Python 3.12) |
| Database | MongoDB Atlas, database `noticeboard_db`, collection `notices` |

## Layout
```
backend/      lambda_function.py, requirements.txt, build.py (packages lambda.zip)
frontend/     Vite + React app (list, add, edit, delete)
postmanscript/ notice-board.postman_collection.json
Architecture.md
```

## API
| Method and path | Purpose | Success |
|-----------------|---------|---------|
| `GET /notices` | List notices, newest first | 200 |
| `GET /notices/{id}` | One notice | 200, 404 |
| `POST /notices` | Create (`title` required, `content` optional) | 201, 400 |
| `PUT /notices/{id}` | Update `title` and/or `content` | 200, 404 |
| `DELETE /notices/{id}` | Delete | 200, 404 |

A malformed id returns 400. Internal errors return a generic 500 and are logged to CloudWatch.

## Deploy (what I ran)
1. Atlas: M0 cluster, database user, Network Access `0.0.0.0/0` (course setup so Lambda can connect).
2. Backend: `cd backend && python build.py` (installs pymongo for Linux x86_64 into `lambda.zip`), then create the Lambda with handler `lambda_function.lambda_handler` and the environment variables `MONGO_URI` and `MONGO_DB`.
3. API Gateway: HTTP API with an AWS_PROXY (payload 2.0) integration and the five routes above, `$default` stage with auto-deploy, CORS for `GET, POST, PUT, DELETE, OPTIONS`, plus permission for API Gateway to invoke the Lambda.
4. Frontend: `cd frontend && VITE_API_URL=<api url> npm run build`, then `aws s3 sync dist s3://<bucket> --delete`. The bucket has static website hosting (index and error document `index.html`) and a public-read bucket policy.

## Run locally
```
cd frontend
npm install
VITE_API_URL=<api url> npm run dev
```

## Security notes
- The Atlas connection string lives only in the Lambda environment variable `MONGO_URI`; it is not in this repository.
- The bucket and API are public and unauthenticated, as the exercise requires. Anyone with the link can add or delete notices, so use only sample data.
