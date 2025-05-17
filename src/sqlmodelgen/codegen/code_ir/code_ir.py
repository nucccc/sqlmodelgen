import ast

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Iterator, Protocol


AnnotationType = ast.Name | ast.BitOr | ast.Subscript


class AttrCallName(StrEnum):
    Field = 'Field'
    Relationship = 'Relationship'


@dataclass
class AttrCallIR:
    name: AttrCallName
    kwargs: list[ast.keyword]


@dataclass
class AttributeIR:
    name: str
    annotation: AnnotationType
    call: AttrCallIR | None


class TableArg(Protocol):

    def to_expr(self) -> ast.expr:
        pass


class UniqueTableArgIR():

    def __init__(self, col_names: list[str]):
        self._col_names = col_names

    def to_expr(self) -> ast.Call:
        return ast.Call(
            func=ast.Name('UniqueConstraint'),
            args=[ast.Constant(col_name) for col_name in self._col_names],
            keywords=[]
        )



@dataclass
class ModelIR:
    class_name: str
    table_name: str
    attrs: list[AttributeIR]
    o2m_rel_attrs: list[AttributeIR] = field(default_factory=list)
    m2o_rel_attrs: list[AttributeIR] = field(default_factory=list)
    table_args: list[TableArg] = field(default_factory=list)

    
    def iter_attr_lists(self) -> Iterator[list[AttributeIR]]:
        yield self.attrs
        yield self.o2m_rel_attrs
        yield self.m2o_rel_attrs

    
    def iter_attrs(self) -> Iterator[AttributeIR]:
        for attr_list in self.iter_attr_lists():
            for attr in attr_list:
                yield attr
    
    def iter_attr_names(self) -> Iterator[str]:
        for attr in self.iter_attrs():
            yield attr.name


    def is_attr_name_used(self, candidate_name: str) -> bool:
        # TODO: this maybe at a point for performance reasons there could be a
        # set or some other data strcture to help the performances and avoid
        # linearly iterating over attribute names
        for attr_name in self.iter_attr_names():
            if attr_name == candidate_name:
                return True
        return False
