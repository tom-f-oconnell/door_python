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

from drosolf import orns
from drosolf import pns

import ipdb


# TODO how to check if r package is already installed?
utils = rpackages.importr('utils')
utils.chooseCRANmirror(ind=1)

if not rpackages.isinstalled('devtools'):
    # TODO way to install package as personal library + create one
    # by default? or run just this command as root?
    #print(dir(utils))
    utils.install_packages(StrVector(('devtools',)))
    #print(utils.installed_packages())

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

# nointeraction=True supresses a warning about loading data into the global
# workspace in R
# TODO this python syntax translate to correct R syntax?
door_data.load_door_data(nointeraction=True)


# TODO TODO cache this function. maybe even setup network wide pubchem caching.
def name2inchikey(odor_names):
    """
    Args:
        odor_names (iterable of strs): the odors to be translated to
        inchikeys

    Returns:
        odor_inchikeys (list of strs): the inchikeys for the input odors
        inchikey2name (dict: str -> str): for quickly getting the name for an
        inchikey

    """
    # TODO support single str inputs too
    odor_inchikeys = []
    inchikey2name = dict()
    for o in odor_names:
        matches = pcp.get_compounds(o, 'name')

        if len(matches) > 1:
            print('WARNING: more than one pubchem match for {}. ' + \
                'ambiguous!'.format(o))
            continue

        elif len(matches) == 0:
            print('WARNING: no pubchem matches found for {}!'.format(o))
            continue

        match = matches[0]

        odor_inchikeys.append(match.inchikey)
        inchikey2name[match.inchikey] = o

    return odor_inchikeys, inchikey2name

def check_door_hallem06():
    """
    Checks consistency of DoOR Hallem (2006, at least) responses against
    the ones I have in drosolf.

    Args:
    """
    # TODO is there not a function to list datasets? i feel like there should be
    orn_responses = orns.orns()
    hallem_odors = set(orn_responses.index)
    #manual_name_fixes = {'E2-hexenal'
    hallem_inchikeys = name2inchikey(hallem_odors)

    # EN stands for "Empty Neuron". there are also 2004.EN and 2004.WT
    r_hallem06_door = door_functions.get_dataset('Hallem.2006.EN')
    ipdb.set_trace()
    hallem06_door = pandas2ri.ri2py(r_hallem06_door)
    hallem06_door = hallem06_door.dropna()

    ipdb.set_trace()


check_door_hallem06()

pn_responses = pns.pns()
# TODO is the index supposed to be 111 long? more?
hallem_odors = set(pn_responses.index)

# TODO how different are 1-OCT and 3-OCT? 3-OCT and MCH?

# TODO is there some way to check whether an odor is in the database by
# name? i suppose it'd be better to normalize to some ID in python first
# anyway?
odor_names = ('4-methylcyclohexanol', '3-octanol')
odor_inchikeys, inchikey2name = name2inchikey(odor_names)

print(odor_inchikeys)

# TODO want dataframe w/ odor IDs (ultimately want names, but will probably
# have to translate?) and responses (hopefully in same format as mine)
# TODO so both of these seem to return something approximately what I
# want... what is the difference?
r_responses = door_functions.get_responses(StrVector(odor_inchikeys))
#responses = door_functions.get_responses(odor_inchikeys)

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

