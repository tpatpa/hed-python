from hed.util.column_mapper import ColumnMapper
from hed.util.base_file_input import BaseFileInput
from hed.util.column_def_group import ColumnDefGroup
from hed.util.def_mapper import DefinitionMapper
from hed.util import error_reporter


class EventFileInput(BaseFileInput):
    """A class to parse bids style spreadsheets into a more general format."""

    def __init__(self, filename=None, worksheet_name=None, tag_columns=None,
                 has_column_names=True, column_prefix_dictionary=None,
                 json_def_files=None, attribute_columns=None,
                 def_dicts=None, csv_string=None):
        """Constructor for the EventFileInput class.

        Parameters
        ----------
        filename: str or None
            An xml/tsv file to open.
        worksheet_name: str
            The name of the Excel workbook worksheet that contains the HED tags.  Not applicable to tsv files.
        tag_columns: []
            A list of ints containing the columns that contain the HED tags. The default value is the 2nd column.
        has_column_names: bool
            True if file has column names. The validation will skip over the first line of the file. False, if
            otherwise.
        column_prefix_dictionary: {}
            A dictionary with keys pertaining to the required HED tag columns that correspond to tags that need to be
            prefixed with a parent tag path. For example, prefixed_needed_tag_columns = {3: 'Event/Description',
            4: 'Event/Label/', 5: 'Event/Category/'} The third column contains tags that need Event/Description/
            prepended to them, the fourth column contains tags that need Event/Label/ prepended to them,
            and the fifth column contains tags that needs Event/Category/ prepended to them.
        json_def_files : str or [str] or ColumnDefGroup or [ColumnDefGroup]
            A list of json filenames to pull events from
        attribute_columns: str or int or [str] or [int]
            A list of column names or numbers to treat as attributes.
            Default: ["duration", "onset"]
        def_dicts: [DefDict]
            DefDict's containing all the definitions this file should use - other than the ones coming from the file
            itself.
            If this is NOT passed, the class will instead gather definitions from any passed in ColumnDefGroups
        csv_string: str or None
            The data to treat as this file.  eg web services passing a string.
        """
        if tag_columns is None:
            tag_columns = []
        if column_prefix_dictionary is None:
            column_prefix_dictionary = {}
        if attribute_columns is None:
            attribute_columns = ["duration", "onset"]

        # This stuff is mostly here to make this easier to use for development
        # you should generally create the DefDict and ColumnDefGroup before reaching this point.
        if json_def_files:
            self.column_group_defs = ColumnDefGroup.load_multiple_json_files(json_def_files)
        else:
            self.column_group_defs = None
        if def_dicts is None:
            self.def_dicts = ColumnDefGroup.extract_defs_from_list(self.column_group_defs)
        else:
            if not isinstance(def_dicts, list):
                self.def_dicts = [def_dicts]
            else:
                self.def_dicts = def_dicts

        def_mapper = DefinitionMapper(self.def_dicts)
        new_mapper = ColumnMapper(json_def_files=self.column_group_defs, tag_columns=tag_columns,
                                  column_prefix_dictionary=column_prefix_dictionary,
                                  attribute_columns=attribute_columns,
                                  definition_mapper=def_mapper)

        super().__init__(filename, worksheet_name, has_column_names, new_mapper,
                                  csv_string=csv_string)

        if not self._has_column_names:
            raise ValueError("You are attempting to open a bids style file with no column headers provided.\n"
                             "This is probably not intended.")

    def validate_file_sidecars(self, hed_schema=None, error_handler=None):
        """
        Validates all column definitions and column definition hed strings.

        This is not an encouraged way to do this.  You should instead validate the sidecars BEFORE creating
        an EventFileInput
        Parameters
        ----------
        hed_schema : HedSchema, optional
            Also semantically validates hed strings if present.
        error_handler : ErrorHandler or None
            Used to report errors.  Uses a default one if none passed in.
        Returns
        -------
        validation_issues : [{}]
            A list of syntax and semantic issues found in the definitions.
        """
        if error_handler is None:
            error_handler = error_reporter.ErrorHandler()
        all_validation_issues = []
        for column_def_group in self.column_group_defs:
            all_validation_issues += column_def_group.validate_entries(hed_schema=hed_schema,
                                                                       error_handler=error_handler)

        return all_validation_issues
