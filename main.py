# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 13:14:13 2018

@author: Sergio P.
"""

from models.otimizador import Otimizador
from models.gerador import Gerador

if __name__ == "__main__":
    ger = Gerador()
    ger.set_requests_data(3)
    ger.save_ins()
    exit()
    otm = Otimizador('04001')
    otm.begin()

