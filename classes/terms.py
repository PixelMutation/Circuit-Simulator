import sys
import numpy as np
from numpy import linspace,logspace,log10
# from math import log10

# def find_and_cast_float(item,dict,throw=True):


class Terms:
    thevenin=True
    VS=None
    ZS=None
    ZL=None
    freqs=None
    logarithmic=False
    def __init__(self,terms_dict):
        self.thevenin="VT" in terms_dict
        if self.thevenin:
            # print("Thevenin")
            self.VS=float(terms_dict["VT"])
        else:
            if "IN" in terms_dict:
                print("Norton")
                #TODO add norton logic
                sys.exit()
            else:
                raise AttributeError("Could not find Thevenin or Norton source in TERMS")
        # TODO use unified functions to check presence in dict, cast and throw errors if required
        self.ZL=float(terms_dict["RL"])
        self.ZS=float(terms_dict["RS"])
        # Find frequency range
        if "Nfreqs" in terms_dict:
            if "Fstart" in terms_dict:
                start=float(terms_dict["Fstart"])
                if "Fend" in terms_dict:
                    end=float(terms_dict["Fend"])
                    self.freqs=linspace(start,end,int(float(terms_dict["Nfreqs"])))
                else:
                    raise AttributeError("Fend not found in TERMS")
            elif "LFstart" in terms_dict:
                self.logarithmic=True
                start=log10(float(terms_dict["LFstart"]))
                if "LFend" in terms_dict:
                    end=log10(float(terms_dict["LFend"]))
                    self.freqs=logspace(start,end,int(float(terms_dict["Nfreqs"])))
                else:
                    raise AttributeError("LFend not found in TERMS")
            else:
                raise AttributeError("LFend not found in TERMS")
        else:
            raise AttributeError("Nfreqs not found in TERMS")
    def __str__(self):
        floats=""
        for f in self.freqs:
            floats+='%.2E' % f + ", "
        string=[
            "Terms object:",
            f"    Thevenin: {self.thevenin}",
            f"    Logarithmic: {self.logarithmic}",
            f"    VS: {self.VS} V",
            f"    ZS: {self.ZS} Ohms",
            f"    ZL: {self.ZL} Ohms",
            f"    Nfreqs: {len(self.freqs)}",
            f"    Range: {self.freqs[0]}Hz to {self.freqs[-1]}Hz ",
        ]
        return '\n'.join(string)