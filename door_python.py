#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
For loading most recent version of DoOR database into Python, as a pandas
dataframe. Some helper functions for translating odors, checking DoOR, and
transforming the DoOR responses to higher orders.
"""

from __future__ import print_function
from __future__ import division

import pandas as pd
import numpy as np
from scipy import spatial
from rpy2.robjects import packages as rpackages
from rpy2.robjects.vectors import StrVector
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
from rpy2 import robjects as ro
import pubchempy as pcp

from drosolf import pns


pn_responses = pns.pns()
# TODO is the index supposed to be 111 long? more?
hallem_odors = set(pn_responses.index)

# TODO how different are 1-OCT and 3-OCT? 3-OCT and MCH?

# TODO how to check if r package is already installed?
utils = rpackages.importr('utils')
utils.chooseCRANmirror(ind=1)

if not rpackages.isinstalled('devtools'):
    # TODO way to install package as personal library + create one
    # by default? or run just this command as root?
    print(dir(utils))
    utils.install_packages(StrVector(('devtools',)))
    print(utils.installed_packages())

else:
    print('devtools installed!')

devtools = importr('devtools')

# TODO make timeout longer / retry?
if not rpackages.isinstalled('DoOR.data'):
    devtools.install_github('ropensci/DoOR.data')

if not rpackages.isinstalled('DoOR.functions'):
    devtools.install_github('ropensci/DoOR.functions')

door_data = importr('DoOR.data')
door_functions = importr('DoOR.functions')
print(dir(door_functions))

# TODO what is the the nointeraction=TRUE bit for, in load_door_data(...)?
# TODO way to load it to a dataframe? or otherwise how to get it out of
# the r workspace / inspect the workspace to see what it loaded?
door_data.load_door_data()

# TODO is there some way to check whether an odor is in the database by
# name? i suppose it'd be better to normalize to some ID in python first
# anyway?
odor_names = ('4-methylcyclohexanol', '3-octanol')
odors_inchikeys = []
inchikey2name = dict()
for o in odor_names:
    possible_matches = pcp.get_compounds(o, 'name')

    assert len(possible_matches) == 1, 'more than one pubchem match for ' +\
        o + '. ambiguous!'
    match = possible_matches[0]

    odors_inchikeys.append(match.inchikey)
    inchikey2name[match.inchikey] = o

print(odors_inchikeys)

# TODO want dataframe w/ odor IDs (ultimately want names, but will probably
# have to translate?) and responses (hopefully in same format as mine)
# TODO so both of these seem to return something approximately what I
# want... what is the difference?
r_responses = door_functions.get_responses(StrVector(odors_inchikeys))
#responses = door_functions.get_responses(odors_inchikeys)

responses = pandas2ri.ri2py(r_responses)
only_with_data = responses.dropna()
# most important this filters out the sensilla recordings
# but it also filters out the recorded IRs and the one GR
only_ors = only_with_data[only_with_data['ORs'].apply(lambda x: 'Or' in x \
    and not 'noOr' in x)]

# TODO it seems one or both of 4-mch / 3-oct are listed as in one / both of
# hallem papers (in DoOR), but i am pretty sure neither is in the 2006...
# what's up? error?
only_ors['ORs'] = only_ors['ORs'].apply(lambda x: x[2:])
