#!/usr/bin/env python
"""
Input/output functions to read and write data files or tables.

See synapse_io.py for reading from and writing to Synapse.org.

Authors:
    - Arno Klein, 2015  (arno@sagebase.org)  http://binarybottle.com

Copyright 2015,  Sage Bionetworks (http://sagebase.org), Apache v2.0 License

"""


def convert_audio_file(old_file, file_append, new_file='', command='ffmpeg',
                       input_args='-i', output_args='-ac 2'):
    """
    Convert audio file to new format.

    Parameters
    ----------
    old_file : string
        full path to the input file
    file_append : string
        append to file name to indicate output file format (e.g., '.wav')
    new_file : string
        full path to the output file (optional)
    command : string
        executable command without arguments
    input_args : string
        arguments preceding input file name in command
    output_args : string
        arguments preceding output file name in command

    Returns
    -------
    converted_file : string
        full path to the converted file

    Examples
    --------
    >>> from mhealthx.data_io import convert_audio_file
    >>> old_file = '/Users/arno/mhealthx_working/mHealthX/phonation_files/test.m4a'
    >>> file_append = '.wav'
    >>> new_file = 'test.m4a'
    >>> command = 'ffmpeg'
    >>> input_args = '-i'
    >>> output_args = '-ac 2'
    >>> converted_file = convert_audio_file(old_file, file_append, new_file, command, input_args, output_args)

    """
    import os
    from nipype.interfaces.base import CommandLine

    if not os.path.isfile(old_file):
        raise(IOError(old_file + " not found"))
    else:
        # Don't convert file if file already has correct append:
        if old_file.endswith(file_append):
            converted_file = old_file
        # Convert file to new format:
        else:
            if new_file:
                output_file = new_file + file_append
            else:
                output_file = old_file + file_append
            # Don't convert file if output file already exists:
            if os.path.isfile(output_file):
                converted_file = output_file
            else:
                # Nipype command line wrapper:
                cli = CommandLine(command = command)
                cli.inputs.args = ' '.join([input_args, old_file,
                                            output_args, output_file])
                cli.cmdline
                cli.run()

                if not os.path.isfile(output_file):
                    raise(IOError(output_file + " not found"))
                else:
                    converted_file = output_file

    return converted_file


def arff_to_csv(arff_file, csv_file):
    """
    Convert an arff file to csv format.

    Column headers include lines that start with '@attribute ',
    include 'numeric', and whose intervening string is not exception_string.
    The function raises an error if the number of resulting columns does
    not equal the number of numeric values.

    Example input: arff output from openSMILE's SMILExtract command

    Adapted some formatting from:
    http://biggyani.blogspot.com/2014/08/
    converting-back-and-forth-between-weka.html

    Parameters
    ----------
    arff_file : string
        arff file (full path)
    csv_file : string
        csv file (full path)

    Returns
    -------
    csv_file : string
        csv file (full path)

    Examples
    --------
    >>> from mhealthx.data_io import arff_to_csv
    >>> arff_file = '/Users/arno/csv/test1.csv'
    >>> csv_file = 'test.csv'
    >>> csv_file = arff_to_csv(arff_file, csv_file)

    """
    import os

    # String not included as a header:
    exception_string = 'class'
    # Remove items from the left and right in the '@data' row:
    data_from_left = 1
    data_from_right = 1

    # Check to make sure arff_file exists:
    if type(arff_file) != str or not os.path.isfile(arff_file):
        raise IOError("The arff file {0} does not exist.".format(arff_file))

    # Open arff_file:
    with open(arff_file, 'r') as fid:
        lines = fid.readlines()

    # Loop through lines of the arff file:
    cols = []
    first_numeric = False
    for iline, line in enumerate(lines):
        if '@data' in line:
            break
        else:

            # If line starts with '@attribute ' and contains 'numeric',
            # append intervening string as a column name, and
            # store index as first line of column names:
            if line.startswith('@attribute ') and 'numeric' in line:
                if '{' in line:
                    interstring = line[11:line.index('{') - 1]
                else:
                    interstring = line[11:line.index('numeric') - 1]

                # If intervening string between '@attribute ' and 'numeric'
                # is not the exception_string, include as a column header:
                if interstring != exception_string:
                    cols.append(interstring)
                    if not first_numeric:
                        first_numeric = True

            # Else break if past first line with '@attribute ' and 'numeric':
            elif first_numeric:
                break

    # Remove left and right (first and last) data items:
    data = lines[len(lines)-1].split(',')
    data = data[data_from_left:-data_from_right]

    if len(data) != len(cols):
        raise Exception('The arff file does not conform to expected format.')

    # Write csv file:
    headers = ",".join(cols)
    data_string = ', '.join(data) + '\n'
    if not csv_file:
        csv_file = arff_file + '.csv'
    with open(csv_file, 'w') as fout:
        fout.write(headers)
        fout.write('\n')
        fout.writelines(data_string)

    return csv_file


