# chatbot/bot.py
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

diego = ChatBot("Diego")

trainer = ChatterBotCorpusTrainer(diego)
trainer.train(
    "chatterbot.corpus.english.greetings",
    "chatterbot.corpus.english.conversations",
)
