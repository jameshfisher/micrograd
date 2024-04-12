import random
from typing import Iterable, TypedDict, Unpack
from micrograd.engine import Value, ValueLike


class Module:

    def zero_grad(self) -> None:
        for p in self.parameters():
            p.grad = 0

    def parameters(self) -> list[Value]:
        return []


class Neuron(Module):
    w: list[Value]
    b: Value
    nonlin: bool

    def __init__(self, nin: int, nonlin: bool = True):
        self.w = [Value(random.uniform(-1, 1)) for _ in range(nin)]
        self.b = Value(0)
        self.nonlin = nonlin

    def __call__(self, x: Iterable[ValueLike]) -> Value:
        act = sum((wi * xi for wi, xi in zip(self.w, x)), self.b)
        return act.relu() if self.nonlin else act

    def parameters(self) -> list[Value]:
        return self.w + [self.b]

    def __repr__(self):
        return f"{'ReLU' if self.nonlin else 'Linear'}Neuron({len(self.w)})"


LayerKWArgs = TypedDict("LayerKWArgs", nonlin=bool)


class Layer(Module):
    neurons: list[Neuron]

    def __init__(self, nin: int, nout: int, **kwargs: Unpack[LayerKWArgs]):
        self.neurons = [Neuron(nin, **kwargs) for _ in range(nout)]

    def __call__(self, x: Iterable[ValueLike]) -> list[Value]:
        return [n(x) for n in self.neurons]

    def parameters(self):
        return [p for n in self.neurons for p in n.parameters()]

    def __repr__(self):
        return f"Layer of [{', '.join(str(n) for n in self.neurons)}]"


class MLP(Module):
    layers: list[Layer]

    def __init__(self, nin: int, nouts: list[int]):
        sz = [nin] + nouts
        self.layers = [
            Layer(sz[i], sz[i + 1], nonlin=i != len(nouts) - 1)
            for i in range(len(nouts))
        ]

    def __call__(self, x: list[ValueLike]) -> list[Value]:
        for layer in self.layers:
            x = layer(x)
        return x

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]

    def __repr__(self):
        return f"MLP of [{', '.join(str(layer) for layer in self.layers)}]"
