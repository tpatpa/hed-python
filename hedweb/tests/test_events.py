import unittest
# from flask import current_app, jsonify, Response
# from hed.web.utils import app_config
# from hed.web.validation import generate_dictionary_validation_filename
# from hed.web.app_factory import AppFactory
# from hed.web.constants import file_constants, spreadsheet_constants
import os

# app = AppFactory.create_app('config.TestConfig')
# with app.app_context():
#     from hed.web import web_utils
#     from hed.web.routes import route_blueprint
#
#     app.register_blueprint(route_blueprint, url_prefix=app.config['URL_PREFIX'])
#     web_utils.create_upload_directory(app.config['UPLOAD_FOLDER'])


class Test(unittest.TestCase):
    def setUp(self):
        print("Stuff")
        # self.create_test_app()
        # self.app = app.app.test_client()
        # self.major_version_key = 'major_versions'
        # self.hed_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED.xml')
        # self.tsv_file1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/tsv_file1.txt')

    # def create_test_app(self):
    #     app = AppFactory.create_app('config.TestConfig')
    #     with app.app_context():
    #         from hed.web.routes import route_blueprint
    #         app.register_blueprint(route_blueprint)
    #         self.app = app.test_client()

    def test_generate_input_from_events_form(self):
        self.assertTrue(1, "Testing generate_input_from_events_form")

    def test_report_events_validation_status(self):
        self.assertTrue(1, "report_events_validation_status")


if __name__ == '__main__':
    unittest.main()