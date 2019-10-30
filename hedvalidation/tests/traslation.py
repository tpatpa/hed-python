import random;
import unittest;

from hedvalidation.hedvalidation.hed_string_delimiter import HedStringDelimiter;
from hedvalidation.hedvalidation.hed_input_reader import HedInputReader;
from hedvalidation.hedvalidation.error_reporter import report_error_type;


class Tests(unittest.TestCase):
    def setUpClass(cls):
        cls.generic_hed_input_reader = HedInputReader('Attribute/onset')

    def validate(self, test_strings, expected_results, expected_issues):
        for test in test_strings:
            hed_tag_string = expected_results[test]
            target_result = expected_issues[test]

            validation_issues = self.generic_hed_input_reader._validate_hed_string(hed_tag_string)

            has_no_issues = (validation_issues == "")
            print(test + " " + str(has_no_issues == target_result))


    def test_mismatched_parentheses(self):
        testStrings =   {
            'extraOpening': \
                '/Action/Reach/To touch,((/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px',
            'extraClosing': \
                '/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px',
            'valid': \
                '/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px'
        }
        expectedResults = {
            'extraOpening': False,
            'extraClose': False,
            'valid': True
        }
        expectedIssues = {
            #I think this is right
            'extraOpening': [report_error_type('parentheses', tag=testStrings['extraOpening'], open_bracket_count=2, closing_bracket_count=1)],
            'extraClosing': [report_error_type('parentheses', tag=testStrings['extraClosing'], open_bracket_count=1, closing_bracket_count=2)]
        }

        self.validate(testStrings, expectedResults, expectedIssues)

    if __name__ == '__main__':
        unittest.main()

    # def malformed_delimiters(self):
    #     testStrings = {
    #         'missingOpeningComma' : \
    #             '/Action/Reach/To touch(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px',
    #         'missingCLosingComma' : \
    #             '/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm)/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px',
    #         'extraOpeningComma' : \
    #             ',/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px',
    #         'extraClosingComma' : \
    #             '/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px,',
    #         'extraOpeningTilde' : \
    #             '~/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px',
    #         'extraClosingTilde' : \
    #             '/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px~',
    #         'multipleExtraOpeningDelimiters' : \
    #             ',~,/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px',
    #         'multipleExtraClosingDelimiters' : \
    #             '/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px,~~,',
    #         'multipleExtraMiddleDelimiters' : \
    #             '/Action/Reach/To touch,,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,~,/Attribute/Location/Screen/Left/23 px',
    #         'valid' : \
    #             '/Action/Reach/To touch,(/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px',
    #         'validNestedParentheses' : \
    #             '/Action/Reach/To touch,((/Attribute/Object side/Left,/Participant/Effect/Body part/Arm),/Attribute/Location/Screen/Top/70 px,/Attribute/Location/Screen/Left/23 px),Event/Duration/3 ms',
    #     }
    #
    #     expectedResults = {
    #         'missingOpeningComma' : False,
    #         'missingClosingComma' : False,
    #         'extraOpeningComma' : False,
    #         'extraClosingComma' : False,
    #         'extraOpeningTilde' : False,
    #         'extraClosingTilde' : False,
    #         'multipleExtraOpeningDelimiters' : False,
    #         'multipleExtraClosingDelimiters' : False,
    #         'multipleExtraMiddleDelimiters' : False,
    #         'valid' : True,
    #         'validNestedParentheses' : True
    #     }
    #     expectedIssues = {
    #         #NOT COMPLETE
    #         'missingOpeningComma' : [error_reporter.report_error_type('commaValid', tag='/Action/Reach/To touch(')],
    #         'missingClosingComma': [error_reporter.report_error_type('comma', tag='/Participant/Effect/Body part/Arm)/')],
    #         'extraOpeningComma': [error_reporter.report_error_type()],
    #         'extraClosingComma': [error_reporter.report_error_type()],
    #         'extraOpeningTilde': [error_reporter.report_error_type()],
    #         'extraClosingTilde': [error_reporter.report_error_type()],
    #         'multipleExtraOpeningDelimiters': [error_reporter.report_error_type()],
    #         'multipleExtraClosingDelimiters': [error_reporter.report_error_type()],
    #         'multipleExtraMiddleDelimiters': [error_reporter.report_error_type()],
    #         'valid': [],
    #         'validNestedParentheses': []
    #     }
    #
    #     validator(testStrings, expectedResults, expectedIssues)
    #
    # def invalid_characters(self):
    #     testStrings = {
    #         'openingBrace' : \
    #             '/Attribute/Object side/Left,/Participant/Effect{/Body part/Arm',
    #         'closingBrace' : \
    #             '/Attribute/Object side/Left,/Participant/Effect}/Body part/Arm',
    #         'openingBracket' : \
    #             '/Attribute/Object side/Left,/Participant/Effect[/Body part/Arm',
    #         'closingBracket' : \
    #             '/Attribute/Object side/Left,/Participant/Effect]/Body part/Arm'
    #     }
    #     expectedResults = {
    #         'openingBrace' : False,
    #         'closingBrace' : False,
    #         'openingBracket' : False,
    #         'closingBracket' : False
    #     }
    #     expectedIssues = {
    #         #NOT COMPLETE
    #         'openingBrace' : [error_reporter.report_error_type()],
    #         'closingBrace' : [error_reporter.report_error_type()],
    #         'openingBracket' : [error_reporter.report_error_type()],
    #         'closingBracket' : [error_reporter.report_error_type()]
    #     }
    #     validator(testStrings, expectedResults, expectedIssues)
    #
    # def exist_in_schema(self):
    #     testString = {
    #         'takesValue' : 'Event/Duration/3 ms',
    #         'full' : 'Attribute/Object side/Left',
    #         'extensionsAllowed' : 'Item/Object/Person/Driver',
    #         'leafExtension' : 'Action/Hum/Song',
    #         'nonExtensionsAllowed' : 'Item/Nonsense',
    #         'illegalComma' : 'Event/Label/This is a label,This/Is/A/Tag'
    #     }
    #     expectedResults = {
    #         'takesValue': True,
    #         'full': True,
    #         'extensionsAllowed': True,
    #         'leafExtension': False,
    #         'nonExtensionsAllowed': False,
    #         'illegalComma': False
    #     }
    #     expectedIssues = {
    #         #NOT COMPLETE
    #         'takesValue': [],
    #         'full': [],
    #         'extensionsAllowed': [],
    #         'leafExtension': [error_reporter.report_error_type()],
    #         'nonExtensionsAllowed': [error_reporter.report_error_type()],
    #         'illegalComma': [error_reporter.report_error_type()]
    #     }
    #     validator(testString,expectedResults,expectedIssues)
    #
    # def prper_capitalization(self):
    #     testString = {
    #         'proper' : 'Event/Category/Experimental stimulus',
    #         'camelCase' : 'DoubleEvent/Something',
    #         'takesValue' : 'Attribute/Temporal rate/20 Hz',
    #         'numeric' : 'Attribute/Repetition/20',
    #         'lowercase' : 'Event/something'
    #     }
    #     expectedResults = {
    #         'proper': True,
    #         'camelCase': True,
    #         'takesValue': True,
    #         'numeric': True,
    #         'lowercase': False
    #     }
    #     expectedIssues = {
    #         #NOT COMPLETE
    #         'proper': [],
    #         'camelCase': [],
    #         'takesValue': [],
    #         'numeric': [],
    #         'lowercase': [error_reporter.report_error_type()]
    #     }
    #     validator(testString, expectedResults, expectedIssues)
    #
    # def child_required(self):
    #     testString = {
    #         'hasChild' : 'Event/Category/Experimental stimulus',
    #         'missingChild' : 'Event/Category'
    #     }
    #     expectedResults = {
    #         'hasChild' : True,
    #         'missingChild' : False
    #     }
    #     expectedIssues = {
    #         #NOT COMPLETE
    #         'hasChild' : [],
    #         'missingChild' : [error_reporter.report_error_type()]
    #     }
    #     validator(testString,expectedResults, expectedIssues)
    #
    # def required_units(self):
    #     testString = {
    #         'hasRequiredUnit' : 'Event/Duration/3 ms',
    #         'missingRequiredUnit' : 'Event/Duration/3',
    #         'notRequiredNumber' : 'Attribute/Color/Red/0.5',
    #         'notRequiredScientific' : 'Attribute/Color/Red/5.2e-1',
    #         'timeValue' : 'Item/2D shape/Clock face/8:30'
    #     }
    #     expectedResults = {
    #         'hasRequiredUnit': True,
    #         'missingRequiredUnit': False,
    #         'notRequiredNumber': True,
    #         'notRequiredScientific': True,
    #         'timeValue': True
    #     }
    #     expectedIssues = {
    #         #NOT COMPLETE
    #         'hasRequiredUnit': [],
    #         'missingRequiredUnit': [error_reporter.report_error_type()],
    #         'notRequiredNumber': [],
    #         'notRequiredScientific': [],
    #         'timeValue': []
    #     }
    #     validator(testString, expectedResults, expectedIssues)
    #
    # def correct_units(self):
    #     testString = {
    #         'correctUnit' : 'Event/Duration/3 ms',
    #         'correctUnitScientific' : 'Event/Duration/3.5e1 ms',
    #         'incorrectUnit' : 'Event/Duration/3 cm',
    #         'notRequiredNumber' : 'Attribute/Color/Red/0.5',
    #         'notRequiredScientific' : 'Attribute/Color/Red/5e-1',
    #         'properTime' : 'Item/2D shape/Clock face/8:30',
    #         'invalidTime' : 'Item/2D shape/Clock face/54:54'
    #     }
    #     expectedResults = {
    #         'correctUnit': True,
    #         'correctUnitScientific': True,
    #         'incorrectUnit': False,
    #         'notRequiredNumber': True,
    #         'notRequiredScientific': True,
    #         'properTime': True,
    #         'invalidTime': False
    #     }
    #     legalTimeUnits = [
    #         's',
    #         'second',
    #         'seconds',
    #         'centiseconds',
    #         'centisecond',
    #         'cs',
    #         'hour:min',
    #         'day',
    #         'days',
    #         'ms',
    #         'milliseconds',
    #         'millisecond',
    #         'minute',
    #         'minutes',
    #         'hour',
    #         'hours',
    #         ]
    #     expectedIssues = {
    #         #NOT COMPLETE
    #         'correctUnit': [],
    #         'correctUnitScientific': [],
    #         'incorrectUnit': [error_reporter.report_error_type()],
    #         'notRequiredNumber': [],
    #         'notRequiredScientific': [],
    #         'properTime': [],
    #         'invalidTime': [error_reporter.report_error_type()]
    #     }
    #     validator(testString, expectedResults, expectedIssues)
    # def no_duplicates(self):