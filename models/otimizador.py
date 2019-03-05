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
		self.C0 = 0.33
		self.C1 = 0.33
		self.C2 = 0.33

		self.optimal_method = 2
		self.res = resultado.Resultado(self.ins, self.optimal_method)

		self.save_data_DB = True

		self.save_lp = False
		if self.optimal_method == 1:
			self.output_lp_name = 'out_lifted.lp'
		elif self.optimal_method == 2:
			self.output_lp_name = 'out_base.lp'
		else:
			self.output_lp_name = None

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
		t = mod.addVars(instantes, lb=0.0, vtype=GRB.CONTINUOUS, name="t")
		u = mod.addVars(carga,     lb=0.0, vtype=GRB.INTEGER,    name="u")

		exp = 0
		exp += self.C0*quicksum(x[ijk] * tau[ij]
		                    for ijk in viagens for ij in arcos
		                    if ijk[0] == ij[0] and ijk[1] == ij[1])
		exp += self.C1*quicksum((t[ik] - T[i])
		                    for i in origens for ik in instantes
		                    if ik[0] == i)
		exp += self.C2*quicksum(t[(i+n,k)] - t[(i,k)]
		                    for i in origens for k in veiculos)

		mod.setObjective(exp, GRB.MINIMIZE)

		for i in locais:
		        
		    delta_mais  = [a for (a,b) in arcos if b == i]
		    delta_menos = [b for (a,b) in arcos if a == i]

		    n_visitas = quicksum(x[ijk] for ijk in viagens
		    	                 if ijk[1] in delta_menos
		    	                 and ijk[0] == i)

		    if i == 0:
		        mod.addConstr( n_visitas == m, name = "n_visitas_depo")
		    elif i != 2*n+1:
		        mod.addConstr( n_visitas == 1, name = "n_visitas_{}".format(i))
		    else:
		    	pass
		        
		    for k in veiculos:
		        ik = (i,k)
		        sum_entrada = quicksum( x[ijk] for ijk in [(j,i,k) for j in delta_mais] )
		        sum_saida = quicksum( x[ijk] for ijk in [(i,j,k) for j in delta_menos] )
		        
		        if i == 2*n+1:
		            mod.addConstr( sum_saida - sum_entrada == -1, name = "fluxo_{}_{}".format(i,k))
		        elif i == 0:
		            mod.addConstr( sum_saida - sum_entrada == 1, name = "fluxo_{}_{}".format(i,k) )
		        else:
		            mod.addConstr( sum_saida - sum_entrada == 0, name = "fluxo_{}_{}".format(i,k) )
		                   
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

					mod.addConstr( n_visitas == n_visitas_destino, name = "consistencia_{}_{}".format(i,k) )
					mod.addConstr( t[ik] >= T[i], name = "inicio_desejado_viagem_{}_{}".format(i,k))
					mod.addConstr( t[dk] >= t[ik], name = "fim_apos_inicio_viagem_{}_{}".format(i,k) )
					mod.addConstr( T_max >= t[dk], name = "fim_antes_total_viagem_{}_{}".format(i,k))
					mod.addConstr( u[ik] >= q[i], name = "partida_maior_demanda_carga_{}_{}".format(i,k) )
					mod.addConstr( Q >= u[ik], name = "partida_menor_capacidade_carga_{}_{}".format(i,k))
 

		for ij in arcos:
			i, j = ij[0], ij[1]
			iin = (i,i+n)
			idp = (i,2*n+1)
			ind = (i+n,2*n+1)

			for k in veiculos:
				ik, jk = (i,k), (j,k)
				ijk = (i,j,k)
				jik = (j,i,k) #motivo do try abaixo

				try:
					mod.addConstr( u[ik] + q[j] - u[jk] - (q[i] + q[j])*x[jik] <= (1 - x[ijk] - x[jik])*Q, name = "elimina_subrota_capacidade_lifted_{}_{}_{}".format(i,j,k) )
				except KeyError:
					mod.addConstr( u[ik] + q[j] - u[jk] <= (1 - x[ijk])*Q, name = "elimina_subrota_capacidade_{}_{}_{}".format(i,j,k) )

				try:
					if j in [_+1 for _ in range(n)]:
						mod.addConstr( t[ik] + s[j] + tau[ij] - t[jk] - (s[j] + tau[ij] - tau[iin] - s[i+n] - tau[ind])*x[jik] <= (1 - x[ijk])*T_max, name = "elimina_subrota_temporal_lifted_{}_{}_{}".format(i,j,k))
					else:
						mod.addConstr( t[ik] + s[j] + tau[ij] - t[jk] - (s[j] + tau[ij] - tau[idp])*x[jik] <= (1 - x[ijk])*T_max, name = "elimina_subrota_temporal_lifted_{}_{}_{}".format(i,j,k))

				except KeyError:
					mod.addConstr( t[ik] + s[j] + tau[ij] - t[jk] <= (1 - x[ijk])*T_max, name = "elimina_subrota_temporal_{}_{}_{}".format(i,j,k) )

		        
		for k in veiculos:   
		    mod.addConstr( u[(2*n+1,k)] == 0 ) # Não há restrições para 'saidas' de
		                                       #    veículos de 2n+1, portanto carga
		                                       #    poderia ser qualquer valor.
		                                       #    Agora não.

		# with open('var.txt', 'r') as file:
		# 	for line in file:
		# 		l = line.split(' ')
		# 		r_hand = float(l[-1].replace('\n',''))
		# 		l_hand = l[0].split('_')
		# 		var = l_hand[0]
		# 		if var == 'x':
		# 			index = (int(l_hand[1]),int(l_hand[2]),int(l_hand[3]))
		# 			mod.addConstr( x[index] == r_hand )
		# 		elif var in ['t', 'u']:
		# 			index = (int(l_hand[1]),int(l_hand[2]))
		# 			if var == 't':
		# 				mod.addConstr( t[index] == r_hand )
		# 			else:
		# 				mod.addConstr( u[index] == r_hand )
		# 		else:
		# 			pass

		mod.optimize()
		
		# mod.computeIIS()

		# exit()

		if self.save_data_DB:
			try:
				if mod.objVal <= 100000 :
					# print('Obj: %g' %mod.objVal)
					# print('Runtime: %g' %mod.runtime)
					for v in mod.getVars():
						self.res.add_trip('{}={}'.format(v.varName, v.x))
					# self.res.fig_requests()
					self.res.fig_routes()
					self.res.result_data_DB(mod.runtime, mod.objVal)
				else :
					self.res.reset_data_DB()
			except AttributeError:
				self.res.reset_data_DB()

		if self.save_lp:
			mod.write('temp.lp')
			f1 = open('temp.lp', 'r')
			f2 = open(self.output_lp_name, 'w')
			for line in f1:
				l = line.replace('[','_')
				l = l.replace(',','_')
				l = l.replace(']','')
				f2.write(l)
			f1.close()
			f2.close()