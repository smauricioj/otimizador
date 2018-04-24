# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 14:23:44 2018

@author: Sergio P.
"""
from os import path
from json import loads
from math import sqrt

class Instancia:
    '''
    Classe que implementa uma instancia do cenário
    em que se resolve o problema de otimização
    de rotas veiculares
    '''
    
    def __init__(self, name):
        '''
        Recebe o nome do arquivo de instância para inicializar a classe
        '''
        actual_path = path.dirname(path.abspath("__file__"))
        instancia_path = path.join(actual_path,'models\\instancias\\'+name)
        with open(instancia_path, 'r') as file:
            d = loads(file.read())
            file.close()
        self.__requests = d['requests']
        self.__service_time = d['static_data']['service_time']
        self.n = len(self.__requests)
        self.m = d['static_data']['number_of_vehicles']
        self.Q = d['static_data']['max_vehicle_capacity']

        self.deposito_x = 0
        self.deposito_y = 0
        
    def __get_distance(self, x1, y1, x2, y2):
        '''
        Função genérica de distância entre 2 pontos
        '''
        return sqrt( (x1-x2)^2 + (y1-y2)^2 )
        
    def __get_distance_deposito(self, x1, y1):
        return self.__get_distance(x1, y1, self.deposito_x, self.deposito_y)
        

    def __get_base(self, initial = None, offset = False, item = None):
        '''
        Função genérica para captar dados simples do json
        e formar um dicionário
        '''
        if not initial:
            initial = {}
        for i, r in enumerate(self.__requests):
            if offset and type(offset) == int:
                index = i+1+offset
            else:
                index = i+1
            if type(item) == int:
                initial[index] = item
            elif type(item) == str:
                initial[index] = r[item]
            else:
                pass
        return initial

    def get_q(self):
        d = {0:0, 2*self.n+1:0}
        d = self.__get_base(d, offset = False, item = 1)
        return self.__get_base(d, offset = self.n, item = -1)
        
    def get_s(self):
        d = {0:0, 2*self.n+1:0}
        d = self.__get_base(d, offset = False, item = self.__service_time)
        return self.__get_base(d, offset = self.n, item = self.__service_time)
        
    def get_t(self):
        return self.__get_base(offset = False, item = "desired_time")
      
    def get_W(self):
        return self.__get_base(offset = False, item = "max_wait_time")
        
    def get_R(self):
        return self.__get_base(offset = False, item = "max_ride_time")
        
                    
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        