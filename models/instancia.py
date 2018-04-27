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
        
    def __get_distance(self, df, fonte, antro):
        '''
        Função genérica de distância entre 2 pontos
            a partir dos dados de um DataFrame
        '''
        x1 = df.get_value(fonte-1,"service_point_x")
        y1 = df.get_value(fonte-1,"service_point_y")
        x2 = df.get_value(antro-1,"service_point_x")
        y2 = df.get_value(antro-1,"service_point_y")
        return round(sqrt( (x1-x2)**2 + (y1-y2)**2 ), 2)
        
    def __get_distance_deposito(self, df, local):
        '''
        Função genérica de distância entre 1 ponto
            e o local do depósito
            a partir dos dados de um DataFrame
        '''
        x1 = df.get_value(local-1,"service_point_x")
        y1 = df.get_value(local-1,"service_point_y")
        x2 = self.deposito_x
        y2 = self.deposito_y
        return round(sqrt( (x1-x2)**2 + (y1-y2)**2 ), 2)
        

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
        # Tempo de viagem do veículo que fica parado é nulo
        tau = {(0,2*self.n+1):0}

        # Dataframes utilizados para encontrar pedidos
        #   e diferenciar entre drops e picks
        df_total = DataFrame(self.__requests)
        df_drops = df_total.loc[df_total["service_type"] == "drop"]
        df_picks = df_total.loc[df_total["service_type"] == "pick"]
        id_origens_drops = [x+1 for x in list(df_drops.index.values)]
        id_destinos_picks = [x+1 for x in list(df_picks.index.values)]
        pedidos = list(df_total.index.values)

        # Um grafo é um dicionário de listas
        graph = defaultdict(list)

        def addEdge(g,u,v):
            g[u].append(v)

        # Para todos os pedidos
        for pedido in pedidos:
            origem_pedido, destino_pedido = pedido+1, pedido+1+self.n

            # Adiciona arcos do depósito para a origem
            #   do destino para o depósito
            #   e entre a origem e o destino
            addEdge(graph, 0, origem_pedido)
            addEdge(graph, destino_pedido, 2*self.n+1)
            addEdge(graph, origem_pedido, destino_pedido)

            # Para todos os outros pedidos
            for outro_pedido in pedidos:
                # (se for o mesmo, ignora)
                if pedido == outro_pedido:
                    pass
                else:
                    origem_outro_pedido, destino_outro_pedido = outro_pedido+1, outro_pedido+1+self.n

                    # Adiciona arcos entre as origens
                    #   entre os destinos
                    #   entre a origem do primeiro e o destino do segundo
                    #   e entre o destino do primeiro e a origem do segundo
                    addEdge(graph, origem_pedido, origem_outro_pedido)
                    addEdge(graph, destino_pedido, destino_outro_pedido)
                    addEdge(graph, origem_pedido, destino_outro_pedido)
                    addEdge(graph, destino_pedido, origem_outro_pedido)

        def genEdge(graph):
            edges = []
            for node in graph:
                for neighbour in graph[node]:
                    edges.append((node, neighbour))
            return edges
        
        # Arcos são tuplas entre nós, nomeados 'fonte' e 'antro'
        for arco in genEdge(graph):
            fonte = arco[0]
            antro = arco[1]
            
            # Se a fonte for o deposito inicial
            if fonte == 0:
                if antro in id_origens_drops:
                    # o tau é nulo se o antro for de drop
                    tau[arco] = 0
                else:
                    # ou é a distância entre o deposito e o local
                    tau[arco] = self.__get_distance_deposito(df_total, antro)
            # Se o antro for o deposito final
            elif antro == 2*self.n+1:
                fonte = fonte-self.n
                if fonte in id_destinos_picks:
                    # o tau é nulo se a fonte for de pick
                    tau[arco] = 0
                else:
                    # ou é a distância entre o deposito e o local
                    tau[arco] = self.__get_distance_deposito(df_total,fonte)
            # Se a fonte for uma origem de pedido
            elif fonte <= self.n:
                # E o antro for o destino desse mesmo pedido
                if antro == fonte+self.n:
                    # o tau é a distancia entre o deposito e o local
                    tau[arco] = self.__get_distance_deposito(df_total,fonte)
                else:
                    # Se o arco for entre origens de drops
                    #   ou entre origem de drop e destino de pick
                    #   o tau é nulo
                    if fonte in id_origens_drops:
                        if antro in id_origens_drops or antro-self.n in id_destinos_picks:
                            tau[arco] = 0
                    else:
                        if antro > self.n:
                            antro = antro-self.n
                        # se não, o tau é a distância entre os dois locais
                        tau[arco] = self.__get_distance(df_total,fonte,antro)
            # Se a fonte for um destino de pedido                   
            else:
                fonte = fonte-self.n
                if antro > self.n:
                    antro = antro-self.n
                    if fonte in id_origens_drops:
                        if antro in id_destinos_picks:
                            tau[arco] = self.__get_distance_deposito(df_total,fonte)
                        else:
                            tau[arco] = self.__get_distance(df_total,fonte,antro)
                    else:
                        if antro in id_destinos_picks:
                            tau[arco] = 0
                        else:
                            tau[arco] = self.__get_distance_deposito(df_total,fonte)
                else:
                    if fonte in id_origens_drops:
                        if antro in id_origens_drops:
                            tau[arco] = self.__get_distance_deposito(df_total,fonte)
                        else:
                            tau[arco] = self.__get_distance(df_total,fonte,antro)
                    else:
                        if antro in id_destinos_picks:
                            tau[arco] = self.__get_distance_deposito(df_total,antro)
                        else:
                            tau[arco] = 0


                # # Se a fonte for destino de pick e o antro for origem de drop
                # #   então o tau é nulo
                # if fonte in id_destinos_picks and antro in id_origens_drops:
                #     tau[arco] = 0
                # else:
                #     if antro > self.n:
                #         antro = antro-self.n
                #     # se não, o arco é a distância entre os dois locais
                #     tau[arco] = self.__get_distance(df_total,fonte,antro)               
        return tau



                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        