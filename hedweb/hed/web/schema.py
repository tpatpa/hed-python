from os.path import basename
import traceback
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from flask import current_app, Response

from hed.schematools import xml2wiki, wiki2xml, constants as converter_constants
from hed.util.hed_dictionary import HedDictionary
from hed.util.file_util import delete_file_if_it_exist, url_to_file, get_file_extension, write_text_iter_to_file
from hed.util.exceptions import SchemaError

from hed.web.web_utils import check_if_option_in_form, file_extension_is_valid, handle_http_error, \
    save_file_to_upload_folder, generate_download_file_response

from hed.web.constants import common_constants, error_constants, file_constants

app_config = current_app.config


def form_has_hed_file(form_request_object, valid_extensions):
    """Checks to see if a HED file is present in a request object from schema form.

    Parameters
    ----------
    form_request_object: Request object
        A Request object containing user data from the schema form.
    valid_extensions: list of str
        List of valid extensions

    Returns
    -------
    boolean
        True if a HED file is present in a request object from the schema form.

    """
    if check_if_option_in_form(form_request_object, common_constants.SCHEMA_UPLOAD_OPTIONS,
                               common_constants.SCHEMA_FILE_OPTION) and \
        common_constants.SCHEMA_FILE in form_request_object.files and \
            file_extension_is_valid(form_request_object.files[common_constants.SCHEMA_FILE].filename, valid_extensions):
        return True
    else:
        return False


def form_has_hed_url(form_request_object, valid_extensions):
    """Checks to see if a HED URL is present in a request object from schema form.

    Parameters
    ----------
    form_request_object: Request object
        A Request object containing user data from the schema form.

    Returns
    -------
    boolean
        True if a HED URL is present in a request object from the schema form.

    """
    if not check_if_option_in_form(form_request_object, common_constants.SCHEMA_UPLOAD_OPTIONS,
                                          common_constants.SCHEMA_URL_OPTION) or \
            common_constants.SCHEMA_URL not in form_request_object.values:
        return False
    parsed_url = urlparse(form_request_object.values.get(common_constants.SCHEMA_URL))
    return file_extension_is_valid(parsed_url.path, valid_extensions)


def generate_input_from_schema_form(form_request_object):
    """Gets the conversion function input arguments from a request object associated with the conversion form.

    Parameters
    ----------
    form_request_object: Request object
        A Request object containing user data from the conversion form.

    Returns
    -------
    dictionary
        A dictionary containing input arguments for calling the underlying schema functions.
    """
    arguments = {}
   
    if form_has_hed_file(form_request_object, file_constants.SCHEMA_EXTENSIONS):
        schema_file = form_request_object.files[common_constants.SCHEMA_FILE]
        arguments[common_constants.SCHEMA_PATH] = save_file_to_upload_folder(schema_file)
        arguments[common_constants.SCHEMA_DISPLAY_NAME] = schema_file.filename
    elif form_has_hed_url(form_request_object):
        schema_url = form_request_object.values[common_constants.SCHEMA_URL]
        arguments[common_constants.SCHEMA_PATH]= url_to_file(schema_url)
        url_parsed = urlparse(schema_url)
        arguments[common_constants.SCHEMA_DISPLAY_NAME] = basename(url_parsed.path)
    return arguments


def get_schema_conversion(schema_local_path):
    """Runs the appropriate xml<>mediawiki converter depending on input filetype.

    returns: A dictionary with converter.constants filled in.
    """

    try:
        if not schema_local_path:
            raise ValueError(f"Invalid input schema path")
        input_extension = get_file_extension(schema_local_path)

        if input_extension == file_constants.SCHEMA_XML_EXTENSION:
            conversion_function = xml2wiki.convert_hed_xml_2_wiki
        elif input_extension == file_constants.SCHEMA_WIKI_EXTENSION:
            conversion_function = wiki2xml.convert_hed_wiki_2_xml
        else:
            raise ValueError(f"Invalid extension type: {input_extension}")
        results = conversion_function(None, schema_local_path)
        converted_schema_path = results.get(converter_constants.HED_OUTPUT_LOCATION_KEY)
        errors = ''
    except ValueError as v:
        errors = v.message
        converted_schema_path = ''

    return converted_schema_path, errors


