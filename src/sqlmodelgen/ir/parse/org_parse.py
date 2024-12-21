'''
there is the need to take the dictionary returned by sqloxide and reorganize it
into some data which is easier to digest
'''

from dataclasses import dataclass


@dataclass
class ColumnOptions:
    unique: bool
    not_null: bool
    primary_key: bool


@dataclass
class FKConstraint:
    column_name: str
    foreign_table: str
    foreign_column: str


@dataclass
class TableConstraints:
    primary_key: list[str] | None
    foreign_key: list[FKConstraint] | None = None


def collect_data_type(data_type_parsed : str | dict) -> str:
    '''
    at times the data type could be either a string or a dictionary,
    and a string could be returned out of it
    '''
    if type(data_type_parsed) is str:
        return data_type_parsed
    
    if type(data_type_parsed) is dict:
        custom = data_type_parsed.get('Custom')
        if custom:
            for elem in custom:
                if len(elem) == 0:
                    continue
                val = elem[0].get('value')
                if val is None:
                    continue
                return val

        # by default for a dict return the first key in the dictionary
        return next(key for key in data_type_parsed.keys())

    # by default return any
    return 'any'


def collect_column_options(options_parsed: list[dict[str, any]]) -> ColumnOptions:
    '''
    collect_column_options takes the list at the "option" keyword for
    every column, and derives options out of these
    '''
    col_opts = ColumnOptions(
        unique=False,
        not_null=False,
        primary_key=False
    )

    for elem in options_parsed:
        option = elem.get('option')
        if option == 'NotNull':
            col_opts.not_null = True
        elif type(option) is dict and 'Unique' in option.keys():
            col_opts.unique = True
            col_opts.primary_key = option['Unique']['is_primary']
        
    return col_opts


def collect_table_contraints(tab_constraints_parsed: list[dict[str, any]]) -> TableConstraints:
    tab_constraints = TableConstraints(
        primary_key=None
    )
    
    for constraint in tab_constraints_parsed:
        primary_key_constraint = constraint.get('PrimaryKey')
        if primary_key_constraint:
            tab_constraints.primary_key = [
                elem['value'] for elem in primary_key_constraint['columns']
            ]
            continue

        # NOTE: for now this shall just support the case of foreign key
        # constraints regarding just one 
        fk_constraint = constraint.get('ForeignKey')
        if fk_constraint:
            column_name = fk_constraint['columns'][0]['value']
            foreign_table = fk_constraint['foreign_table'][0]['value']
            foreign_column = fk_constraint['referred_columns'][0]['value']
            if tab_constraints.foreign_key is None:
                tab_constraints.foreign_key = list()
            tab_constraints.foreign_key.append(
                FKConstraint(
                    column_name=column_name,
                    foreign_table=foreign_table,
                    foreign_column=foreign_column
                )
            )

    return tab_constraints
