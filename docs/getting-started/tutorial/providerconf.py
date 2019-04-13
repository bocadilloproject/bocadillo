from contextlib import contextmanager

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from bocadillo import provider


@provider(scope="app")
def diego():
    diego = ChatBot("Diego")

    trainer = ChatterBotCorpusTrainer(diego)
    trainer.train(
        "chatterbot.corpus.english.greetings",
        "chatterbot.corpus.english.conversations",
    )

    return diego


@provider(scope="app")
def clients():
    return set()


@provider
def save_client(clients):
    @contextmanager
    def _register(ws):
        clients.add(ws)
        try:
            yield ws
        finally:
            clients.remove(ws)

    return _register
