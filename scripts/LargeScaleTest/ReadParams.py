#!/usr/bin/env python

import os
import json

def GetMostRecentParams(paramsFolder):
    files = os.listdir(paramsFolder)
    prefix = 'params'
    numbers = [int(f[len(prefix):]) for f in files if f.startswith(prefix) and not f.endswith('~')]
    paramsNumber = max(numbers)
    paramsFile = paramsFolder + prefix + str(paramsNumber)
    params = {}
    with open(paramsFile) as f:
        params = json.load(f)
    return params

