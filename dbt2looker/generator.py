import logging
from typing import List

import lkml

from . import models

LOOKER_DTYPE_MAP = {
    'bigquery': {
        'INT64':     'number',
        'INTEGER':   'number',
        'FLOAT':     'number',
        'NUMERIC':   'number',
        'BOOLEAN':   'yesno',
        'STRING':    'string',
        'TIMESTAMP': 'timestamp',
        'DATETIME':  'datetime',
        'DATE':      'date',
        'TIME':      'string',    # Can time-only be handled better in looker?
        'BOOL':      'yesno',
        'ARRAY':     'string',
        'GEOGRAPHY': 'string',
    },
    'snowflake': {
        'NUMBER': 'number',
        'DECIMAL': 'number',
        'NUMERIC': 'number',
        'INT': 'number',
        'INTEGER': 'number',
        'BIGINT': 'number',
        'SMALLINT': 'number',
        'FLOAT': 'number',
        'FLOAT4': 'number',
        'FLOAT8': 'number',
        'DOUBLE': 'number',
        'DOUBLE PRECISION': 'number',
        'REAL': 'number',
        'VARCHAR': 'string',
        'CHAR': 'string',
        'CHARACTER': 'string',
        'STRING': 'string',
        'TEXT': 'string',
        'BINARY': 'string',
        'VARBINARY': 'string',
        'BOOLEAN': 'yesno',
        'DATE': 'date',
        'DATETIME': 'datetime',
        'TIME': 'string',        # can we support time?
        'TIMESTAMP': 'timestamp',
        'TIMESTAMP_NTZ': 'timestamp',
        # TIMESTAMP_LTZ not supported (see https://docs.looker.com/reference/field-params/dimension_group)
        # TIMESTAMP_TZ not supported (see https://docs.looker.com/reference/field-params/dimension_group)
        'VARIANT': 'string',
        'OBJECT': 'string',
        'ARRAY': 'string',
        'GEOGRAPHY': 'string',
    },
    'redshift': {
        'SMALLINT': 'number',
        'INT2': 'number',
        'INTEGER': 'number',
        'INT': 'number',
        'INT4': 'number',
        'BIGINT': 'number',
        'INT8': 'number',
        'DECIMAL': 'number',
        'NUMERIC': 'number',
        'REAL': 'number',
        'FLOAT4': 'number',
        'DOUBLE PRECISION': 'number',
        'FLOAT8': 'number',
        'FLOAT': 'number',
        'BOOLEAN': 'yesno',
        'BOOL': 'yesno',
        'CHAR': 'string',
        'CHARACTER': 'string',
        'NCHAR': 'string',
        'BPCHAR': 'string',
        'VARCHAR': 'string',
        'CHARACTER VARYING': 'string',
        'NVARCHAR': 'string',
        'TEXT': 'string',
        'DATE': 'date',
        'TIMESTAMP': 'timestamp',
        'TIMESTAMP WITHOUT TIME ZONE': 'timestamp',
        # TIMESTAMPTZ not supported
        # TIMESTAMP WITH TIME ZONE not supported
        'GEOMETRY': 'string',
        # HLLSKETCH not supported
        'TIME': 'string',
        'TIME WITHOUT TIME ZONE': 'string',
        # TIMETZ not supported
        # TIME WITH TIME ZONE not supported
    },
    'postgres': {
        # BIT, BIT VARYING, VARBIT not supported
        # BOX not supported
        # BYTEA not supported
        # CIRCLE not supported
        # INTERVAL not supported
        # LINE not supported
        # LSEG not supported
        # PATH not supported
        # POINT not supported
        # POLYGON not supported
        # TSQUERY, TSVECTOR not supported
        'XML': 'string',
        'UUID': 'string',
        'PG_LSN': 'string',
        'MACADDR': 'string',
        'JSON': 'string',
        'JSONB': 'string',
        'CIDR': 'string',
        'INET': 'string',
        'MONEY': 'number',
        'SMALLINT': 'number',
        'INT2': 'number',
        'SMALLSERIAL': 'number',
        'SERIAL2': 'number',
        'INTEGER': 'number',
        'INT': 'number',
        'INT4': 'number',
        'SERIAL': 'number',
        'SERIAL4': 'number',
        'BIGINT': 'number',
        'INT8': 'number',
        'BIGSERIAL': 'number',
        'SERIAL8': 'number',
        'DECIMAL': 'number',
        'NUMERIC': 'number',
        'REAL': 'number',
        'FLOAT4': 'number',
        'DOUBLE PRECISION': 'number',
        'FLOAT8': 'number',
        'FLOAT': 'number',
        'BOOLEAN': 'yesno',
        'BOOL': 'yesno',
        'CHAR': 'string',
        'CHARACTER': 'string',
        'NCHAR': 'string',
        'BPCHAR': 'string',
        'VARCHAR': 'string',
        'CHARACTER VARYING': 'string',
        'NVARCHAR': 'string',
        'TEXT': 'string',
        'DATE': 'date',
        'TIMESTAMP': 'timestamp',
        'TIMESTAMP WITHOUT TIME ZONE': 'timestamp',
        # TIMESTAMPTZ not supported
        # TIMESTAMP WITH TIME ZONE not supported
        'GEOMETRY': 'string',
        # HLLSKETCH not supported
        'TIME': 'string',
        'TIME WITHOUT TIME ZONE': 'string',
        # TIMETZ not supported
        # TIME WITH TIME ZONE not supported
    }
}

