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


class DynamicValue(BaseModel):
    column_name: str


class Condition(BaseModel):
    column: str
    operator: str  # e.g. "between", "=", ">=", etc.
    value: Union[str, int, DynamicValue, List[str]]


class Query(BaseModel):
    table_name: Table
    columns: List[str]
    conditions: List[Condition]
    order_by: Union[str, List[str]]


client = AIMLAPI()

completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant. The current date is August 6, 2024. You help users query for the data they are looking for by calling the query function.",
        },
        {
            "role": "user",
            "content": "look up all my orders in november of last year that were fulfilled but not delivered on time",
        },
    ],
    tools=[
        aimlapi.pydantic_function_tool(Query),
    ],
)

tool_call = (completion.choices[0].message.tool_calls or [])[0]
rich.print(tool_call.function)
assert isinstance(tool_call.function.parsed_arguments, Query)
print(tool_call.function.parsed_arguments.table_name)
