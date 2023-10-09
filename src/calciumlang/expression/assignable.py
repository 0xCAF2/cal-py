import typing
from calciumlang.environment import Environment
import abc


class Assignable(abc.ABC):
    @abc.abstractmethod
    def assign(self, value: typing.Any, env: Environment) -> None:
        pass

    @abc.abstractmethod
    def evaluate(self, env: Environment) -> typing.Any:
        pass


class Variable(Assignable):
    def __init__(self, name: str) -> None:
        self.name = name

    def assign(self, value: typing.Any, env: Environment) -> None:
        env.context.register(self.name, value)

    def evaluate(self, env: Environment) -> typing.Any:
        return env.context.lookup(self.name)


class Attribute(Assignable):
    def __init__(
        self, obj: typing.Union[str, Assignable], properties: list[str]
    ) -> None:
        self.obj = obj
        self.properties = properties

    def assign(self, value: typing.Any, env: Environment) -> None:
        target = self._lookup(env)
        for prop in self.properties[:-1]:
            target = getattr(target, prop)
        setattr(target, self.properties[-1], value)

    def evaluate(self, env: Environment) -> typing.Any:
        target = self._lookup(env)
        for prop in self.properties:
            target = getattr(target, prop)
        return target

    def _lookup(self, env: Environment) -> typing.Any:
        if isinstance(self.obj, Variable or isinstance(self.obj, Attribute)):
            return self.obj.evaluate(env)
        return self.obj


KeyType = typing.Union[int, str, Assignable]
KeyIndex = typing.Union[int, Variable]


class Subscript(Assignable):
    def __init__(
        self,
        ref: Assignable,
        key: typing.Optional[KeyType],
        start: typing.Optional[KeyIndex] = None,
        stop: typing.Optional[KeyIndex] = None,
    ) -> None:
        self.ref = ref
        self.key = key
        self.start = start
        self.stop = stop

    def assign(self, value: typing.Any, env: Environment) -> None:
        obj: typing.Any = self.ref.evaluate(env)
        key: typing.Any = env.evaluate(self.key)
        start: typing.Optional[int] = env.evaluate(self.start)
        stop: typing.Optional[int] = env.evaluate(self.stop)

        if key is not None:
            obj[key] = value
            return
        if start is None:
            if stop is None:
                obj[:] = value
                return
            else:
                obj[:stop] = value
                return
        else:
            if stop is None:
                obj[start:] = value
                return
            else:
                obj[start:stop] = value
                return

    def evaluate(self, env: Environment) -> typing.Any:
        obj: typing.Any = self.ref.evaluate(env)
        key: typing.Any = env.evaluate(self.key)
        start: typing.Optional[int] = env.evaluate(self.start)
        stop: typing.Optional[int] = env.evaluate(self.stop)

        if key is not None:
            return obj[key]
        if start is None:
            if stop is None:
                return obj[:]
            else:
                return obj[:stop]
        else:
            if stop is None:
                return obj[start:]
            else:
                return obj[start:stop]
