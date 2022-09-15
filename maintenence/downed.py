# this file is to be hosted when the site is down for construction
import fastapi

app = fastapi.FastAPI(debug=True)


@app.route("/")
async def root(*args, **kwargs):
    return fastapi.responses.JSONResponse(
        {"detail": "Under construction, check back in later."}, 503
    )
