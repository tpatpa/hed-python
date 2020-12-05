from hed.util.column_mapper import ColumnMapper
from hed.util.base_file_input import BaseFileInput
from hed.util.column_def_group import ColumnDefinitionGroup

class EventFileInput(BaseFileInput):
    """A class to parse bids style spreadsheets into a more general format."""

    def __init__(self, filename, worksheet_name=None, tag_columns=None,
                 has_column_names=True, column_prefix_dictionary=None,
                 json_def_files=None, attribute_columns=None,
                 hed_dictionary=None):
        """Constructor for the EventFileInput class.

         Parameters
         ----------
         filename: str
             An xml/tsv file to open.
         worksheet_name: str
             The name of the Excel workbook worksheet that contains the HED tags.  Not applicable to tsv files.
         tag_columns: list
             A list of ints containing the columns that contain the HED tags. The default value is the 2nd column.
         has_column_names: bool
             True if file has column names. The validation will skip over the first line of the file. False, if
             otherwise.
         column_prefix_dictionary: dict
             A dictionary with keys pertaining to the required HED tag columns that correspond to tags that need to be
             prefixed with a parent tag path. For example, prefixed_needed_tag_columns = {3: 'Event/Description',
             4: 'Event/Label/', 5: 'Event/Category/'} The third column contains tags that need Event/Description/ prepended to them,
             the fourth column contains tags that need Event/Label/ prepended to them, and the fifth column contains tags
             that needs Event/Category/ prepended to them.
         json_def_files : str or [str] or ColumnDefinitionGroup or [ColumnDefinitionGroup]
             A list of json filenames to pull events from
         attribute_columns: str or int or [str] or [int]
             A list of column names or numbers to treat as attributes.
             Default: ["duration", "onset"]
         """
        if tag_columns is None:
            tag_columns = []
        if column_prefix_dictionary is None:
            column_prefix_dictionary = {}
        if attribute_columns is None:
            attribute_columns = ["duration", "onset"]

        column_group_defs = ColumnDefinitionGroup.load_multiple_json_files(json_def_files)

        new_mapper = ColumnMapper(json_def_files=column_group_defs, tag_columns=tag_columns, column_prefix_dictionary=column_prefix_dictionary,
                                  hed_dictionary=hed_dictionary, attribute_columns=attribute_columns)

        super().__init__(filename, worksheet_name, has_column_names, new_mapper)

        if not self._has_column_names:
            raise ValueError("You are attempting to open a bids style file with no column headers provided.\n"
                             "This is probably not intended.")


if __name__ == '__main__':
    from hed.util.hed_dictionary import HedDictionary
    local_hed_xml = "examples/data/HED7.1.1.xml"
    hed_dictionary = HedDictionary(local_hed_xml)
    event_file = EventFileInput("examples/data/basic_events_test.tsv",
                                json_def_files="examples/data/both_types_events_errors.json", attribute_columns=["onset"],
                                hed_dictionary=hed_dictionary)

    for stuff in event_file:
        print(stuff)
