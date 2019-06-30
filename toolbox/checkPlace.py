#!/usr/bin/python

import sys

from toolbox.cswaUtils import getConfig
import toolbox.cswaGetAuthorityTree


config = toolbox.getConfig({'webapp': 'pahma_Packinglist_Dev'})

place = sys.argv[1]
print('place:', place)
places = toolbox.cswaGetAuthorityTree.getAuthority('places', 'Placeitem', place, config.get('connect', 'connect_string'))
if len(places) < 200:
    for placeitem in places:
        print(placeitem)
else:
    print(place, ':', len(places))