# def get_uploaded_file_paths_from_schema_form(form_request_object):
#     """Gets the other paths of the uploaded files in the form.
# 
#     Parameters
#     ----------
#     form_request_object: Request object
#         A Request object containing user data from the schema form.
# 
#     Returns
#     -------
#     string
#         The local file path, if exists.
#     """
#     schema_local_path = ''
#     hed_present_in_form = check_if_option_in_form(form_request_object, common_constants.SCHEMA_UPLOAD_OPTIONS,
#                                                   common_constants.SCHEMA_FILE_OPTION) and \
#         common_constants.SCHEMA_FILE in form_request_object.files
#     if hed_present_in_form and file_extension_is_valid(
#             form_request_object.files[common_constants.SCHEMA_FILE].filename, file_constants.SCHEMA_EXTENSIONS):
#         schema_local_path = save_file_to_upload_folder(form_request_object.files[common_constants.SCHEMA_FILE])
#     elif form_has_hed_url(form_request_object):
#         schema_local_path = url_to_file(form_request_object.values[common_constants.SCHEMA_URL])
#     return schema_local_path


def run_schema_conversion(form_request_object):
    """Run conversion(wiki2xml or xml2wiki from converter)

    returns: Response or string.
        Non empty string is an error
        Response is a download success.
    """
    hed_file_path = ''
    try:
        arguments = generate_input_from_schema_form(form_request_object)
        hed_file_path = arguments.get(common_constants.SCHEMA_PATH)
        schema_file, errors = get_schema_conversion(hed_file_path)
        print(schema_file)
        print(hed_file_path)
        if errors:
            download_response = errors
        else:
            download_response = generate_download_file_response(schema_file)
        if isinstance(download_response, Response):
            return download_response
        elif isinstance(download_response, str):
            return handle_http_error(error_constants.NOT_FOUND_ERROR, download_response)
        else:
            raise Exception("Unable to download schema file for unknown reasons")
    except SchemaError as e:
        return e.message
    except HTTPError:
        return error_constants.NO_URL_CONNECTION_ERROR
    except URLError:
        return error_constants.INVALID_URL_ERROR
    except:
        return traceback.format_exc()
    finally:
        delete_file_if_it_exist(hed_file_path)


def run_schema_duplicate_tag_detection(form_request_object):
    """Run tag comparison(map_schema from converter)

    returns: Response or string.
        Empty string is success, but nothing to download.
        Non empty string is an error
        Response is a download success.
    """
    hed_file_path = ''
    try:
        conversion_input_arguments = generate_input_from_schema_form(form_request_object)
        hed_file_path = conversion_input_arguments.get(common_constants.SCHEMA_PATH)
        if hed_file_path.endswith(".mediawiki"):
            new_file_path, errors = get_schema_conversion(hed_file_path)
            if new_file_path:
                delete_file_if_it_exist(hed_file_path)
                hed_file_path = new_file_path

        if not file_extension_is_valid(hed_file_path, [file_constants.SCHEMA_XML_EXTENSION]):
            raise ValueError(f"Invalid extension on file: {hed_file_path}")
        hed_dict = HedDictionary(hed_file_path)
        x = hed_dict.has_duplicate_tags()
        if hed_dict.has_duplicate_tags():
            dup_tag_file = write_text_iter_to_file(hed_dict.dupe_tag_iter(True))
            #download_response = generate_download_file_response_and_delete(dup_tag_file)
            download_response = generate_download_file_response(dup_tag_file, f"Duplicate tags for: {hed_file_path}")
            if isinstance(download_response, str):
                return handle_http_error(error_constants.NOT_FOUND_ERROR, download_response)
            return download_response
    except URLError:
        return error_constants.INVALID_URL_ERROR
    except HTTPError:
        return error_constants.NO_URL_CONNECTION_ERROR
    except SchemaError as e:
        return e.message
    finally:
        delete_file_if_it_exist(hed_file_path)
    return ""


def form_has_hed_url(form_request_object):
    """Checks to see if a HED XML URL is present in a request object from conversion form.

    Parameters
    ----------
    form_request_object: Request object
        A Request object containing user data from the conversion form.

    Returns
    -------
    boolean
        True if a HED XML other is present in a request object from the conversion form.

    """
    url_checked = check_if_option_in_form(form_request_object, common_constants.SCHEMA_UPLOAD_OPTIONS,
                                          common_constants.SCHEMA_URL_OPTION)
    return url_checked and common_constants.SCHEMA_URL in form_request_object.values
