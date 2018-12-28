from typing import List, Callable, Awaitable, MutableMapping, Any

# ASGI
Scope = dict
Event = MutableMapping[str, Any]
Receive = Callable[[], Event]
Send = Callable[[Event], None]
ASGIAppInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIAppInstance]

# WSGI
Environ = dict
StartResponse = Callable[[str, List[str]], None]
WSGIApp = Callable[[Environ, StartResponse], List[bytes]]
