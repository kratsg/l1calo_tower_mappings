import xmltodict
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pl
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from palettable import colorbrewer

def colorbar_index(ncolors, cmap, **kwargs):
    #cmap = cmap_discretize(cmap, ncolors)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors+0.5)
    colorbar = pl.colorbar(mappable, **kwargs)
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(range(ncolors))

def cmap_discretize(cmap, N):
    """Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet.
        N: number of colors.

    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)
    """

    if type(cmap) == str:
        cmap = pl.get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N+1)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki])
                       for i in xrange(N+1) ]
    # Return colormap object.
    return mcolors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)

def xml_getObjects(doc, node, attr, val):
    return [n for n in doc[node] if n['@{0:s}'.format(attr)] == val]

def xml_getRegions(doc, region):
    return xml_getObjects(doc, 'region', 'group', region)

def xml_getSubregions(doc, subregion):
    return xml_getObjects(doc, 'subregion', 'name', subregion)

def xml_getSamplings(doc, sampling):
    return xml_getObjects(doc, 'field', 'name', sampling)

def list_getRegion(regions, region, val):
    for r in regions:
        if xml_getObjects(r, 'range', 'field', region)[0]['@value'] == val:
            return r

def indexToCoordinates(index, start, step):
    return int(index)*float(step) + float(start)

files = ['gTowerInfo.txt', 'jTowerInfo.txt']
prefixes = ['G', 'J']

''' Step 1:
        parse the XML file entirely into memory
'''
towerDefs = xmltodict.parse(file('IdDictCalorimeter_DC3-05.xml').read())['IdDictionary']

''' Step 2:
        Iterate over gTower/jTower, etc... and figure out the mappings
'''
for f, prefix in zip(files, prefixes):
    region = 'Reg_{0:s}Tower'.format(prefix)
    regionName = '{0:s}Tregion'.format(prefix)
    subregion = '{0:s}Tower'.format(prefix)
    samplingName = '{0:s}Tsampling'.format(prefix)
    etaName = '{0:s}Teta'.format(prefix)
    phiName = '{0:s}Tphi'.format(prefix)

    # get tower information
    tower_info = np.loadtxt(f, skiprows=1, dtype='str')
    # load up xml definitions for given set
    info = {'region': [], 'subregion': [], 'sampling': []}
    info['region'] = xml_getRegions(towerDefs, region)
    info['subregion'] = xml_getSubregions(towerDefs, subregion)
    info['sampling'] = xml_getSamplings(towerDefs, samplingName)

    towerInfo = []
    # convert to integers dynamically except for the first column which is just an ID in hex format
    for ID, pos_neg_eta, regionIndex, sampling, ieta, iphi in tower_info:
        regionDefs = list_getRegion(info['region'], regionName, regionIndex)
        etaDefs = xml_getObjects(regionDefs, 'range', 'field', etaName)
        phiDefs = xml_getObjects(regionDefs, 'range', 'field', phiName)
        etaStart = regionDefs['@eta0']
        phiStart = regionDefs['@phi0']
        etaStep = regionDefs['@deta']
        phiStep = regionDefs['@dphi']

        eta = indexToCoordinates(ieta, etaStart, etaStep)
        phi = indexToCoordinates(iphi, phiStart, phiStep)
        # rectangles are drawn from bottom left (x,y)
        # negative eta needs to be shifted to account for the flipping
        #       if you take a piece of paper and draw it out, you realize
        #       we have to shift it to the right by etaStep (so it flips correctly and is
        #       drawn correctly from bottom left)
        eta += ((-np.sign(int(pos_neg_eta)) + 1)/2.)*float(etaStep)
        eta *= np.sign(int(pos_neg_eta))

        towerInfo.append((eta, phi, int(regionIndex), int(sampling), float(etaStep), float(phiStep)))

    towerInfo = np.array(towerInfo)
    cmap = pl.cm.jet

    x = towerInfo[:,0]
    y = towerInfo[:,1]
    z = towerInfo[:,2]
    x_sizes = towerInfo[:,4]
    y_sizes = towerInfo[:,5]

    gridSpacing = 0.2
    if prefix == 'J':
        gridSpacing = 0.1
    N = len(set(z))

    zvals = list(set(z))
    colors = colorbrewer.qualitative.Paired_10
    cmap = mcolors.ListedColormap(colors.mpl_colors)
    bounds = np.arange(N+1)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    hatches = ['/', '\\', '//', '\\\\', '///', '\\\\\\', '////', '\\\\\\\\', '/////', '\\\\\\\\\\']

    fig, ax = pl.subplots(figsize=(16, 16))
    for xx, yy, zz, xx_size, yy_size, c in zip(x, y, z, x_sizes, y_sizes, cmap(norm(z))):
        # lower zorder is drawn first
        zorder = z.max() - zz
        rect = pl.Rectangle( (xx, yy), xx_size, yy_size, facecolor=c, edgecolor='white', alpha=0.5, zorder=zorder, hatch=hatches[norm(zz)])
        ax.add_patch(rect)

    cbaxes = fig.add_axes([0.13, 0.8, 0.77, 0.03])

    cbar = matplotlib.colorbar.ColorbarBase(cbaxes, cmap=cmap, boundaries=bounds, norm=norm, orientation='horizontal')
    cbar.set_ticks(np.linspace(0, N, N+1)+0.5)
    cbar.set_ticklabels(range(N))
    cbaxes.set_xlabel('region ID')

    ax.set_xlim((-5, 5))
    ax.set_ylim((0, 6.5))
    ax.set_xticks(np.arange(-5, 5, gridSpacing), minor=True)
    ax.set_yticks(np.arange(0, 6.4, gridSpacing), minor=True)
    ax.grid(True, which='both', linestyle='--')
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    ax.set_xlabel(r'$\eta$')
    ax.set_ylabel(r'$\phi$')

    ax.set_aspect('equal')

    fig.savefig('{0:s}Towers.pdf'.format(prefix), dpi=90, bbox_inches='tight')

