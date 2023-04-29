import sys
import numpy as np
from numpy import linspace,logspace,log10
# from math import log10

class Terms:
    VT=None
    ZS=None
    ZL=None
    freqs=None
    def __init__(self,terms_dict):
        
        if "VT" in terms_dict:
            # print("Thevenin")
            self.VT=float(terms_dict["VT"])
        else:
            if "IN" in terms_dict:
                print("Norton")
                #TODO add norton logic
                sys.exit()
            else:
                print("Could not find Thevenin or Norton source")
                sys.exit()
        self.ZL=float(terms_dict["RL"])
        self.ZS=float(terms_dict["RS"])
        if "Fstart" in terms_dict:
            start=float(terms_dict["Fstart"])
            end=float(terms_dict["Fend"])
            self.freqs=linspace(start,end,int(float(terms_dict["Nfreqs"])))
        else:
            start=log10(float(terms_dict["LFstart"]))
            end=log10(float(terms_dict["LFend"]))
            self.freqs=logspace(start,end,int(float(terms_dict["Nfreqs"])))
    def __str__(self):
        floats=""
        for f in self.freqs:
            floats+='%.2E' % f + ", "
        string=[
            "Terms object:",
            f"    VT: {self.VT} V",
            f"    ZS: {self.ZS} Ω",
            f"    ZL: {self.ZL} Ω",
            f"    Nfreqs: {len(self.freqs)}",
            f"    Range: {self.freqs[0]}Hz to {self.freqs[-1]}Hz ",
        ]
        return '\n'.join(string)