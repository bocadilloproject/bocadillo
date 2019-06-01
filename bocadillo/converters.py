import decimal
import inspect
from datetime import date, datetime, time
from functools import wraps
import typing

import typesystem

FIELD_ALIASES: typing.Dict[typing.Type, typesystem.Field] = {
    int: typesystem.Integer,
    float: typesystem.Float,
    bool: typesystem.Boolean,
    decimal.Decimal: typesystem.Decimal,
    date: typesystem.Date,
    time: typesystem.Time,
    datetime: typesystem.DateTime,
}


class PathConversionError(typesystem.ValidationError):
    pass


class Converter:

    __slots__ = ("func", "signature", "annotations", "required_params")

    def __init__(self, func: typing.Callable):
        self.func = func
        self.signature = inspect.signature(self.func)

        self.annotations: typing.Dict[str, typing.Type] = {
            param.name: param.annotation
            for param in self.signature.parameters.values()
            if param.annotation is not inspect.Parameter.empty
        }
        self.required_params = set(
            param.name
            for param in self.signature.parameters.values()
            if param.default is inspect.Parameter.empty
        )

    def convert(self, args: tuple, kwargs: dict) -> typing.Tuple[tuple, dict]:
        bound: inspect.BoundArguments = self.signature.bind(*args, **kwargs)

        errors: typing.List[typesystem.ValidationError] = []

        for param_name, value in bound.arguments.items():
            try:
                annotation = self.annotations[param_name]
            except KeyError:
                continue

            # Find the TypeSystem field for the parameter's annotation.
            if isinstance(annotation, typesystem.Field):
                field = annotation
            else:
                try:
                    field = FIELD_ALIASES[annotation]()
                except KeyError:
                    continue

            # Perform validation.
            try:
                value = field.validate(value)
            except typesystem.ValidationError as exc:
                # NOTE: `add_prefix` sets the key of the error in the final
                # error's dict representation.
                errors.extend(exc.messages(add_prefix=param_name))
            else:
                bound.arguments[param_name] = value

        if errors:
            raise PathConversionError(messages=errors)

        # NOTE: apply defaults last to prevent validating the default values.
        # It's faster and less bug-prone.
        bound.apply_defaults()

        return bound.args, bound.kwargs


class ViewConverter(Converter):

    __slots__ = ("query_parameters",)

    def __init__(self, func: typing.Callable):
        super().__init__(func)

        self.query_parameters = set(
            param.name
            for param in self.signature.parameters.values()
            if param.default is not inspect.Parameter.empty
        )

    def get_query_params(self, args: tuple, kwargs: dict) -> dict:
        raise NotImplementedError

    def convert(self, args: tuple, kwargs: dict) -> typing.Tuple[tuple, dict]:
        query_params = self.get_query_params(args, kwargs)

        for param_name in self.query_parameters:
            if param_name in query_params:
                kwargs[param_name] = query_params[param_name]

        return super().convert(args, kwargs)


def convert_arguments(
    func: typing.Callable, converter_class: typing.Type[Converter]
) -> typing.Callable:
    converter = converter_class(func)

    @wraps(func)
    async def converted(*args, **kwargs):
        args, kwargs = converter.convert(args, kwargs)
        return await func(*args, **kwargs)

    return converted
