# this file is to be hosted when the site is down for construction
import fastapi
import slowapi
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi import util

limiter = slowapi.Limiter(key_func=util.get_remote_address)
app = fastapi.FastAPI(debug=True)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.route("/")
@limiter.limit("1/minute")
async def root(request: fastapi.Request, *args, **kwargs):
    return fastapi.responses.JSONResponse(
        {"detail": "Under construction, check back in later."}, 503
    )
