from typing import List, Callable, Awaitable

# ASGI
Scope = Message = dict
Receive = Callable[[], Message]
Send = Callable[[Message], None]
ASGIAppInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIAppInstance]

# WSGI
Environ = dict
StartResponse = Callable[[str, List[str]], None]
WSGIApp = Callable[[Environ, StartResponse], List[bytes]]
