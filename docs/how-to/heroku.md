# Heroku deployment

In this guide, we will be looking at how to deploy a Bocadillo application to Heroku.
You can find the example code in the [heroku-example](https://github.com/bocadilloproject/heroku-example) repo.

## Bocadillo application

Let's assume you have the following `app.py` script:

```
from bocadillo import App

app = App()

@app.route("/")
async def index(req, res):
    res.text = "Hello, from Heroku!"

if __name__ == "__main__":
    app.run()
```

## Procfile

The [Procfile](https://devcenter.heroku.com/articles/procfile) is a text file located in the root directory of your project which explicitly declares what command should be executed to start your app.

As described in [Deployment](/discussions/deployment.md#running-with-gunicorn), the following should fit most use cases:

```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
```

## requirements.txt

Heroku recognizes a Python app by the existence of requirements.txt file in the root directory (see [Python Dependencies via Pip](https://devcenter.heroku.com/articles/python-pip)). Here's an example of what yours may look like:

```
bocadillo
gunicorn
```

## runtime.txt

Place this file in the root directory with a specific Python version. [Heroku will look at it](https://devcenter.heroku.com/articles/python-runtimes) to determine which Python version to use.

```
python-3.6.8
```

## Heroku CLI

To interact with Heroku from the command line, make sure you have the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed.

## Create a Heroku application

```sh
heroku login    # This will ask you to enter email id and password

heroku create my-bocadillo-app  # This will create an application with given name in Heroku

heroku git:remote -a my-bocadillo-app   # This will add a git remote to an app repository so that you can refer to it when deploying
```

## Commit the changes and deploy!

```
git add .       # Add all the files

git commit -m “Ready to deploy to Heroku”     # Commit the code

git push heroku master      # This will push the entire app on Heroku Server

heroku open     # Visit the app through generated URL or with this command

heroku logs     # This is to check the logs, if anything goes wrong.
```

That's it! You've just deployed a Bocadillo application to Heroku. 🚀
