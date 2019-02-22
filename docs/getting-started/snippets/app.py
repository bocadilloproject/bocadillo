# app.py
import re
from asyncio import sleep
from json import JSONDecodeError
from typing import Dict, List, NamedTuple, Optional

from bocadillo import (
    App,
    HTTPError,
    Middleware,
    Recipe,
    Request,
    Response,
    Templates,
    hooks,
)

# We'll start by defining a few helper classes and functions.


class Course(NamedTuple):
    """Represents a course taught by a teacher."""

    id: int
    name: str
    teacher: str


class Storage:
    """In-memory storage backend for courses."""

    _id = 0

    def __init__(self):
        self._courses: List[Course] = []

    def all(self) -> List[dict]:
        return [course._asdict() for course in self._courses]

    def get(self, id: int) -> Optional[Course]:
        for course in self._courses:
            if course.id == id:
                return course
        return None

    def create(self, **kwargs) -> Course:
        self._id += 1
        kwargs["id"] = self._id
        course = Course(**kwargs)
        self._courses.append(course)
        return course


class Analytics:
    """In-memory analytics backend."""

    def __init__(self):
        self._counts: Dict[int, int] = {}

    async def mark_seen(self, id: int):
        # NOTE: `async` is not that helpful here, but
        # it would be if you had to send an HTTP request
        # to an external analytics service, e.g. with aiohttp.
        # We simulate this with a sleep.
        await sleep(0.1)
        self._counts.setdefault(id, 0)
        self._counts[id] += 1

    def top(self, n: int) -> List[int]:
        """Return IDs of the top `n` seen courses."""
        n = max(0, n)
        by_count_desc = sorted(
            self._counts, key=lambda id: self._counts[id], reverse=True
        )
        return by_count_desc[:n]


# Now, we define application-level helpers: middleware, hooks.

# Middleware!


class TokenMiddleware(Middleware):
    """Token-based authorization middleware."""

    _regex = re.compile(r"^Token: (\w+)$")

    def before_dispatch(self, req: Request, res: Response):
        """Attach API token to req, if provided in header."""
        # Request headers!
        header = req.headers.get("Authorization", "")
        match = self._regex.match(header)
        token: Optional[str] = match and match.group(1) or None
        req.token = token


def _is_valid(token: str):
    # Caution! Not production-ready.
    return token == "knowntoken"


# Hooks!


async def requires_token(req, res, params):
    """Protects a view behind token-based authorization."""
    if req.token is None or not _is_valid(req.token):
        raise HTTPError(401)


async def validate_course(req, res, params):
    """Validate a request payload for required Course fields."""
    try:
        # Request body consumption!
        # Also available: await req.body()
        data = await req.json()
    except JSONDecodeError:
        # HTTP error responses!
        raise HTTPError(400, detail="Invalid JSON")

    # NOTE: you're free to integrate a third-party
    # validation library such as Marshmallow or jsonschema.
    for field in "name", "teacher":
        if field not in data:
            raise HTTPError(400, detail=f"{field} is a required field")


# Now, let's assemble the actual application, shall we?

app = App(
    # Built-in CORS, HSTS and GZip!
    enable_cors=True,
    enable_hsts=False,  # the default
    enable_gzip=True,
    gzip_min_size=1024,  # the default
)

# Register the token middleware.
app.add_middleware(TokenMiddleware)

# Instanciate helper backends.
storage = Storage()
analytics = Analytics()


# Jinja templates!
templates = Templates(app)


# Routes! Views! Static files!
@app.route("/")
async def index(req, res):
    courses = storage.all()
    # Notes:
    # - Templates are loaded from the `./templates`
    # directory by default.
    # - Static files (powered by WhiteNoise) are
    # served by default at `/static` from the
    # `./static` directory.
    # - This means the HTML template can use a reference
    # to `/static/styles.css`.
    res.html = await templates.render("index.html", courses=courses)


# Recipes!
# (App-like group of stuff, good for cutting
# an app into manageable, bite-sized components.)
courses = Recipe("courses")


# Class-based views!
@courses.route("/")
class CoursesList:
    """API endpoints on the list of courses."""

    async def get(self, req, res):
        # Media responses! (JSON by default)
        res.media = storage.all()

    @hooks.before(validate_course)  # Hooks again!
    async def post(self, req, res):
        payload = await req.json()
        course = storage.create(**payload)
        res.media = course._asdict()
        # Status codes!
        res.status_code = 201


# F-string-powered route parameters! And validation!
# (here, `:d` stands for integer)
@courses.route("/{pk:d}")
async def get_course(req, res, pk: int):
    course = storage.get(pk)
    if course is None:
        raise HTTPError(404)

    res.media = course._asdict()

    # Background tasks!
    # Will execute after `res` has been sent
    # (but NOT in a separate thread).
    @res.background
    async def mark_course_as_seen():
        await analytics.mark_seen(pk)


# 👇 Executes `requires_token()` before the view
@courses.route("/top")
@hooks.before(requires_token)
async def get_top_courses(req, res):
    try:
        # Query parameters!
        n = int(req.query_params.get("n"))
    except TypeError:
        n = 5
    courses = [storage.get(pk)._asdict() for pk in analytics.top(n=n)]
    res.media = courses


# Mounts the routes of `courses` at `/courses` on `app`
app.recipe(courses)


# Custom error handlers!
@app.error_handler(HTTPError)
def handle_json(req, res, exc):
    res.media = {
        "error": exc.status_phrase,
        "status": exc.status_code,
        "message": "Duh!",
    }
    res.status_code = exc.status_code


if __name__ == "__main__":
    app.run()
