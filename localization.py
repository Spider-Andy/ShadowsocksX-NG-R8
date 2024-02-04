# coding=utf-8
# Created by Spider-Andy on 2024-01-23
# Search for xib files in the specified folder, parse files, and generate corresponding *.strings files
#

import os
import re
import subprocess
import fnmatch
import xml.etree.ElementTree as ET
# Xib files folder
packagePath = 'ShadowsocksX-NG/'
# *.strings folder
resourcesPath = packagePath+'resources/'


def fetch_files_recursive(directory, extension):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '*' + extension):
            matches.append(os.path.join(root, filename))
    return matches


def find_substring_in(s, sub):
    if sub in s:
        return True
    else:
        return False


localizables = {}
# Read Localizable.strings file to generate Localizable.strings file associated with XIB file
# Only read the Localizable.strings file under the path ./ShadowsocksX NG/resources/
#
for file in fetch_files_recursive('./'+resourcesPath, 'Localizable.strings'):
    filePath = file.split('/')
    path = filePath[len(filePath) - 2]
    local = filePath[len(filePath) - 2].split('.')[0]
    localizables[local] = {'path': file.rsplit("/", 1)[0]}
    with open(file, 'r') as f:
        properties = {}
        for line in f:
            propertArray = line.split("=")
            if len(propertArray) == 2:
                properties[propertArray[0].strip()] = propertArray[1].strip()
        localizables[local]['properties'] = properties

tagsList = {
    'window': 'NSWindow',
    'menu': 'NSMenu',
    'menuItem': 'NSMenuItem',
    'buttonCell': 'NSButtonCell',
    'textFieldCell': 'NSTextFieldCell',
    'toolbarItem': 'NSToolbarItem',
    'tabViewItem': 'NSTabViewItem',
}

tagsToFilter = [
    'action',
    'dependencies',
    'deployment',
    'button',
    'font',
    'color',
    'image',
    'constraints',
    'constraint',
    'outlet',
    'resources',
    'point',
    'connections',
    'rect',
    'subviews',
    'modifierMask',
    'capability',
    'imageView',
    'autoresizingMask',
    'real',
    'textField',
    'behavior',
    'allowedInputSourceLocales',
    'objects',
    'windowStyleMask',
    'comboBox',
    'comboBoxCell',
    'items',
    'binding',
    'string',
    'scroller',
    'size',
    'nil',
    'customObject',
    'bool',
    'dictionary',
    'box',
    'userDefinedRuntimeAttributes',
    'userDefinedRuntimeAttribute',
    'progressIndicator',
    'windowPositionMask',
    'view',
    'allowedToolbarItems',
    'tableColumnResizingMask',
    'userDefaultsController',
    'numberFormatter',
    'plugIn',
    'scrollView',
    'value',
    'imageCell',
    'defaultToolbarItems',
    'tableColumns',
    'tableColumn',
    'secureTextFieldCell',
    'tableHeaderCell',
    'secureTextField',
    'clipView',
    'objectValues',
    'tabView',
    'toolbar',
    'tableView',
    'tabViewItems',
    'textView',
    'customView'
]
undefinedTags = set()

# Parse xib file child


def parse_xib_file_child(child):
    tagsLists = []

    def parse_child(child):
        for subChild in child:
            if tagsList.get(subChild.tag) != None:
                # /* Class = "NSMenuItem"; title = "Servers"; ObjectID = "u5M-hQ-VSc"; */
                attr = subChild.attrib
                if attr.get('title') != None:
                    # Convert title to "title"
                    title = '"' + attr.get('title') + '"'
                    tagsLists.append(
                        {
                            'type': 'title',
                            'id': attr.get('id'),
                            'title': title,
                            'className': tagsList.get(subChild.tag)
                        })
                elif attr.get('label') != None:
                    title = '"' + attr.get('label') + '"'
                    tagsLists.append(
                        {
                            'type': 'label',
                            'id': attr.get('id'),
                            'label': title,
                            'className': tagsList.get(subChild.tag)
                        })
                elif attr.get('paletteLabel') != None:
                    title = '"' + attr.get('paletteLabel') + '"'
                    tagsLists.append(
                        {
                            'type': 'paletteLabel',
                            'id': attr.get('id'),
                            'paletteLabel': title,
                            'className': tagsList.get(subChild.tag)
                        })
            elif subChild.tag not in tagsToFilter:
                undefinedTags.add(subChild.tag)

            if len(subChild) > 0:
                parse_child(subChild)
    parse_child(child)
    return tagsLists

# Generate xib file association localization file


def generate_xib_string_file(filePath):
    tree = ET.parse(filePath)
    root = tree.getroot()
    tagsLists = parse_xib_file_child(root)
    if len(tagsLists) > 0:
        result = re.search(r'[^/]+(?!.*/)[^\.xib]', filePath)
        fileName = result.group()
        for local in localizables:
            properties = localizables[local].get('properties')
            path = localizables[local].get('path')
            file = open(path + '/' + fileName + '.strings',
                        mode='w', encoding="utf-8")
            for tag in tagsLists:
                # /* Class = "NSMenuItem"; title = "Import Bunch Json File"; ObjectID = "15a-D6-JJo"; */
                # "15a-D6-JJo.title" = "Import Bunch Json File";
                file.write('\n')
                if tag.get('type') == 'title':
                    file.write('/* Class = "' + tag.get('className') + '"; title = ' +
                               tag.get('title') + '; ObjectID = "' + tag.get('id') + '"; */\n')
                    file.write('"'+tag.get('id')+'.title"')
                    file.write(' = ')
                    if properties.get(tag.get('title')) != None:
                        file.write(properties.get(tag.get('title')))
                    else:
                        file.write(tag.get('title'))
                        file.write(';')
                    file.write('\n')
                elif tag.get('type') == 'paletteLabel':
                    # /* Class = "NSToolbarItem"; paletteLabel = "General"; ObjectID = "w0N-kL-X0c"; */
                    # "w0N-kL-X0c.paletteLabel" = "常规设置";
                    file.write('/* Class = "' + tag.get('className') + '"; paletteLabel = ' +
                               tag.get('paletteLabel') + '; ObjectID = "' + tag.get('id') + '"; */\n')
                    file.write('"'+tag.get('id')+'.paletteLabel"')
                    file.write(' = ')
                    if properties.get(tag.get('paletteLabel')) != None:
                        file.write(properties.get(tag.get('paletteLabel')))
                    else:
                        file.write(tag.get('paletteLabel'))
                        file.write(';')
                    file.write('\n')
                elif tag.get('type') == 'label':
                    # /* Class = "NSTabViewItem"; label = "HTTP"; ObjectID = "MFd-Rl-0zu"; */
                    # "MFd-Rl-0zu.label" = "HTTP";
                    file.write('/* Class = "' + tag.get('className') + '"; label = ' +
                               tag.get('label') + '; ObjectID = "' + tag.get('id') + '"; */\n')
                    file.write('"'+tag.get('id')+'.label"')
                    file.write(' = ')
                    if properties.get(tag.get('label')) != None:
                        file.write(properties.get(tag.get('label')))
                    else:
                        file.write(tag.get('label'))
                        file.write(';')
                    file.write('\n')
            file.close()


print("-------------------- fetch xib files --------------------")
# fetch xib files
for filePath in fetch_files_recursive('./' + packagePath, '.xib'):
    if find_substring_in(filePath, packagePath):
        generate_xib_string_file(filePath)

if len(undefinedTags) > 0:
    print("-------------------- print undefinedTags --------------------")
    for undefinedTag in undefinedTags:
        print('This tag does not define whether to generate a string or filter: ' + undefinedTag)
