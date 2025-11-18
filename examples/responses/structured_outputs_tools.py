from enum import Enum
from typing import List, Union

import rich
from pydantic import BaseModel

import aimlapi
from aimlapi import AIMLAPI


class Table(str, Enum):
    orders = "orders"
    customers = "customers"
    products = "products"


class Column(str, Enum):
    id = "id"
    status = "status"
    expected_delivery_date = "expected_delivery_date"
    delivered_at = "delivered_at"
    shipped_at = "shipped_at"
    ordered_at = "ordered_at"
    canceled_at = "canceled_at"


class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"
    le = "<="
    ge = ">="
    ne = "!="


class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


class DynamicValue(BaseModel):
    column_name: str


class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int, DynamicValue]


class Query(BaseModel):
    """Query e-commerce tables for orders, customers or products."""

    table_name: Table
    columns: List[Column]
    conditions: List[Condition]
    order_by: OrderBy


client = AIMLAPI()

response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input="look up all my orders in november of last year that were fulfilled but not delivered on time",
    tools=[
        aimlapi.pydantic_function_tool(Query),
    ],
)

rich.print(response)

function_call = response.output[0]
assert function_call.type == "function_call"
assert isinstance(function_call.parsed_arguments, Query)
print("table name:", function_call.parsed_arguments.table_name)
