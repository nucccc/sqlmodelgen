'''
there is the need to take the dictionary returned by sqloxide and reorganize it
into some data which is easier to digest
'''

from dataclasses import dataclass


@dataclass
class ColumnOptions:
    unique: bool
    not_null: bool


@dataclass
class TableConstraints:
    pass


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
        not_null=False
    )
    
    for elem in options_parsed:
        option = elem.get('option')
        if option == 'NotNull':
            col_opts.not_null = True
        elif type(option) is dict and 'Unique' in option.keys():
            col_opts.unique = True
        
    return col_opts