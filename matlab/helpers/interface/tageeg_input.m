% GUI for input needed to create inputs for tageeg
%
% Usage:
%
%   >>  [baseMap, canceled, editXML, preservePrefix, selectFields, ...
%       useGUI] = tageeg_input()
%
%
% Output:
%
%   baseMap          A fieldMap object or the name of a file that contains
%                    a fieldMap object to be used to initialize tag
%                    information.
%
%   canceled
%                    True if the cancel button is pressed. False if
%                    otherwise.
%
%   extensionsAllowed
%                    If true (default), the HED can be extended. If
%                    false, the HED can not be extended. The 
%                    'ExtensionAnywhere argument determines where the HED
%                    can be extended if extension are allowed.
%                  
%
%   extensionsAnywhere
%                    If true, the HED can be extended underneath all tags.
%                    If false (default), the HED can only be extended where
%                    allowed. These are tags with the 'extensionAllowed'
%                    attribute or leaf tags (tags that do not have
%                    children).
%
%   preservePrefix
%                    If false (default), tags for the same field value that
%                    share prefixes are combined and only the most specific
%                    is retained (e.g., /a/b/c and /a/b become just
%                    /a/b/c). If true, then all unique tags are retained.
%
%   selectFields
%                    If true (default), the user is presented with a
%                    GUI that allow users to select which fields to tag.
%
%   useGUI
%                    If true (default), the CTAGGER GUI is displayed after
%                    initialization.
%
% Copyright (C) 2012-2016 Thomas Rognon tcrognon@gmail.com,
% Jeremy Cockfield jeremy.cockfield@gmail.com, and
% Kay Robbins kay.robbins@utsa.edu
%
% This program is free software; you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation; either version 2 of the License, or
% (at your option) any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program; if not, write to the Free Software
% Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

function [baseMap, canceled, extensionsAllowed, extensionsAnywhere, ...
    preservePrefix, selectFields, useGUI] = tageeg_input()
baseMap = '';
canceled = true;
extensionsAllowed = true;
extensionsAnywhere = false;
preservePrefix = false;
selectFields = true;
useGUI = true;
title = 'Inputs for tagging an EEG structure';
inputFig = figure( ...
    'Color', [.94 .94 .94], ...
    'MenuBar', 'none', ...
    'Name', title, ...
    'NextPlot', 'add', ...
    'NumberTitle','off', ...
    'Resize', 'on', ...
    'Tag', title, ...
    'Toolbar', 'none', ...
    'Visible', 'off', ...
    'WindowStyle', 'modal');
createLayout();
movegui(inputFig); % Make sure it is visible
drawnow
uiwait(inputFig);
if ishandle(inputFig)
    close(inputFig);
