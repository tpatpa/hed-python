% This function takes in a string containing HED tags
% associated with a particular study and validates them based on the
% tags and attributes in the HED XML file.
%
% Usage:
%
%   >>  issues = validatestr(str);
%
%   >>  issues = validatestr(str, varargin);
%
% Input:
%
%   str
%                   A string containing HED tags that are validated.
%
%
%   Optional:
%
%   'extensionAllowed'
%                   True(default) if descendants of extension allowed tags
%                   are accepted which will generate warnings, False if
%                   they are not accepted which will generate errors.
%
%   'hedXML'
%                   The name or the path of the XML file containing
%                   all of the HED tags and their attributes.
%
% Output:
%
%   issues
%                   A string containing all of the issues found through
%                   the validation.
%
% Copyright (C) 2015 Jeremy Cockfield jeremy.cockfield@gmail.com and
% Kay Robbins, UTSA, kay.robbins@utsa.edu
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
% Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

function issues = validatestr(str, varargin)
p = parseArguments(str, varargin{:});
issues = validate(p);

    function issues = validate(p)
        % Validates a cellstr
        p.hedMaps = getHEDMaps(p);
        issues = parsestr(p.hedMaps, p.str, p.generateWarnings);
    end % validate

    function hedMaps = getHEDMaps(p)
        % Gets a structure that contains Maps associated with the HED XML
        % tags
        hedMaps = loadHEDMap();
        mapVersion = hedMaps.version;
        xmlVersion = getxmlversion(p.hedXML);
        if ~strcmp(mapVersion, xmlVersion);
            hedMaps = mapattributes(p.hedXML);
        end
    end % getHEDMaps

    function hedMaps = loadHEDMap()
        % Loads a structure that contains Maps associated with the HED XML
        % tags
        Maps = load('HEDMaps.mat');
        hedMaps = Maps.hedMaps;
    end % loadHEDMap

    function p = parseArguments(str, varargin)
        % Parses the arguements passed in and returns the results
        p = inputParser();
        p.addRequired('str', @(x) ~isempty(x) && ischar(x));
        p.addParamValue('generateWarnings', false, ...
            @(x) validateattributes(x, {'logical'}, {}));
        p.addParamValue('hedXML', 'HED.xml', ...
            @(x) (~isempty(x) && ischar(x)));
        p.parse(str, varargin{:});
        p = p.Results;
    end % parseArguments

end % validatestr