looker_date_time_types = ['datetime', 'timestamp']
looker_date_types = ['date']
looker_scalar_types = ['number', 'yesno', 'string']

looker_timeframes = [
    'raw',
    'time',
    'date',
    'week',
    'month',
    'quarter',
    'year',
]


def map_adapter_type_to_looker(adapter_type: models.SupportedDbtAdapters, column_type: str):
    looker_type = LOOKER_DTYPE_MAP[adapter_type].get(column_type)
    if (column_type is not None) and (looker_type is None):
        logging.warning(f'Column type {column_type} not supported for conversion from {adapter_type} to looker. No dimension will be created.')
    return looker_type


def lookml_date_time_dimension_group(column: models.DbtModelColumn, adapter_type: models.SupportedDbtAdapters):
    return {
        'name': column.name,
        'type': 'time',
        'sql': f'${{TABLE}}.{column.name}',
        'description': column.description,
        'datatype': map_adapter_type_to_looker(adapter_type, column.data_type),
        'timeframes': ['raw', 'time', 'hour', 'date', 'week', 'month', 'quarter', 'year']
    }


def lookml_date_dimension_group(column: models.DbtModelColumn, adapter_type: models.SupportedDbtAdapters):
    return {
        'name': column.name,
        'type': 'time',
        'sql': f'${{TABLE}}.{column.name}',
        'description': column.description,
        'datatype': map_adapter_type_to_looker(adapter_type, column.data_type),
        'timeframes': ['raw', 'date', 'week', 'month', 'quarter', 'year']
    }


def lookml_dimension_groups_from_model(model: models.DbtModel, adapter_type: models.SupportedDbtAdapters):
    date_times = [
        lookml_date_time_dimension_group(column, adapter_type)
        for column in model.columns.values()
        if map_adapter_type_to_looker(adapter_type, column.data_type) in looker_date_time_types
    ]
    dates = [
        lookml_date_dimension_group(column, adapter_type)
        for column in model.columns.values()
        if map_adapter_type_to_looker(adapter_type, column.data_type) in looker_date_types
    ]
    return date_times + dates


def lookml_dimension_name_from_column(column: models.DbtModelColumn):
    return column.meta.looker.dimension.name or column.name


def lookml_dimensions_from_model(model: models.DbtModel, adapter_type: models.SupportedDbtAdapters):
    return [
        {
            'name': lookml_dimension_name_from_column(column),
            'type': map_adapter_type_to_looker(adapter_type, column.data_type),
            'sql': f'${{TABLE}}.{column.name}',
            'description': column.description
        }
        for column in model.columns.values()
        if map_adapter_type_to_looker(adapter_type, column.data_type) in looker_scalar_types
    ]


def lookml_measure_filters(measure: models.Dbt2LookerMeasure, model: models.DbtModel):
    try:
        columns = {
            column_name: model.columns[column_name]
            for f in measure.filters
            for column_name in f
        }
    except KeyError as e:
        raise ValueError(
            f'Model {model.unique_id} contains a measure that references a non_existent column: {e}\n'
            f'Ensure that dbt model {model.unique_id} contains a column: {e}'
        ) from e
    return [{
        lookml_dimension_name_from_column(columns[column_name]): fexpr
        for column_name, fexpr in f.items()
    } for f in measure.filters]


def lookml_measures_from_model(model: models.DbtModel):
    return [
        {
            'name': measure.name or f'{measure.type.value} of {column.name}',
            'type': measure.type.value,
            'sql': f'${{TABLE}}.{column.name}',
            'description': measure.description or f'{measure.type.value.capitalize()} of {column.description}',

            # Filters must reference a valid column in the dbt manifest
            **(
                {'filters': lookml_measure_filters(measure, model)}
                if measure.filters else {}
            )
        }
        for column in model.columns.values()
        for measure in column.meta.looker.measures
    ]


def lookml_view_from_dbt_model(model: models.DbtModel, adapter_type: models.SupportedDbtAdapters):
    lookml = {
        'view': {
            'name': model.name,
            'sql_table_name': f'{model.database}.{model.db_schema}.{model.name}',
            'dimension_groups': lookml_dimension_groups_from_model(model, adapter_type),
            'dimensions': lookml_dimensions_from_model(model, adapter_type),
            'measures': lookml_measures_from_model(model),
        }
    }
    contents = lkml.dump(lookml)
    filename = f'{model.name}.view'
    return models.LookViewFile(filename=filename, contents=contents)


def lookml_join_on_sql(left: str, right: str, left_on: str, right_on: str):
    return f'${{{left}.{left_on}}} = ${{{right}.{right_on}}}'


def lookml_model_from_dbt_model(model: models.DbtModel, dbt_project_name: str):
    # Note: assumes view names = model names
    #       and models are unique across dbt packages in project
    lookml = {
        'connection': dbt_project_name,
        'include': '/views/*',
        'explore': {
            'name': model.name,
            'description': model.description,
            'joins': [
                {
                    'name': model_name,
                    'type': join.type.value,
                    'relationship': join.relationship.value,
                    'sql_on': lookml_join_on_sql(
                        left=model.name,
                        left_on=join.left_on,
                        right=model_name,
                        right_on=join.right_on,
                    )
                }
                for model_name, join in model.meta.looker.joins.items()
            ]
        }
    }
    contents = lkml.dump(lookml)
    filename = f'{model.name}.model'
    return models.LookModelFile(filename=filename, contents=contents)