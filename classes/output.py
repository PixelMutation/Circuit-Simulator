import numpy as np
import csv

from classes.circuit import Circuit
from classes.terms import Terms


CSV_LINE_WIDTH=11

class Column:
    real=None
    unit=None
    prefix=None
    decibel=None
    full_unit=""
    values=[]
    def __init__(self,real:bool,unit:str,prefix:str,decibel:bool,values:list):
        self.real=real
        self.unit=unit
        self.prefix=prefix
        self.decibel=decibel
        self.values=values
        if decibel:
            self.full_unit+="dB"
        if not prefix is None:
            self.full_unit+=prefix
        if not unit is None:
            self.full_unit+=unit
    def __str__(self):
        string=[
            f"      Real: {self.real}\n",
            f"      Unit: {self.unit}\n",
            f"      Prefix: {self.prefix}\n",
            f"      Decibel: {self.decibel}\n",
            # f"    Values: {self.values}"
        ]
        return ''.join(string)


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
        self.results["Freq"]=[Column(None,"Hz",None,False,terms.freqs)]
        for var,unit in output_dict.items():

            dB=False
            prefix=None
            # check for and remove dB modifier
            if not unit is None:
                # print(unit)
                if not unit is None and "dB" in unit:
                    dB=True
                    unit=unit.replace("dB","")
                if not len(unit)==0:
                    # check for and remove prefixes
                    if unit[0] in prefixes:
                        prefix=unit[0]
                        unit=unit[1:] # remove prefix
                else:
                    unit=None

            self.results[var]=[
                Column(True,unit,prefix,dB,[0 for i in range(len(terms.freqs))]),
                Column(False,unit,prefix,dB,[0 for i in range(len(terms.freqs))])
            ]
            # if in dB, the second column is Rads thus has no prefix
            if dB:
                self.results[var][1].unit="Rads"
                self.results[var][1].prefix=None
    # Calculate all output variables and store them
    def calc_variables(self):
        for var,columns in self.results.items():
            if var!="Freq ":
                values=self.circuit.calc_output(var)
                for idx,val in enumerate(values):
                    columns[0].values[idx]=np.real(val)
                    columns[1].values[idx]=np.imag(val)
    def save_csv(self,path):
        with open(path+".csv","w") as f:
            
            writer = csv.writer(f,lineterminator="\n")
            vars=[]
            units=[]
            values=[[] for i in range(len(self.results["Freq"][0].values))]
            for var,columns in self.results.items():
                for column in columns:
                    if column.real is None:
                        vars.append(var.rjust(CSV_LINE_WIDTH))
                    else:
                        if column.real:
                            vars.append(f"Re({var})".rjust(CSV_LINE_WIDTH))
                        else:
                            vars.append(f"Im({var})".rjust(CSV_LINE_WIDTH))
                    units.append(column.full_unit.rjust(CSV_LINE_WIDTH))
                    for idx,val in enumerate(column.values):
                        if val is None:
                            values[idx].append("None".rjust(CSV_LINE_WIDTH))
                        else:
                            values[idx].append(('%.3e' % val).rjust(CSV_LINE_WIDTH))
            # print(vars)
            writer.writerow(vars)
            # print(units)
            writer.writerow(units)
            # print(values[0])
            for row in values:
                writer.writerow(row)



                
    def __str__(self):
        results_string=""
        for var,columns in self.results.items():
            for column in columns:
                results_string+="\n        "+var+"\n   "
                col_strings=str(column).splitlines(keepends=True)
                results_string+='   '.join(col_strings)
        string=[
            "Output object:",
            f"    Results:{results_string}",
        ]
        return '\n'.join(string)
