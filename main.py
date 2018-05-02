# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 13:14:13 2018

@author: Sergio P.
"""
from gurobipy import Model, GRB, quicksum
from models.instancia import Instancia

if __name__ == "__main__":
    ins = Instancia('instancia004.json')
    M = GRB.INFINITY
    n, m, Q = ins.n, ins.m, ins.Q
    q, s, t = ins.get_q(), ins.get_s(), ins.get_t()
    W, R = ins.get_W(), ins.get_R()
    tau = ins.get_tau()
    custo = tau
    # for k, v in tau.iteritems():
    #     print k, ' : ',v
    
    origens  = [o+1 for o in range(n)]
    destinos = [d+1+n for d in range(n)]
    locais   = [0]+origens+destinos+[2*n+1]
    veiculos = range(m)

    tau = custo
    
    arcos = custo.keys()
    vertices = list(set(sum(arcos, ())))
    
    mod = Model("Roteamento")
    
    viagens   = {(i,j,k):0 for (i,j) in custo.keys() for k in veiculos}
    visitas   = {(i,k):0   for i in locais for k in veiculos}
    instantes = {(i,k):0   for i in locais for k in veiculos}
    carga     = {(i,k):0   for i in locais for k in veiculos}
                 
    x = mod.addVars(viagens,   lb=0.0, ub=1.0, vtype=GRB.INTEGER,    name="x")
    y = mod.addVars(visitas,   lb=0.0, ub=1.0, vtype=GRB.INTEGER,    name="y")
    T = mod.addVars(instantes, lb=0.0,         vtype=GRB.CONTINUOUS, name="T")
    u = mod.addVars(carga,     lb=0.0,         vtype=GRB.INTEGER,    name="u")
    
    exp = 0
    exp += 0.5*quicksum(x[ijk]*custo[ij]
                        for ijk in viagens for ij in arcos
                        if ijk[0] == ij[0] and ijk[1] == ij[1])
    exp += 0.3*quicksum((T[ik] - t[i])*(T[ik] - t[i])
                        for ik in visitas for i in origens
                        if ik[0] == i)
    exp += 0.2*quicksum((T[(i,k)] - T[(i+n,k)])*(T[(i,k)] - T[(i+n,k)])
                        for i in origens for k in veiculos)

    mod.setObjective(exp, GRB.MINIMIZE)

    for i in locais:
        # Eq. 1.4
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
            
            # Eq. 1.3 e 1.5
            if i == 2*n+1:
                mod.addConstr( y[ik] == sum_entrada )
                mod.addConstr( sum_saida - sum_entrada == -1 )
            elif i == 0:
                mod.addConstr( y[ik] == sum_saida )
                mod.addConstr( sum_saida - sum_entrada == 1 )
            else:
                mod.addConstr( y[ik] == sum_saida )
                mod.addConstr( sum_saida - sum_entrada == 0 )
                       
            if i in origens:
                d = i+n
                dk = (d,k)
                
                # Eq. 1.6
                mod.addConstr( y[ik] == y[dk] )
                
                # Eq. 1.9
                mod.addConstr( t[i] <= T[ik] )
                mod.addConstr( T[ik] <= t[i] + W[i])
                
                # Eq. 1.10
                mod.addConstr( T[dk] <= T[ik] + R[i] + s[i] - s[d] )
                
            
    for ij in arcos:
        for k in veiculos:
            i, j = ij[0], ij[1]
            ik, jk = (i,k), (j,k)
            ijk = (i,j,k)
            
            # Eq. 1.8
            mod.addConstr( T[ik] + s[i] + tau[ij] - T[jk] <= (1 - x[ijk])*1000 )
            
            # Eq. 1.7
            mod.addConstr( u[ik] + q[i] - u[jk] <= (1 - x[ijk])*Q )
            
    for k in veiculos:   
        mod.addConstr( u[(2*n+1,k)] == 0 ) # Não há restrições para 'saidas' de
                                           #    veículos de 2n+1, portanto carga
                                           #    poderia ser qualquer valor.
                                           #    Agora não.
    
    # mod.addConstr( x[(1,2,0)] == 1 )
    mod.optimize()
    mod.printAttr('X')
    # try:
    #     mod.printAttr('X')
    # except:
    #     mod.feasRelaxS(0, True, False, True);
    #     mod.optimize()
    #     mod.printAttr('X')
    print('Obj: %g' %mod.objVal)


























