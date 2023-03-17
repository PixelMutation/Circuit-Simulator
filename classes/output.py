import numpy as np

from classes.circuit import Circuit,Terms

class Column:
    real=None
    unit=None
    prefix=None
    decibel=None
    values=[]
    def __init__(self,real:bool,unit:str,prefix:str,decibel:bool,values:list=[]):
        self.real=real
        self.unit=unit
        self.prefix=prefix
        self.decibel=decibel
        self.values=values

# SI prefixes and their scale factors
prefixes={
    "p":1e-12,
    "n":1e-9,
    "u":1e-6,
    "m":1e-3,
    "k":1e3,
    "M":1e6,
    "G":1e9
}

class Output:
    results={}
    circuit=None
    terms=None
    # Constructor
    def __init__(self,output_dict,circuit,terms):
        self.circuit=circuit
        self.terms=terms
        # Store frequency column first
        self.results["Freq"]=[Column(True,"Hz",None,False,terms.freqs)]
        for var,unit in output_dict.items():
            # check for and remove dB modifier
            if "dB" in unit:
                dB=True
                unit=unit.replace("dB","")
            else:
                dB=False
            # check for and remove prefixes
            prefix=None
            if unit[0] in prefixes:
                prefix=unit[0]
                uint=uint[1:] # remove prefix

            self.results[var]=[
                Column(True,unit,prefix,dB),
                Column(False,unit,prefix,dB)
            ]
            # if in dB, the second column is Rads thus has no prefix
            if dB:
                self.results[var][1].unit="Rads"
                self.results[var][1].prefix=None
    # Calculate all output variables and store them
    def calc_variables(self):
        for var,columns in self.results.items():
            if var!="Freq":
                for idx,val in self.circuit.calc_output(var).enumerate():
                    columns[0].values[idx]=val.real
                    columns[1].values[idx]=val.imag