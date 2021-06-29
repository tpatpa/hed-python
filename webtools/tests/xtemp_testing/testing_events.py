import os
from hed.models import EventsInput
from hed.schema.hed_schema_file import load_schema
from hed.validator.event_validator import EventValidator
from hed.models import ColumnDefGroup
from hed.errors.error_reporter import get_printable_issue_string

if __name__ == '__main__':
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/HED8.0.0-alpha.1.xml')
    local_hed_file = '../data/HED8.0.0-alpha.1.xml'
    example_data_path = '../data'  # path to example data
    events_path= os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events.tsv')

    hed_schema = load_schema(schema_path)
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/bids_events.json")
    column_group = ColumnDefGroup(json_path)
    def_dict, def_issues = column_group.extract_defs()
    if def_issues:
        print(get_printable_issue_string(def_issues,
                                         title="There should be no errors in the definitions from the sidecars:"))
    input_file = EventsInput(filename=events_path, json_def_files=column_group)

    validation_issues = input_file.validate_file_sidecars(hed_schema=hed_schema)
    if validation_issues:
        print(get_printable_issue_string(validation_issues,
                                         title="There should be no errors with the sidecar.  \""
                                         "This will likely cause other errors if there are."))
    validator = EventValidator(hed_schema=hed_schema)
    validation_issues = validator.validate_input(input_file)
    print(get_printable_issue_string(validation_issues, "Normal hed string errors"))

    events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/bids_events.tsv')
    with open(events_path, "r") as myfile:
        events_string = myfile.read()
    input_file = EventsInput(csv_string=events_string)
    # input_file = EventFileInput(data_as_csv_string=events_string)