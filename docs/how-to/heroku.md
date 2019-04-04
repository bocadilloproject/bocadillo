# Heroku deployment

In this guide, we will be looking at how to deploy a Bocadillo application to Heroku.
You can find the example code in the [heroku-example](https://github.com/bocadilloproject/heroku-example) repo.

## Setting things up

### Bocadillo application

Let's assume you have the following `app.py` script:

```python
from bocadillo import App

app = App()

@app.route("/")
async def index(req, res):
    res.text = "Hello, from Heroku!"

if __name__ == "__main__":
    app.run()
```

### Procfile

The [Procfile](https://devcenter.heroku.com/articles/procfile) is a text file located in the root directory of your project which explicitly declares what command should be executed to start your app.

As described in [Deployment](/discussions/deployment.md#running-with-gunicorn), the following should fit most use cases:

```txt
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
```

### `requirements.txt`

Heroku recognizes a Python app by the existence of `requirements.txt` file in the root directory (see [Python Dependencies via Pip](https://devcenter.heroku.com/articles/python-pip)). Here's an example of what yours may look like:

```txt
bocadillo
gunicorn
```

### `runtime.txt`

Place this file in the root directory with a specific Python version. [Heroku will look at it](https://devcenter.heroku.com/articles/python-runtimes) to determine which Python version to use.

```txt
python-3.6.8
```

## Deploying via the Heroku CLI

1. Log into the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) (you may need to install it on your machine):

```bash
heroku login
```

2. Create the application on Heroku, e.g.:

```bash
heroku create my-bocadillo-app
```

3. Add the app's git remote:

```
heroku git:remote -a my-bocadillo-app
```

4. Commit the changes, if any:

```bash
git add .
git commit -m “Ready to deploy to Heroku”
```

5. Deploy!

```bash
git push heroku master
```

Once this is done, you can visit the newly deployed application using `$ heroku open`.

Congrats! You've just deployed a Bocadillo application to Heroku. 🚀
