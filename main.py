# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 13:14:13 2018

@author: Sergio P.
"""
from gurobipy import Model, GRB, quicksum
from models.instancia import Instancia

if __name__ == "__main__":
    ins = Instancia('instancia.json')
    M = GRB.INFINITY
    n, m, Q = ins.n, ins.m, ins.Q
    q, s, t = ins.get_q(), ins.get_s(), ins.get_t()
    W, R = ins.get_W(), ins.get_R()
    
    #print q
    #print s
    #print t
    #print W
    #print R
    
    origens  = [o+1 for o in range(n)]
    destinos = [d+1+n for d in range(n)]
    locais   = [0]+origens+destinos+[2*n+1]
    veiculos = range(m)
                 
    custo = {(0,1):  1, (0,2):  1, (0,5):  0,
             (1,2):  1, (1,3):  1, (1,4):  1,
             (2,1):  1, (2,3):  1, (2,4):  1,
             (3,2):  1, (3,4):  1, (3,5):  1,
             (4,1):  1, (4,3):  1, (4,5):  1}
             
    tau =   {(0,1):  1, (0,2):  1, (0,5):  0,
             (1,2):  1, (1,3):  1, (1,4):  1,
             (2,1):  1, (2,3):  1, (2,4):  1,
             (3,2):  1, (3,4):  1, (3,5):  1,
             (4,1):  1, (4,3):  1, (4,5):  1}
             
    #custo = {(0,1):  1, (0,3):  0, (1,2):  1, (2,3):  1}
    #tau = {(0,1):  1, (0,3):  0, (1,2):  2, (2,3):  1}
            
    #s = {0: 0, 1: 3, 2: 3, 3:0}
    #q = {0: 0, 1: 1, 2:-1, 3:0}
    #t = {1: 5}
    #W = {1: 2}
    #R = {1: 6}
    
    arcos = custo.keys()
    vertices = list(set(sum(arcos, ())))
    
    #print arcos
    #print vertices
    #for ijk in viagens:
    #    print ijk
    
    mod = Model("Roteamento")
    
    viagens   = {(i,j,k):0 for (i,j) in custo.keys() for k in veiculos}
    visitas   = {(i,k):0   for i in locais for k in veiculos}
    instantes = {(i,k):0   for i in locais for k in veiculos}
    carga     = {(i,k):0   for i in locais for k in veiculos}
                 
    x = mod.addVars(viagens,   lb=0.0, ub=1.0, vtype=GRB.INTEGER,    name="x")
    y = mod.addVars(visitas,   lb=0.0, ub=1.0, vtype=GRB.INTEGER,    name="y")
    T = mod.addVars(instantes, lb=0.0,         vtype=GRB.CONTINUOUS, name="T")
    u = mod.addVars(carga,     lb=0.0,         vtype=GRB.INTEGER,    name="u")
    
    pesos = [0.1, 0.3, 0.6]
    soma_custos = quicksum(x[ijk]*custo[ij]
                               for ijk in viagens for ij in arcos
                               if ijk[0] == ij[0] and ijk[1] == ij[1])
    soma_tempos_viagens = quicksum( (T[ik] - t[i])*(T[ik] - t[i])
                                        for ik in visitas for i in origens
                                        if ik[0] == i)
    soma_tempos_espera = quicksum( (T[(i,k)] - T[(i+n,k)])*(T[(i,k)] - T[(i+n,k)])
                                        for i in origens for k in veiculos)
    somas = [soma_custos, soma_tempos_viagens, soma_tempos_espera]
    soma_final = None
    for i in range(3):
        soma_final += pesos[i]*somas[i]

    mod.setObjective(soma_final, GRB.MINIMIZE)
    
    #mod.setObjective(quicksum(T[ik] - t[i] for ik in visitas for i in origens
    #                          if ik[0] == i), GRB.MINIMIZE)
    #
    #mod.setObjective(quicksum(T[(i,k)] - T[(i+n,k)] for i in origens for k in veiculos
    #                          ), GRB.MINIMIZE)
    
    for i in locais:
        # Eq. 1.3
        if i not in [0, 2*n+1]:
            mod.addConstr( quicksum(y[ik] for ik in visitas if ik[0] == i) == 1 )
        else:
            mod.addConstr( quicksum(y[ik] for ik in visitas if ik[0] == i) == m )
            
        delta_mais  = [a for (a,b) in arcos if b == i]
        delta_menos = [b for (a,b) in arcos if a == i]
            
        for k in veiculos:
            ik = (i,k)
            all_ijk_delta_mais  = [(j,i,k) for j in delta_mais]
            all_ijk_delta_menos = [(i,j,k) for j in delta_menos]                               
            sum_entrada = quicksum(x[ijk] for ijk in viagens if ijk in all_ijk_delta_mais)
            sum_saida = quicksum(x[ijk] for ijk in viagens if ijk in all_ijk_delta_menos)
            
            # Eq. 1.4 e 1.5
            if i == 2*n+1:
                mod.addConstr( y[ik] == sum_entrada )
                mod.addConstr( sum_saida - sum_entrada == -1 )
            elif i == 0:
                mod.addConstr( y[ik] == sum_saida )
                mod.addConstr( sum_saida - sum_entrada == 1 )
            else:
                mod.addConstr( y[ik] == sum_saida )
                mod.addConstr( sum_saida - sum_entrada == 0 )
            
            # Eq. 1.8
            mod.addConstr( q[i] + u[ik] <= Q )
            
            if i in origens:
                d = i+n
                dk = (d,k)
                
                # Eq. 1.6
                mod.addConstr( y[ik] == y[dk] )
                
                # Eq. 1.10
                mod.addConstr( t[i] <= T[ik] )
                mod.addConstr( T[ik] <= t[i] + W[i] )
                
                # Eq. 1.11
                mod.addConstr( T[dk] <= T[ik] + R[i] + s[i] - s[d] )
                
            
    for ij in arcos:
        for k in veiculos:
            i, j = ij[0], ij[1]
            ik, jk = (i,k), (j,k)
            ijk = (i,j,k)
            
            # Eq. 1.9
            mod.addConstr( T[ik] + s[i] + tau[ij] - T[jk] <= (1 - x[ijk])*100 )
            
            # Eq. 1.7
            mod.addConstr( u[ik] - u[jk] + Q*y[jk] <= Q - q[j] )
            
    for k in veiculos:        
        mod.addConstr( u[(2*n+1,k)] == 0 ) # Não há restrições para 'saidas' de
                                           #    veículos de 2n+1, portanto carga
                                           #    poderia ser qualquer valor.
                                           #    Agora não.
        
#    mod.optimize()
#    mod.printAttr('X')
#    print('Obj: %g' %mod.objVal)


























