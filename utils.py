import pandas as pd
import numpy as np

def combine_address(row):
    tags = ['Affiliation 1 Department, Institution', 'City (e.g. Brisbane)', 'State', 'Country']
    elements = [row[tag] for tag in tags if type(row[tag]) is str]

    return ", ".join(elements)