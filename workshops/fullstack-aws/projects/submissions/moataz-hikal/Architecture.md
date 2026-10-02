# Architecture

```
 Browser
   |  1. page load (HTTP)
   v
 S3 static website  (moataz-hikal-notice-board-site, public read)
   |
   |  2. fetch() calls, JSON over HTTPS, CORS enabled
   v
 API Gateway HTTP API  (moataz-hikal-notice-board-api)
   |  AWS_PROXY, payload format 2.0
   v
 Lambda  (moataz-hikal-notice-board, Python 3.12)
   |  pymongo, TLS
   v
 MongoDB Atlas  (noticeboard_db.notices)
```

## Decisions and why
- **HTTP API instead of REST API:** cheaper, simpler CORS, and payload 2.0 gives the handler `requestContext.http.method` and `pathParameters.id` directly.
- **One Lambda for all five routes:** the logic is tiny, so one function keeps deployment to one zip and one set of environment variables.
- **MongoClient created at module level:** warm invocations reuse the connection instead of reconnecting on every request.
- **pymongo packaged in the zip (`build.py`):** Lambda does not ship pymongo; the wheel is built for `manylinux2014_x86_64` / Python 3.12 so it matches the runtime even when built on Windows.
- **Secrets in environment variables:** the Atlas URI is set on the function, never in the repo or the frontend bundle. The frontend only knows the public API URL (`VITE_API_URL`, baked in at build time).
- **Input handling:** invalid JSON or ids give 400, missing notices give 404, unexpected errors give a generic 500 (details stay in CloudWatch).

## Known limits
No authentication, and `Access-Control-Allow-Origin: *` with an open API: fine for a training exercise, not for real data. Atlas allows `0.0.0.0/0` because Lambda has no fixed IP in this setup.
