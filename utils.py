import pandas as pd
import numpy as np

class AddressCombinator:

    def __init__(self):
        self.affiliation = 'Affiliation 1 Department, Institution'
        self.city = 'City (e.g. Brisbane)'
        self.state = 'State'
        self.country = 'Country'

    def combine_address(self, row):
        tags = [self.affiliation, self.city, self.state, self.country]
        elements = [row[tag] for tag in tags if type(row[tag]) is str]
        return ", ".join(elements)