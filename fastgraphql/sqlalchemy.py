import logging

from typing import Any, Callable, List, Optional, Tuple, Type, TypeVar

from fastgraphql.context import AdaptContext
from fastgraphql.exceptions import GraphQLFactoryException
from fastgraphql.scalars import GraphQLScalar
from fastgraphql.schema import GraphQLSchema, SelfGraphQL
from fastgraphql.types import (
    GraphQLArray,
    GraphQLDataType,
    GraphQLType,
    GraphQLTypeAttribute,
)
from fastgraphql.utils import DefaultCase, DefaultUnchanged

try:
    from sqlalchemy import ARRAY, Column
    from sqlalchemy.exc import NoInspectionAvailable
    from sqlalchemy.inspection import inspect
    from sqlalchemy.orm import Mapper, RelationshipProperty
    from sqlalchemy.sql.type_api import TypeEngine

except ImportError as e:  # pragma: no cover
    raise ImportError("Please use `pip install fastgraphql[sqlalchemy]`") from e

T = TypeVar("T")

CreateGraphQLTypeSignature = Callable[
    [Type[Any], Optional[List[str]], Optional[str], Optional[AdaptContext]],
    Tuple[GraphQLDataType, bool],
]

logger = logging.getLogger(__name__)


def adapt_sqlalchemy_graphql(
    python_type: Type[T],
    parse_type_func: CreateGraphQLTypeSignature,
    schema: GraphQLSchema,
    name: Optional[str],
    exclude_model_attrs: Optional[List[str]],
    as_input: bool,
    context: Optional[AdaptContext],
    default_case: DefaultCase = DefaultUnchanged(),
) -> GraphQLType:

    if not exclude_model_attrs:
        exclude_model_attrs = []
    if not name:
        name = default_case(python_type.__name__)
    try:
        mapper = inspect(python_type)
    except NoInspectionAvailable as e:
        raise GraphQLFactoryException(
            f"{python_type.__qualname__} does not seems to be a SQLAlchemy Model"
        ) from e

    if graphql_type := SelfGraphQL.check_if_exists(
        python_type=python_type, as_input=as_input
    ):
        return graphql_type

    foreign_columns = []
    column: Column[Any]
    graphql_type = GraphQLType(name=name, as_input=as_input, python_type=python_type)

    SelfGraphQL.add_type_metadata(
        python_type=python_type, graphql_type=graphql_type, as_input=as_input
    )

    for column in mapper.columns:
        if not isinstance(column, Column):
            logger.warning(
                "SQLAlchemy type %s are not supported, yet...",
                column.__class__.__name__,
            )
            continue
        if column.name in exclude_model_attrs:
            continue

        if column.foreign_keys:
            foreign_columns.append(column)
            continue

        graphql_type.add_attribute(
            adapt_column(
                column=column,
                parse_type_func=parse_type_func,
                schema=schema,
                default_case=default_case,
                context=AdaptContext(
                    graphql_type=graphql_type,
                    python_field="",
                    graphql_field="",
                    parent_context=context,
                ),
            )
        )

    adapt_relation(
        graphql_type=graphql_type,
        mapper=mapper,
        foreign_columns=foreign_columns,
        schema=schema,
        parse_type_func=parse_type_func,
        as_input=as_input,
        default_case=default_case,
        context=context,
    )

    for column in foreign_columns:
        graphql_type.add_attribute(
            adapt_column(
                column=column,
                parse_type_func=parse_type_func,
                schema=schema,
                default_case=default_case,
                context=context,
            )
        )

    if as_input:
        schema.add_input_type(graphql_type=graphql_type)
    else:
        schema.add_type(graphql_type=graphql_type)

    return graphql_type


def adapt_relation(
    graphql_type: GraphQLType,
    mapper: Mapper,
    foreign_columns: List[Column[Any]],
    schema: GraphQLSchema,
    parse_type_func: CreateGraphQLTypeSignature,
    as_input: bool,
    default_case: DefaultCase,
    context: Optional[AdaptContext],
) -> None:
    relation: RelationshipProperty[Any]
    for relation in mapper.relationships:
        nullable = any(c.nullable for c in relation.local_columns)
        graphql_type.add_attribute(
            GraphQLTypeAttribute(
                graphql_name=default_case(relation.key),
                python_name=relation.key,
                type_reference=adapt_sqlalchemy_graphql(
                    python_type=relation.mapper.entity,
                    schema=schema,
                    as_input=as_input,
                    parse_type_func=parse_type_func,
                    name=None,
                    exclude_model_attrs=None,
                    context=context,
                ).ref(nullable=nullable),
            )
        )

        if all(
            [p[0].table.name == p[1].table.name for p in relation.local_remote_pairs]
        ):
            for column in relation.remote_side:
                foreign_columns.remove(column)
        else:
            for column in relation.local_columns:
                foreign_columns.remove(column)


def parse_sql_type(
    sql_type: TypeEngine[Any],
    parse_type_func: CreateGraphQLTypeSignature,
    context: Optional[AdaptContext],
) -> Tuple[GraphQLDataType, bool]:
    if isinstance(sql_type, ARRAY):
        item_type, nullable = parse_sql_type(
            sql_type.item_type, parse_type_func=parse_type_func, context=context
        )

        return GraphQLArray(item_type=item_type.ref(nullable=nullable)), False
    else:
        return parse_type_func(sql_type.python_type, None, None, context)


def adapt_column(
    column: Column[Any],
    parse_type_func: CreateGraphQLTypeSignature,
    schema: GraphQLSchema,
    default_case: DefaultCase,
    context: Optional[AdaptContext],
) -> GraphQLTypeAttribute:
    graphql_type, nullable = parse_sql_type(
        sql_type=column.type, parse_type_func=parse_type_func, context=context
    )
    if isinstance(graphql_type, GraphQLScalar) and not graphql_type.default_scalar:
        schema.add_scalar(graphql_type)
    if "graphql_name" in column.info:
        graphql_name = column.info["graphql_name"]
    else:
        graphql_name = default_case(column.name)

    if "graphql_type" in column.info:
        graphql_type = column.info["graphql_type"]

    return GraphQLTypeAttribute(
        graphql_name=graphql_name,
        python_name=column.name,
        type_reference=graphql_type.ref(nullable=column.nullable),
    )
