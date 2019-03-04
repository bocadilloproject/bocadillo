from time import sleep
from tests.utils import Server
from bocadillo import App

app = App()
server = Server(app)
server.start()
sleep(3)
server.terminate()
server.join()
