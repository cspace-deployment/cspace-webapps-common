# -*- coding: UTF-8 -*-
"""
A collection of functions for processing parent-child lists into hierarchical dictionaries.
The goal, which buildConceptDict accomplishes, is to go from a list like this:

    inp = [['San Francisco','California'], ['California','United States'], ['North America',None], ['Africa',None],\
    ['New York','United States'], ['United States','North America'], ['Angola','Africa'], ['Eastern Cape','South Africa'],\
    ['South Africa','Africa'], ['Rapa Nui',None]]

to a dictionary like this:

    res = {PARENT: ['Rapa Nui', {'North America': [{'United States': ['New York', {'California': ['San Francisco']}]}]},\
     {'Africa':['Angola', {'South Africa': ['Eastern Cape']}]}]}

Or in hierarchical form:

    <PARENT>
        Rapa Nui
        North America
            United States
                New York
                California
                    San Francisco
        Africa
            Angola
            South Africa
                Eastern Cape


Additionally, if a non-null root value is already set, the "if pair[3] == NONE:" statement in nullStrip()
should be replaced with "if pair[3] == <ROOT_VALUE>:". Bear in mind that the final root value is controlled by PARENT.

-----------------------------------

N.B.: The old two-column list has been replaced by a list of the form [[childName, parentName, childID, parentID],[...]...].
The hierarchy is now built from the third and fourth rows and displayed using the first and second.

"""

# This should be set to whatever the root value should be.
PARENT = 'ROOT'


def buildConceptDict(l):
    """
    Wrapper that takes in a 4-column list L and builds a hierarchical dictionary from the 3rd and 4th column of each row.
    (The first & second rows are the display names of the third & fourth rows).
    """
    return dictBuilder(nullStrip(l))


def nullStrip(l):
    """Strips out all the null values in the third column of a list L, replacing them with PARENT."""
    for pair in l:
        if pair[3] == None:
            pair[3] = PARENT
    return l


def dictBuilder(l, root=PARENT):
    """
    Takes in a list of child-parent pairs L and a root value ROOT and returns a hierarchical dictionary, maintaining sorting.
    """
    seen = 0
    d = {root: []}
    for pair in l:
        if pair[3] != root and seen:
            break
        if pair[3] == root:
            if seen == 0:
                seen = 1
            d[root].append(dictBuilder(l, pair[2]))
    if d == {root: []}:
        return root
    return d


def stripRootHTML(res):
    """Removes the ROOT level from the JSON tree"""
    # res = res[:res.rfind('</ul>')]
    return res.replace('<li><a>►</a> ' + PARENT + '<ul>', '<ul class="tree">')


def buildHTML(d, indent=0, lookup=None):
    """
    Given a dictionary D, an optional initial indent INDENT, and a lookup table LOOKUP,
    returns a string representation of the tree needed for jqTree without a root level.
    """
    return stripRootHTML(makeHTML(d, indent, lookup))


def makeHTML(d, indent=0, lookup=None):
    """
    Given a dictionary D, an optional initial indent INDENT, and a lookup table LOOKUP,
    returns a string representation of the tree needed for jqTree.
    """
    res = ''
    if not (lookup):
        print('<tr>NO LOOKUP TABLE!</tr>'
)
    space = ' '
    if not (isinstance(d, dict)):
        res += '<li>' + str(lookup[d]) + '</li>'
    for key in d:
        res += '<li><a>►</a> ' + str(lookup[key])
        if isinstance(d[key], str):
            res += '<li>' + str(lookup(d[key])) + '</li>'
        else:
            res += '<ul>'
            for val in d[key]:
                if isinstance(val, dict):
                    res += makeHTML(val, indent + 4, lookup)
                else:
                    res += '<li>' + str(lookup[val]) + '</li>'
            res += '</li></ul>'
    return res
