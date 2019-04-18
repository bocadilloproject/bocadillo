from aiodine import Store, scopes

# pylint: disable=invalid-name
STORE = Store(
    scope_aliases={"request": scopes.FUNCTION, "app": scopes.SESSION},
    providers_module="providerconf",
    default_scope=scopes.FUNCTION,
)
provider = STORE.provider
discover_providers = STORE.discover
useprovider = STORE.useprovider
consumer = STORE.consumer
