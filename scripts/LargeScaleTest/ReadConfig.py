#!/usr/bin/env python

import os
import json

def GetMostRecentConfig(configFolder):
    files = os.listdir(configFolder)
    prefix = 'config'
    numbers = [int(f[len(prefix):]) for f in files if f.startswith(prefix) and not f.endswith('~')]
    configNumber = max(numbers)
    configurationFile = configFolder + prefix + str(configNumber)
    config = {}
    with open(configurationFile) as f:
        config = json.load(f)
    return config

def GetMostRecentConfigNumber(configFolder):
    files = os.listdir(configFolder)
    prefix = 'config'
    numbers = [int(f[len(prefix):]) for f in files if f.startswith(prefix) and not f.endswith('~')]
    configNumber = max(numbers)

    return configNumber

