import xmltodict
import numpy as np

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as pl

def xml_getObjects(doc, node, attr, val):
    return [n for n in doc[node] if n['@{0:s}'.format(attr)] == val]

def xml_getRegions(doc, region):
    return xml_getObjects(doc, 'region', 'group', region)

def xml_getSubregions(doc, subregion):
    return xml_getObjects(doc, 'subregion', 'name', subregion)

def xml_getSamplings(doc, sampling):
    return xml_getObjects(doc, 'field', 'name', sampling)

files = ['gTowerInfo.txt', 'jTowerInfo.txt']
regions = ['Reg_GTower', 'Reg_JTower']
subregions = ['GTower', 'JTower']
samplings = ['GTsampling', 'JTsampling']

''' Step 1:
        parse the XML file entirely into memory
'''
towerDefs = xmltodict.parse(file('IdDictCalorimeter_DC3-05.xml').read())['IdDictionary']

''' Step 2:
        Iterate over gTower/jTower, etc... and figure out the mappings
'''
for f, region, subregion, sampling in zip(files, regions, subregions, samplings):
    # get tower information
    tower_info = np.loadtxt(f, skiprows=1, dtype='str')
    # load up xml definitions for given set
    info = {'region': [], 'subregion': [], 'sampling': []}
    info['region'] = xml_getRegions(towerDefs, region)
    info['subregion'] = xml_getSubregions(towerDefs, subregion)
    info['sampling'] = xml_getSamplings(towerDefs, sampling)

    # convert to integers dynamically except for the first column which is just an ID in hex format
    for ID, pos_neg_eta, regionIndex, sampling, ieta, iphi in ([row[0]] + map(int, row[1:]) for row in tower_info):
        pass
