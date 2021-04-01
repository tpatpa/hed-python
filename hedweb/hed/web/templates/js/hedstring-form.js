
$(function () {
    prepareForm();
});

/**
 * Submits the form for tag comparison if we have a valid file.
 */
$('#hedstring-submit').on('click', function () {
   if (!hedStringIsSpecified()) {
        flashMessageOnScreen('Must give a non-empty hedstring.  See above.', 'error',
            'hedstring-submit-flash')
    } else {
        submitHedStringForm();
    }
});

/*$('#hedstring-validate').on('change', function () {
    updateFormGui();
});

$('#schema-url-option').on('change',function () {
    updateFormGui();
});*/

/**
 * Checks to see if a hedstring has been specified.
 */
function hedStringIsSpecified() {
/*    let jsonFile = $('#json-file');
    if (jsonFile[0].files.length === 0) {
        flashMessageOnScreen('JSON is not specified.', 'error', 'json-flash');
        return false;
    }*/
    return true;
}


/**
 * Prepare the validation form after the page is ready. The form will be reset to handle page refresh and
 * components will be hidden and populated.
 */
function prepareForm() {
    resetForm();
    getHEDVersions()
    hideOtherHEDVersionFileUpload()
}

/**
 * Resets the fields in the form.
 */
function resetForm() {
    $('#hedstring-form')[0].reset();
    resetFormFlashMessages();
    hideOtherHEDVersionFileUpload()
}


/**
 * Resets the flash messages that aren't related to the form submission.
 */
function resetFormFlashMessages() {
    clearHEDFlashMessage();
    flashMessageOnScreen('', 'success', 'hedstring-flash');
    flashMessageOnScreen('', 'success', 'hedstring-submit-flash');
}



/**
 * Submit the form and return the validation results. If there are issues then they are returned in an attachment
 * file.
 */
function submitHedStringForm() {
    let stringForm = document.getElementById("hedstring-form");
    let formData = new FormData(stringForm);

    //let dictionaryFile = getJsonFileLabel();
    //let display_name = convertToResultsName(dictionaryFile, 'issues')
    resetFormFlashMessages();
    flashMessageOnScreen('HED string is being processed ...', 'success', 'hedstring-submit-flash')
    $.ajax({
            type: 'POST',
            url: "{{url_for('route_blueprint.get_hedstring_results')}}",
            data: formData,
            contentType: false,
            processData: false,
            dataType: 'json',
            success: function (hedInfo) {
                resetFormFlashMessages();
                if (hedInfo['hedstring-result']) {
                    $('#hedstring-result').val(hedInfo['hedstring-result'])
                    flashMessageOnScreen('Processing completed', 'success', 'hedstring-submit-flash')
                } else if (hedInfo['message'])
                    flashMessageOnScreen(hedInfo['message'], 'error', 'hedstring-submit-flash')
                else {
                    flashMessageOnScreen('Server could not respond to this request', 'error', 'hedstring-submit-flash')
                }
            },
            error: function (jqXHR) {
                console.log(jqXHR.responseJSON.message);
                flashMessageOnScreen(jqXHR.responseJSON.message, 'error', 'hedstring-submit-flash')
            }
        }
    )
}

function submitHedStringFormNew() {
    let stringForm = document.getElementById("hedstring-form");
    let formData = new FormData(stringForm);

    //let dictionaryFile = getJsonFileLabel();
    //let display_name = convertToResultsName(dictionaryFile, 'issues')
    resetFormFlashMessages();
    flashMessageOnScreen('HED string is being processed ...', 'success', 'hedstring-submit-flash')
    $.ajax({
            type: 'POST',
            url: "{{url_for('route_blueprint.get_hedstring_results')}}",
            data: formData,
            contentType: false,
            processData: false,
            dataType: 'json',
            success: function (hedInfo) {
                resetFormFlashMessages();
                if (hedInfo['hedstring-result']) {
                    $('#hedstring-result').val(hedInfo['hedstring-result'])
                    flashMessageOnScreen('Processing completed', 'success', 'hedstring-submit-flash')
                } else if (hedInfo['message'])
                    flashMessageOnScreen(hedInfo['message'], 'error', 'hedstring-submit-flash')
                else {
                    flashMessageOnScreen('Server could not respond to this request', 'error', 'hedstring-submit-flash')
                }
            },
            error: function (jqXHR) {
                console.log(jqXHR.responseJSON.message);
                flashMessageOnScreen(jqXHR.responseJSON.message, 'error', 'hedstring-submit-flash')
            }
        }
    )
}


function updateFormGui() {
     let filename = getSchemaFilename();
     let isXMLFilename = fileHasValidExtension(filename, [SCHEMA_XML_EXTENSION]);
     let isMediawikiFilename = fileHasValidExtension(filename, [SCHEMA_MEDIAWIKI_EXTENSION]);

     let hasValidFilename = false;
     if (isXMLFilename) {
        $('#schema-conversion-submit').html("Convert to mediawiki")
        hasValidFilename = true;
     } else if (isMediawikiFilename) {
        $('#schema-conversion-submit').html("Convert to XML");
        hasValidFilename = true;
     } else {
        $('#schema-conversion-submit').html("Convert Format");
     }

     let urlChecked = document.getElementById("schema-url-option").checked;
     if (!urlChecked || hasValidFilename) {
        flashMessageOnScreen("", 'success', 'schema-url-flash')
     }
     let uploadChecked = document.getElementById("schema-file-option").checked;
     if (!uploadChecked || hasValidFilename) {
        flashMessageOnScreen("", 'success', 'schema-file-flash')
     }

     if (filename && urlChecked && !hasValidFilename) {
        flashMessageOnScreen('Please choose a valid schema url (.xml, .mediawiki)', 'error',
        'schema-url-flash');
     }

     if (filename && uploadChecked && !hasValidFilename) {
         flashMessageOnScreen('Please upload a valid schema file (.xml, .mediawiki)', 'error',
        'schema-file-flash');
     }

     if (!uploadChecked && !urlChecked) {
        flashMessageOnScreen('No source file specified.', 'error', 'schema-file-flash');
     }

     flashMessageOnScreen('', 'success', 'schema-submit-flash')
}
