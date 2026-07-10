import os
import sys
import warnings
import numpy as np
import pandas as pd
import requests
import xgboost as xgb
import matplotlib

from datetime import date 

def predict(a, b):
    #TODO: predict
    pass

def main():
    today = date.today()
    fixtures = pd.read_csv("data/fixtures.csv")


