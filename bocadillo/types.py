from typing import List, Callable, Coroutine

ASGIAppInstance = Callable[[Callable, Callable], Coroutine]
ASGIApp = Callable[[dict], ASGIAppInstance]
WSGIApp = Callable[[dict, Callable], List[bytes]]
