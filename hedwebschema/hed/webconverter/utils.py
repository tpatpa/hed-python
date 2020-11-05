import traceback
import urllib
from flask import Response

from hed.util.file_util import url_to_file, get_file_extension

from hed.webconverter.constants.other import file_extension_constants
from hed.webconverter.constants.error import error_constants
from hed.webconverter.constants.form import conversion_arg_constants, js_form_constants

from hed.schematools import xml2wiki, wiki2xml, constants as converter_constants
from hed.util.errors import SchemaError
from hed.tools import duplicate_tags
from hed.util.file_util import delete_file_if_it_exist
from hed.webconverter.web_utils import handle_http_error, _save_hed_to_upload_folder_if_present, _file_has_valid_extension


def _get_uploaded_file_paths_from_forms(form_request_object):
    """Gets the other paths of the uploaded files in the form.

    Parameters
    ----------
    form_request_object: Request object
        A Request object containing user data from the conversion form.

    Returns
    -------
    string
        The local file path, if exists.
    """
    hed_file_path = ''
    if hed_present_in_form(form_request_object) and _file_has_valid_extension(
            form_request_object.files[js_form_constants.HED_FILE], file_extension_constants.HED_FILE_EXTENSIONS):
        hed_file_path = _save_hed_to_upload_folder_if_present(
            form_request_object.files[js_form_constants.HED_FILE])
    elif url_present_in_form(form_request_object):
        hed_file_path = url_to_file(form_request_object.values[js_form_constants.HED_URL])
    return hed_file_path



def _run_conversion(hed_file_path):
    """Runs the appropriate xml<>mediawiki converter depending on input filetype.

    returns: A dictionary with converter.constants filled in.
    """
    input_extension = get_file_extension(hed_file_path)
    if input_extension == file_extension_constants.HED_XML_EXTENSION:
        conversion_function = xml2wiki.convert_hed_xml_2_wiki
    elif input_extension == file_extension_constants.HED_WIKI_EXTENSION:
        conversion_function = wiki2xml.convert_hed_wiki_2_xml
    else:
        raise ValueError(f"Invalid extension type: {input_extension}")

    return conversion_function(None, hed_file_path)

def _run_tag_compare(local_xml_path):
    """Runs tag compare for the given XML file.

    returns: A dictionary with converter.constants filled in.
    """
    input_extension = get_file_extension(local_xml_path)
    if input_extension != file_extension_constants.HED_XML_EXTENSION:
        raise ValueError(f"Invalid extension type: {input_extension}")

    return duplicate_tags.check_for_duplicate_tags(local_xml_path)


def run_conversion(form_request_object):
    """Run conversion(wiki2xml or xml2wiki from converter)

    returns: Response or string.
        Non empty string is an error
        Response is a download success.
    """
    hed_file_path = ''
    try:
        conversion_input_arguments = _generate_input_arguments_from_conversion_form(form_request_object)
        hed_file_path = conversion_input_arguments[conversion_arg_constants.HED_XML_PATH]
        result_dict = _run_conversion(hed_file_path)
        filename = result_dict[converter_constants.HED_OUTPUT_LOCATION_KEY]
        download_response = generate_download_file_response_and_delete(filename)
        if isinstance(download_response, str):
            return handle_http_error(error_constants.NOT_FOUND_ERROR, download_response)
        return download_response
    except urllib.error.URLError:
        return error_constants.INVALID_URL_ERROR
    except urllib.error.HTTPError:
        return error_constants.NO_URL_CONNECTION_ERROR
    except SchemaError as e:
        return e.message
    except:
        return traceback.format_exc()
    finally:
        delete_file_if_it_exist(hed_file_path)


