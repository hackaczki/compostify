import pandas as pd

def read_composte_data():
    data = pd.read_csv("municipal-waste-recycled-and-composted-6.csv")
    return data[['Countries:text', 'Countries:code', '2004:number', '2020:number']].dropna().sort_values('2004:number')
