# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 14:23:44 2018

@author: Sergio P.
"""
from os import path
from json import loads
from math import sqrt
from pandas import DataFrame
from collections import defaultdict

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
        return round(sqrt( (x1-x2)**2 + (y1-y2)**2 ), 2)
        
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
        
    def get_tau(self):
        tau = {(0,2*self.n+1):0}

        df_total = DataFrame(self.__requests)
        df_drops = df_total.loc[df_total["service_type"] == "drop"]
        df_picks = df_total.loc[df_total["service_type"] == "pick"]
        id_origens_drops = [x+1 for x in list(df_drops.index.values)]
        id_destinos_drops = [x+1+self.n for x in list(df_drops.index.values)]
        id_origens_picks = [x+1+self.n for x in list(df_picks.index.values)]
        id_destinos_picks = [x+1 for x in list(df_picks.index.values)]
        id_origens = id_origens_drops + id_origens_picks
        id_destinos = id_destinos_drops + id_destinos_picks

        pedidos = list(df_total.index.values)
        graph = defaultdict(list)

        def addEdge(g,u,v):
            g[u].append(v)

        def genEdge(graph):
            edges = []
            for node in graph:
                for neighbour in graph[node]:
                    edges.append((node, neighbour))
            return edges

        for pedido in pedidos:
            origem_pedido, destino_pedido = pedido+1, pedido+1+self.n

            addEdge(graph, 0, origem_pedido)
            addEdge(graph, destino_pedido, 2*self.n+1)
            addEdge(graph, origem_pedido, destino_pedido)

            for outro_pedido in pedidos:
                if pedido == outro_pedido:
                    pass
                else:
                    origem_outro_pedido, destino_outro_pedido = outro_pedido+1, outro_pedido+1+self.n

                    addEdge(graph, origem_pedido, origem_outro_pedido)
                    addEdge(graph, destino_pedido, destino_outro_pedido)
                    addEdge(graph, origem_pedido, destino_outro_pedido)
                    addEdge(graph, destino_pedido, origem_outro_pedido)
        
        for arco in genEdge(graph):
            fonte = arco[0]
            antro = arco[1]

            if fonte == 0:
                if antro in id_origens_drops:
                    tau[arco] = 0
                else:
                    x = df_total.get_value(antro-1,"service_point_x")
                    y = df_total.get_value(antro-1,"service_point_y")
                    tau[arco] = self.__get_distance_deposito(x,y)
            elif antro == 2*self.n+1:
                id_fonte = fonte-self.n
                if id_fonte in id_destinos_picks:
                    tau[arco] = 0
                else:
                    x = df_total.get_value(id_fonte-1,"service_point_x")
                    y = df_total.get_value(id_fonte-1,"service_point_y")
                    tau[arco] = self.__get_distance_deposito(x,y)
            elif fonte >= self.n:
                if antro == fonte+self.n:
                    x = df_total.get_value(fonte-1,"service_point_x")
                    y = df_total.get_value(fonte-1,"service_point_y")
                    tau[arco] = self.__get_distance_deposito(x,y)
                else:
                    if fonte in id_origens_drops and antro in id_origens_drops:
                        tau[arco] = 0
                    elif fonte in id_origens_drops and antro-self.n in id_destinos_picks:
                        tau[arco] = 0
                    else:
                        pass
            else:
                pass
                
        print tau



                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        