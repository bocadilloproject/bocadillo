from typing import List, Callable, Awaitable, MutableMapping, Any

# ASGI
Scope = dict
Message = MutableMapping[str, Any]
Receive = Callable[[], Message]
Send = Callable[[Message], None]
ASGIAppInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIAppInstance]

# WSGI
Environ = dict
StartResponse = Callable[[str, List[str]], None]
WSGIApp = Callable[[Environ, StartResponse], List[bytes]]
