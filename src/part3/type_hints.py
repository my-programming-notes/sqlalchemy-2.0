"""
Appendix D: Python Type Hints and Postponed Evaluation of Annotations
"""
from __future__ import annotations

from typing import List, Optional, Union

from models import Employee


def get_employee(employee_id: Union[int, str]) -> Optional[Employee]:
    ...


def get_employee_py310(employee_id: int | str) -> Employee | None:
    ...


def get_employee_names(employee_ids: List[int]) -> List[Union[str, None]]:
    return []


def get_employee_names_py310(employee_ids: list[int]) -> list[str | None]:
    return []


class Node:
    def add_child(self, node: Node) -> None:
        pass


print(Node.add_child.__annotations__)