def concatenate_tables_vertically(tables, output_csv_file=None):
    """
    Vertically concatenate multiple table files or pandas DataFrames or dicts
    with the same column names and store as a csv table.

    Parameters
    ----------
    tables : list of table files or pandas DataFrames or dicts
        each table or dataframe has the same column names
    output_csv_file : string or None
        output table file (full path)

    Returns
    -------
    table_data : Pandas DataFrame
        output table data
    output_csv_file : string or None
        output table file (full path)

    Examples
    --------
    >>> import pandas as pd
    >>> from mhealthx.data_io import concatenate_tables_vertically
    >>> df1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
    >>>                     'B': ['B0', 'B1', 'B2', 'B3'],
    >>>                     'C': ['C0', 'C1', 'C2', 'C3']},
    >>>                    index=[0, 1, 2, 3])
    >>> df2 = pd.DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],
    >>>                     'B': ['B4', 'B5', 'B6', 'B7'],
    >>>                     'C': ['C4', 'C5', 'C6', 'C7']},
    >>>                     index=[0, 1, 2, 3])
    >>> tables = [df1, df2]
    >>> tables = ['/Users/arno/csv/table1.csv', '/Users/arno/csv/table2.csv']
    >>> tables = [{'A':[1,2,3,4],'B':[5,6,7,8],'C':[9,10,11,12]}, {'A':[10,20,30,40],'B':[50,60,70,80],'C':[90,100,110,120]}]
    >>> output_csv_file = None #'./test.csv'
    >>> table_data, output_csv_file = concatenate_tables_vertically(tables, output_csv_file)
    """
    import os
    import pandas as pd

    # Raise an error if tables are not strings or pandas DataFrames or dicts:
    type0 = type(tables[0])
    if type0 not in [str, pd.DataFrame, dict]:
        raise IOError("'tables' should contain strings or pandas DataFrames "
                      "or dictionaries.")

    # pandas DataFrames:
    if type(tables[0]) == pd.DataFrame:
        pass
    # file strings:
    elif type(tables[0]) == str:
        tables_from_files = []
        for table in tables:
            if os.path.isfile(table):
                tables_from_files.append(pd.read_csv(table))
            else:
                raise IOError('{0} is not a file.'.format(table))
        tables = tables_from_files
    # dicts:
    elif type(tables[0]) == dict:
        tables_from_dicts = []
        for table in tables:
            if type(table) == dict:
                tables_from_dicts.append(pd.DataFrame.from_dict(table))
            else:
                raise IOError("'table' doesn't contain all dictionaries.")
        tables = tables_from_dicts

    # Vertically concatenate tables:
    table_data = pd.concat(tables, ignore_index=True)

    # Store as csv file:
    if output_csv_file:
        table_data.to_csv(output_csv_file, index=False)

    return table_data, output_csv_file


def concatenate_tables_horizontally(tables, output_csv_file=None):
    """
    Horizontally concatenate multiple table files or pandas DataFrames or
    dictionaries that have the same number of rows and store as a csv table.

    If any one of the members of the tables list is itself a list,
    call concatenate_tables_vertically() on this list.

    Parameters
    ----------
    tables : list of strings, pandas DataFrames, and/or lists of dicts
        each component table has the same number of rows
    output_csv_file : string or None
        output table file (full path)

    Returns
    -------
    table_data : Pandas DataFrame
        output table data
    output_csv_file : string or None
        output table file (full path)

    Examples
    --------
    >>> import pandas as pd
    >>> from mhealthx.data_io import concatenate_tables_horizontally
    >>> df1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
    >>>                     'B': ['B0', 'B1', 'B2', 'B3'],
    >>>                     'C': ['C0', 'C1', 'C2', 'C3']},
    >>>                    index=[0, 1, 2, 3])
    >>> df2 = pd.DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],
    >>>                     'B': ['B4', 'B5', 'B6', 'B7'],
    >>>                     'C': ['C4', 'C5', 'C6', 'C7']},
    >>>                     index=[0, 1, 2, 3])
    >>> tables1 = [df1, df2]
    >>> tables2 = [{'A':[1,2,3,4],'B':[5,6,7,8],'C':[9,10,11,12]}, {'A':[10,20,30,40],'B':[50,60,70,80],'C':[90,100,110,120]}]
    >>> tables = [tables1, tables2]
    >>> output_csv_file = None #'./test.csv'
    >>> table_data, output_csv_file = concatenate_tables_horizontally(tables, output_csv_file)
    """
    import os
    import pandas as pd

    from mhealthx.data_io import concatenate_tables_vertically as cat_vert

    # Create a list of pandas DataFrames:
    tables_to_combine = []
    for table in tables:
        # pandas DataFrame:
        if type(table) == pd.DataFrame:
            tables_to_combine.append(table)
        # file string:
        elif type(table) == str:
            if os.path.isfile(table):
                table_from_file = pd.DataFrame.from_csv(table)
                tables_to_combine.append(table_from_file)
            else:
                raise IOError('{0} is not a file.'.format(table))
        # list of tables to be vertically concatenated:
        elif type(table) == list:
            out_file = None
            subtable, out_file = cat_vert(table, out_file)
            tables_to_combine.append(subtable)
        else:
            raise IOError("'tables' members are not the right types.")
    tables = tables_to_combine

    # Raise an error if tables are not pandas DataFrames of the same height:
    table0 = tables[0]
    nrows = table0.shape[0]
    for table in tables:
        if table.shape[0] != nrows:
            raise Exception("The tables have different numbers of rows!")

    # Horizontally concatenate tables:
    table_data = pd.concat(tables, ignore_index=True, axis=0)

    # Store as csv file:
    if output_csv_file:
        table_data.to_csv(output_csv_file, index=False)

    return table_data, output_csv_file



# ============================================================================
if __name__ == '__main__':

    pass