end

    function browseBaseTagsCallback(~, ~)
        % Callback for 'Browse' button that sets the 'Base tags' editbox
        [file, path] = uigetfile({'*.mat', 'MATLAB Files (*.mat)'}, ...
            'Browse for event tags');
        tagsFile = fullfile(path, file);
        if ischar(file) && ~isempty(file) && validateBaseTags(tagsFile)
            baseMap = tagsFile;
            set(findobj('Tag', 'BaseTags'), 'String', baseMap);
        end
    end % browseBaseTagsCallback

    function cancelCallback(~, ~)
        % Callback for 'Cancel' button
        baseMap = '';
        canceled = true;
        preservePrefix = false;
        selectFields = true;
        useGUI = true;
        close(inputFig);
    end % browseTagsCallback

    function createBrowsePanel()
        % Creates top panel used for browsing for files
        browsePanel = uipanel('BorderType','none', ...
            'BackgroundColor',[.94 .94 .94],...
            'FontSize',12,...
            'Position',[0 .7 1 .3]);
        uicontrol('Parent', browsePanel, ...
            'Style','text', 'String', 'Import tags', ...
            'Units','normalized',...
            'HorizontalAlignment', 'Left', ...
            'Position', [0.015 0.8 0.13 0.13]);
        uicontrol('Parent', browsePanel, 'style', 'edit', ...
            'BackgroundColor', 'w', 'HorizontalAlignment', 'Left', ...
            'Tag', 'BaseTags', 'String', '', ...
            'TooltipString', ...
            'Complete path for loading the consolidated event tags', ...
            'Units','normalized',...
            'Callback', @baseTagsCtrlCallback, ...
            'Position', [0.15 0.7 0.6 0.25]);
        uicontrol('Parent', browsePanel, ...
            'string', 'Browse', 'style', 'pushbutton', ...
            'TooltipString', 'Press to choose import event tag file', ...
            'Units','normalized',...
            'Callback', @browseBaseTagsCallback, ...
            'Position', [0.775 0.7 0.21 0.25]);
    end % createBrowsePanel

    function createButtonPanel()
        % Create the button panel at the bottom of the GUI
        rewriteGroupPanel = uipanel('BorderType','none', ...
            'BackgroundColor',[.94 .94 .94],...
            'FontSize',12,...
            'Position',[0.6 0 .4 .2]);
        uicontrol('Parent', rewriteGroupPanel, ...
            'Style', 'pushbutton', 'Tag', 'OkayButton', ...
            'String', 'Okay', 'Enable', 'on', 'Tooltip', ...
            'Continue', ...
            'Units','normalized', ...
            'Callback', @okayCallback, ...
            'Position',[0.025 0.3 0.45 0.4]);
        uicontrol('Parent', rewriteGroupPanel, ...
            'Style', 'pushbutton', 'Tag', 'CancelButton', ...
            'String', 'Cancel', 'Enable', 'on', 'Tooltip', ...
            'Cancel', ...
            'Units','normalized', ...
            'Callback', @cancelCallback, ...
            'Position',[0.515 0.3 0.45 0.4]);
    end % createButtonPanel

    function createLayout()
        % Creates the GUI layout
        createBrowsePanel();
        createExtensionPanel();
        createOptionsGroupPanel();
        createButtonPanel();
    end % createLayout

    function createExtensionPanel()
        % Create the panel for extension options
        bg = uibuttongroup('Title', 'HED extension options', ...
            'Position', [0.15 .5 .6 .3],...
            'FontSize',12, ...
            'SelectionChangeFcn', @extensionsCallback);
        uicontrol(bg,'Style',...
            'radiobutton',...
            'Units','normalized', ...
            'Tag', 'WhereAllowed', ...
            'String','Only where allowed',...
            'Position',[0.15 0.66 0.8 0.33],...
            'HandleVisibility','off');
        uicontrol(bg,'Style','radiobutton',...
            'Units','normalized', ...
            'Tag','Anywhere',...
            'String','Anywhere',...
            'Position',[0.15 0.33 0.8 0.33],...
            'HandleVisibility','off');     
        uicontrol(bg,'Style','radiobutton',...
            'Units','normalized', ...
            'Tag','Nowhere',...
            'String','Nowhere',...
            'Position',[0.15 0 0.8 0.33],...
            'HandleVisibility','off');
    end % createExtensionPanel

    function extensionsCallback(src, ~)
        % Callback for 'HED extension options' radio button group
        if strcmp('WhereAllowed', src.SelectedObject.Tag)
            extensionsAllowed = true;
            extensionsAnywhere = false;
        elseif strcmp('Anywhere', src.SelectedObject.Tag)
            extensionsAllowed = true;
            extensionsAnywhere = true;
        else
            extensionsAllowed = false;
            extensionsAnywhere = false;
        end
    end % extensionsCallback

    function createOptionsGroupPanel()
        % Create the panel for additional options
        optionGroupPanel = uipanel('BackgroundColor',[.94,.94,.94],...
            'FontSize',12,...
            'Title','Additional options', ...
            'Position',[0.15 .2 .6 .3]);
        uicontrol('Parent', optionGroupPanel, ...
            'Style', 'CheckBox', 'Tag', 'UseGUICB', ...
            'String', 'Use CTagger', 'Enable', 'on', 'Tooltip', ...
            'If checked, use CTagger for each selected field', ...
            'Units','normalized', ...
            'Value', 1, ...
            'Callback', @useCTaggerCallback, ...
            'Position', [0.15 0.66 0.8 0.33]);
        uicontrol('Parent', optionGroupPanel, ...
            'Style', 'CheckBox', 'Tag', 'SelectFieldsCB', ...
            'String', 'Choose fields to tag', 'Enable', 'on', 'Tooltip', ...
            'If checked, use menu to choose fields to tag', ...
            'Units','normalized', ...
            'Value', 1, ...
            'Callback', @selectFieldsCallback, ...
            'Position', [0.15 0.33 0.8 0.33]);
        uicontrol('Parent', optionGroupPanel, ...
            'Style', 'CheckBox', 'Tag', 'PreservePrefixCB', ...
            'String', 'Preserve tag prefixes', 'Enable', 'on', 'Tooltip', ...
            'If checked, do not consolidate tags that share prefixes', ...
            'Units','normalized', ...
            'Value', 0, ...
            'Callback', @preservePrefixCallback, ...
            'Position', [0.15 0 0.8 0.33]);
    end % createOptionsGroupPanel

    function okayCallback(~, ~)
        % Callback for 'Okay' button
        canceled = false;
        close(inputFig);
    end % okayCallback

    function preservePrefixCallback(src, ~)
        % Callback for user directly editing the 'Preserve tag prefixes'
        % checkbox
        preservePrefix = get(src, 'Max') == get(src, 'Value');
    end % useGUICallback

    function selectFieldsCallback(src, ~)
        % Callback for user directly editing the 'Select fields to tag'
        % checkbox
        selectFields = get(src, 'Max') == get(src, 'Value');
    end % selectFieldsCallback

    function baseTagsCtrlCallback(src, ~)
        % Callback for user directly editing directory control textbox
        tagsFile = get(src, 'String');
        if ~isempty(strtrim(tagsFile)) && validateBaseTags(tagsFile)
            baseMap = tagsFile;
        end
    end % baseTagsCtrlCallback

    function valid = validateBaseTags(tagsFile)
        % Checks to see if the 'Base tags' passed in is valid
        valid = true;
        if isempty(fieldMap.loadFieldMap(tagsFile))
            valid = false;
            warndlg([ tagsFile ...
                ' is a invalid base tag file'], 'Invalid file');
            set(findobj('Tag', 'BaseTags'), 'String', baseMap);
        end
    end % validateBaseTags

    function useCTaggerCallback(src, ~)
        % Callback for user directly editing the 'Use CTagger' checkbox
        useGUI = get(src, 'Max') == get(src, 'Value');
        if ~useGUI
            set(findobj('Tag', 'SelectFieldsCB'), 'Enable', 'off');
            set(findobj('Tag', 'EditXMLCB'), 'Enable', 'off');
            set(findobj('Tag', 'PreservePrefixCB'), 'Enable', 'off');
        else
            set(findobj('Tag', 'SelectFieldsCB'), 'Enable', 'on');
            set(findobj('Tag', 'EditXMLCB'), 'Enable', 'on');
            set(findobj('Tag', 'PreservePrefixCB'), 'Enable', 'on');
        end
    end % useCTaggerCallback

end % tageeg_input