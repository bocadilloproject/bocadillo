# blog.py
from bocadillo import API, HTTPError, view
import traceback
from bocadillo.error_handlers import error_to_text
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist
from models import Post, Category
from utils import get_or_404

api = API()

# Database setup.


@api.on("startup")
async def db_init():
    await Tortoise.init(
        db_url="sqlite://db.sqlite", modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()


@api.on("shutdown")
async def db_cleanup():
    await Tortoise.close_connections()


# Routes.


@api.route("/")
async def home(req, res):
    posts = await Post.all().prefetch_related("category")
    res.html = await api.template("home.html", posts=posts)


@api.route("/new")
class PostCreate:
    async def get(self, req, res):
        # Simple GET request. Display the form page.
        categories = await Category.all()
        res.html = await api.template("post_create.html", categories=categories)

    async def post(self, req, res):
        # Form data was submitted.
        form: dict = await req.form()

        # Get the category object based on the given category name, or
        # create it if it does not exist.
        category = form.pop("category")
        try:
            form["category"] = await Category.get(name=category)
        except DoesNotExist:
            form["category"] = await Category.create(name=category)

        # Create a new post in the database.
        post = Post(**form)
        await post.save()

        # Redirect to the post's detail page.
        api.redirect(name="post_detail", pk=post.id)


@api.route("/{pk:d}")
async def post_detail(req, res, pk: int):
    post = await get_or_404(Post, id=pk, prefetch_related="category")
    res.html = await api.template("post_detail.html", post=post)


@api.route("/{pk:d}/delete")
class PostDelete:
    async def get(self, req, res, pk: int):
        # Simple GET request. Display the confirmation page.
        post = await get_or_404(Post, id=pk)
        res.html = await api.template("post_delete.html", post=post)

    async def post(self, req, res, pk: int):
        # Delete the post.
        # NOTE: we do not use the DELETE method because it is not
        # supported by HTML forms.
        post = await get_or_404(Post, id=pk)
        await post.delete()
        api.redirect(name="home")


if __name__ == "__main__":
    api.run(debug=True)
