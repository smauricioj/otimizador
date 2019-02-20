# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:34 2018

@author: Sergio P.
"""
from gurobipy import Model, GRB, quicksum
from traceback import format_exc

from instancia import Instancia
import resultado

class Otimizador:

	def __init__(self, ins_id):
		self.ins = Instancia('{}.json'.format(ins_id))
		self.C0 = 0.25
		self.C1 = 0.5
		self.C2 = 0.25

	def begin(self):
		M = GRB.INFINITY
		n, m, Q   = self.ins.n, self.ins.m, self.ins.Q
		q, s, T   = self.ins.get_q(), self.ins.get_s(), self.ins.get_t()
		W, R, tau = self.ins.get_W(), self.ins.get_R(), self.ins.get_tau()
		T_max = self.ins.T
		arcos = tau.keys()
		origens, destinos, locais = self.ins.get_O(), self.ins.get_D(), self.ins.get_V()
		veiculos = self.ins.get_K()

		mod = Model("Roteamento")
		mod.params.MIPGap = 0.1
		mod.params.TimeLimit = 20*60

		viagens   = {(i,j,k):0 for (i,j) in tau.keys() for k in veiculos}
		instantes = {(i,k):0   for i in locais for k in veiculos}
		carga     = {(i,k):0   for i in locais for k in veiculos}
		             
		x = mod.addVars(viagens,           vtype=GRB.BINARY,     name="x")
		t = mod.addVars(instantes, lb=0.0, vtype=GRB.CONTINUOUS, name="T")
		u = mod.addVars(carga,     lb=0.0, vtype=GRB.INTEGER,    name="u")

		exp = 0
		exp += self.C0*quicksum(x[ijk] * tau[ij]
		                    for ijk in viagens for ij in arcos
		                    if ijk[0] == ij[0] and ijk[1] == ij[1])
		exp += self.C1*quicksum((T[ik] - t[i]) * (T[ik] - t[i])
		                    for i in origens for ik in instantes
		                    if ik[0] == i)
		exp += self.C2*quicksum(T[(i+n,k)] - T[(i,k)]
		                    for i in origens for k in veiculos)

		mod.setObjective(exp, GRB.MINIMIZE)

		for i in locais:
		        
		    delta_mais  = [a for (a,b) in arcos if b == i]
		    delta_menos = [b for (a,b) in arcos if a == i]

		    n_visitas = quicksum(x[ijk] for ijk in viagens
		    	                 if ijk[1] in delta_menos
		    	                 and ijk[0] == i)

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
		        
		        if i == 2*n+1:
		            mod.addConstr( sum_saida - sum_entrada == -1 )
		        elif i == 0:
		            mod.addConstr( sum_saida - sum_entrada == 1 )
		        else:
		            mod.addConstr( sum_saida - sum_entrada == 0 )
		                   
		        if i in origens:
					delta_menos_destino = [b for (a,b) in arcos if a == i+n]
					n_visitas = quicksum(x[ijk] for ijk in viagens
										 if ijk[0] == i
										 and ijk[1] in delta_menos
										 and ijk[2] == k)
					n_visitas_destino = quicksum(x[ijk] for ijk in viagens
						                         if ijk[1] in delta_menos_destino
						                         and ijk[0] == i+n
						                         and ijk[2] == k)
					dk = (i+n,k)

					mod.addConstr( n_visitas == n_visitas_destino )
					mod.addConstr( t[ik] >= T[i])
					mod.addConstr( t[dk] >= t[ik] )
 

		for ij in arcos:
		    i, j = ij[0], ij[1]
		    qj = q.copy()
		    del qj[i]

		    for k in veiculos:
		        ik, jk = (i,k), (j,k)
		        ijk = (i,j,k)

		        # n_demanda_destino = quicksum(qj[x]*x[ijk] for ijk in viagens for x in locais
		        # 							 if ijk[0] != j)

		        mod.addConstr( t[ik] + s[j] + tau[ij] - t[jk] <= (1 - x[ijk])*T_max )
		        
		        mod.addConstr( u[ik] + q[j] - u[jk] <= (1 - x[ijk])*Q )

		        # try:
		        # 	mod.addConstr( u[ik] <= Q - ( x[(0,i,k)]*(Q - max(qj.iterkeys(), key=(lambda key: q[key])) - q[i]) ) - n_demanda_destino )
		        # except KeyError as e:
		        # 	mod.addConstr( u[ik] <= Q - n_demanda_destino )

		        # mod.addConstr( q[i] <= u[ik] )
		        # mod.addConstr( Q >= u[ik] )

		        
		for k in veiculos:   
		    mod.addConstr( u[(2*n+1,k)] == 0 ) # Não há restrições para 'saidas' de
		                                       #    veículos de 2n+1, portanto carga
		                                       #    poderia ser qualquer valor.
		                                       #    Agora não.

		mod.optimize()
		print('Obj: %g' %mod.objVal)
		print('Runtime: %g' %mod.runtime)
		self.res = resultado.Resultado(self.ins)
		if mod.objVal <= 100000:
			for v in mod.getVars():
				self.res.add_trip('{}={}'.format(v.varName, v.x))
			# self.res.fig_requests()
			self.res.fig_routes()
			self.res.result_data_DB(mod.runtime, mod.objVal)
		else:
			print 'deu nada, só vai'