import typing

if typing.TYPE_CHECKING:
    from .applications import App


class SettingsError(Exception):
    """Raised when a setting is missing, ill-declared or invalid."""


class Settings:
    def __init__(self, obj: typing.Optional[typing.Any]):
        for setting in dir(obj):
            if not setting.isupper():
                continue
            value = getattr(obj, setting)
            setattr(self, setting, value)


class LazySettings:
    """A lazy proxy for application settings.

    Once configured, an instance of this class can be used to access settings
    from anywhere in the application code base.

    Such an instance is in fact exposed as `bocadillo.settings`.

    Settings can be accessed using:

    - Dot notation: `settings.FOO`.
    - The `getattr` builtin: `getattr(settings, "FOO")`.
    - The dict-like `.get()` method: `settings.get("FOO", "foo")`.
    """

    def __init__(self):
        self._wrapped = None

    def configure(self, obj: typing.Any = None, **options):
        if self.configured:
            raise RuntimeError("Settings are already configured")

        wrapped = Settings(obj)

        for name, option in options.items():
            if name.startswith("_"):
                continue

            if not name.isupper():
                raise SettingsError(f"Setting {name} must be uppercase.")

            setattr(wrapped, name, option)

        self._wrapped = wrapped

    @property
    def configured(self) -> bool:
        return self._wrapped is not None

    def __getattr__(self, name: str) -> typing.Any:
        if not self.configured:
            raise SettingsError(
                f"Requested setting {name} but settings aren't configured yet."
            )

        value = getattr(self._wrapped, name)

        self.__dict__[name] = value  # cache setting

        return value

    def __setattr__(self, name: str, value: typing.Any):
        if name == "_wrapped":
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)  # remove from cache
        super().__setattr__(name, value)

    def get(self, name: str, default: typing.Any = None) -> typing.Any:
        return getattr(self, name, default)

    def _clear(self):
        self._wrapped = None


settings = LazySettings()  # pylint: disable=invalid-name


def configure(app: "App", settings_obj: typing.Any = None, **kwargs) -> "App":
    """Configure the application settings and setup plugins.

    # Parameters
    settings_obj (any): an optional settings object or module.
    **kwargs (any): arbitrary settings, case-insensitive.
    """
    from .plugins import get_plugins

    kwargs = {key.upper(): value for key, value in kwargs.items()}

    settings.configure(settings_obj, **kwargs)

    for plugin in get_plugins().values():
        plugin(app)

    return app  # for convenience