def run_tag_compare(form_request_object):
    """Run tag comparison(map_schema from converter)

    returns: Response or string.
        Empty string is success, but nothing to download.
        Non empty string is an error
        Response is a download success.
    """
    hed_file_path = ''
    try:
        conversion_input_arguments = _generate_input_arguments_from_conversion_form(form_request_object)
        hed_file_path = conversion_input_arguments[conversion_arg_constants.HED_XML_PATH]
        if hed_file_path.endswith(".mediawiki"):
            new_file_path = _run_conversion(hed_file_path)[converter_constants.HED_OUTPUT_LOCATION_KEY]
            if new_file_path:
                delete_file_if_it_exist(hed_file_path)
                hed_file_path = new_file_path
        result_dict = _run_tag_compare(hed_file_path)
        if result_dict[converter_constants.HED_OUTPUT_LOCATION_KEY]:
            filename = result_dict[converter_constants.HED_OUTPUT_LOCATION_KEY]
            download_response = generate_download_file_response_and_delete(filename)
            if isinstance(download_response, str):
                return handle_http_error(error_constants.NOT_FOUND_ERROR, download_response)
            return download_response
    except urllib.error.URLError:
        return error_constants.INVALID_URL_ERROR
    except urllib.error.HTTPError:
        return error_constants.NO_URL_CONNECTION_ERROR
    except SchemaError as e:
        return e.message
    finally:
        delete_file_if_it_exist(hed_file_path)
    return ""


def generate_download_file_response_and_delete(full_filename, display_filename=None):
    """Generates a download other response.

    Parameters
    ----------
    full_filename: string
        The download other name.
    display_filename: string
        What the save as window should show for filename.  If none use download file name.

    Returns
    -------
    response object or string.
        A response object containing the download, or a string on error.

    """
    if display_filename is None:
        display_filename = full_filename
    try:
        def generate():
            with open(full_filename, 'r', encoding='utf-8') as download_file:
                for line in download_file:
                    yield line
            delete_file_if_it_exist(full_filename)

        return Response(generate(), mimetype='text/plain charset=utf-8',
                        headers={'Content-Disposition': f"attachment; filename={display_filename}"})
    except:
        return traceback.format_exc()


def _generate_input_arguments_from_conversion_form(form_request_object):
    """Gets the conversion function input arguments from a request object associated with the conversion form.

    Parameters
    ----------
    form_request_object: Request object
        A Request object containing user data from the conversion form.

    Returns
    -------
    dictionary
        A dictionary containing input arguments for calling the underlying conversion function.
    """
    conversion_input_arguments = {}
    hed_file_path = _get_uploaded_file_paths_from_forms(form_request_object)
    conversion_input_arguments[conversion_arg_constants.HED_XML_PATH] = hed_file_path
    return conversion_input_arguments


def url_present_in_form(conversion_form_request_object):
    """Checks to see if a HED XML URL is present in a request object from conversion form.

    Parameters
    ----------
    conversion_form_request_object: Request object
        A Request object containing user data from the conversion form.

    Returns
    -------
    boolean
        True if a HED XML other is present in a request object from the conversion form.

    """
    return _check_if_option_in_form(conversion_form_request_object, js_form_constants.OPTIONS_GROUP,
                                    js_form_constants.OPTION_URL) \
                                    and js_form_constants.HED_URL in conversion_form_request_object.values


def _check_if_option_in_form(conversion_form_request_object, option_name, target_value):
    """Checks if the given option has a specific value.
       This is used for radio buttons.
    """
    if option_name in conversion_form_request_object.values:
        if conversion_form_request_object.values[option_name] == target_value:
            return True

    return False


def hed_present_in_form(conversion_form_request_object):
    """Checks to see if a HED XML other is present in a request object from conversion form.

    Parameters
    ----------
    conversion_form_request_object: Request object
        A Request object containing user data from the conversion form.

    Returns
    -------
    boolean
        True if a HED XML other is present in a request object from the conversion form.

    """
    return _check_if_option_in_form(conversion_form_request_object, js_form_constants.OPTIONS_GROUP,
                                    js_form_constants.OPTION_UPLOAD) \
                                    and js_form_constants.HED_FILE in conversion_form_request_object.files


