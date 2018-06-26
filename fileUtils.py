import pandas as pd

def readFile(file):
    pacientes = pd.read_csv(file)
    return pacientes