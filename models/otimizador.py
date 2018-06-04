# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:34 2018

@author: Sergio P.
"""
from gurobipy import Model, GRB, quicksum

from instancia import Instancia
from resultado import Resultado

class Otimizador:

	def __init__(self, ins_id):
	    self.ins = Instancia('{}.json'.format(ins_id))
	    self.res = Resultado(self.ins)

	def begin(self):
		M = GRB.INFINITY
		n, m, Q   = self.ins.n, self.ins.m, self.ins.Q
		q, s, t   = self.ins.get_q(), self.ins.get_s(), self.ins.get_t()
		W, R, tau = self.ins.get_W(), self.ins.get_R(), self.ins.get_tau()
		arcos = tau.keys()
		origens, destinos, locais = self.ins.get_O(), self.ins.get_D(), self.ins.get_V()
		veiculos = self.ins.get_K()
		mod = Model("Roteamento")

		viagens   = {(i,j,k):0 for (i,j) in tau.keys() for k in veiculos}
		instantes = {(i,k):0   for i in locais for k in veiculos}
		carga     = {(i,k):0   for i in locais for k in veiculos}
		             
		x = mod.addVars(viagens,   lb=0.0, ub=1.0, vtype=GRB.INTEGER,    name="x")
		T = mod.addVars(instantes, lb=0.0,         vtype=GRB.CONTINUOUS, name="T")
		u = mod.addVars(carga,     lb=0.0,         vtype=GRB.INTEGER,    name="u")

		exp = 0
		exp += 0.0*quicksum(x[ijk] * tau[ij]
		                    for ijk in viagens for ij in arcos
		                    if ijk[0] == ij[0] and ijk[1] == ij[1])
		exp += 0.5*quicksum((T[ik] - t[i]) * (T[ik] - t[i])
		                    for ik in instantes for i in origens
		                    if ik[0] == i)
		exp += 0.5*quicksum((T[(i,k)] - T[(i+n,k)]) * (T[(i,k)] - T[(i+n,k)])
		                    for i in origens for k in veiculos)

		mod.setObjective(exp, GRB.MINIMIZE)

		for i in locais:
		        
		    delta_mais  = [a for (a,b) in arcos if b == i]
		    delta_menos = [b for (a,b) in arcos if a == i]

		    # print '-'*40
		    # print 'origem: ',i
		    # print 'lista: ',[a for a in viagens if a[0] == i and a[1] in delta_menos]

		    n_visitas = quicksum(x[ijk] for ijk in viagens
		    	                 if ijk[1] in delta_menos
		    	                 and ijk[0] == i)

		    # Eq. 1.5
		    if i == 0:
		        mod.addConstr( n_visitas == m )
		    elif i != 2*n+1:
		        mod.addConstr( n_visitas == 1 )
		    else:
		    	pass
		        
		    for k in veiculos:
		        ik = (i,k)
		        sum_entrada = quicksum( x[ijk] for ijk in [(j,i,k) for j in delta_mais] )
		        sum_saida = quicksum( x[ijk] for ijk in [(i,j,k) for j in delta_menos] )
		        
		        # Eq. 1.6
		        if i == 2*n+1:
		            mod.addConstr( sum_saida - sum_entrada == -1 )
		        elif i == 0:
		            mod.addConstr( sum_saida - sum_entrada == 1 )
		        else:
		            mod.addConstr( sum_saida - sum_entrada == 0 )
		                   
		        if i in origens:
					delta_menos_destino = [b for (a,b) in arcos if a == i+n]
					# print '-'*40
					# print 'origem: ',i
					# print 'lista origem:  ',[a for a in viagens if a[0] == i and a[1] in delta_menos and a[2] == k]
					# print 'lista destino:  ',[a for a in viagens if a[0] == i+n and a[1] in delta_menos_destino and a[2] == k]
					n_visitas = quicksum(x[ijk] for ijk in viagens
										 if ijk[0] == i
										 and ijk[1] in delta_menos
										 and ijk[2] == k)
					n_visitas_destino = quicksum(x[ijk] for ijk in viagens
						                         if ijk[1] in delta_menos_destino
						                         and ijk[0] == i+n
						                         and ijk[2] == k)
					dk = (i+n,k)

					# Eq. 1.7
					mod.addConstr( n_visitas == n_visitas_destino )
					mod.addConstr( T[ik] >= t[i])
					mod.addConstr( T[dk] >= T[ik] )
 

		for ij in arcos:
		    i, j = ij[0], ij[1]

		    for k in veiculos:
		        ik, jk = (i,k), (j,k)
		        ijk = (i,j,k)

		        # Eq. 1.9
		        mod.addConstr( T[ik] + s[i] + tau[ij] - T[jk] <= (1 - x[ijk])*1000 )
		        
		        # Eq. 1.8
		        mod.addConstr( u[ik] + q[i] - u[jk] <= (1 - x[ijk])*Q )
		        
		for k in veiculos:   
		    mod.addConstr( u[(2*n+1,k)] == 0 ) # Não há restrições para 'saidas' de
		                                       #    veículos de 2n+1, portanto carga
		                                       #    poderia ser qualquer valor.
		                                       #    Agora não.

		mod.optimize()
		try:
			print('Obj: %g' %mod.objVal)
			print('Runtime: %g' %mod.runtime)
			for v in mod.getVars():
				# if v.x != 0:
					# print v.varName, ':', v.x
				self.res.addTrip('{}={}'.format(v.varName, v.x))
			self.res.fig_requests()
			self.res.fig_routes()
			self.res.save_global_results(mod.runtime)
		except Exception:
			pass