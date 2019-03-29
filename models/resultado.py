# -*- coding: utf-8 -*-
"""
Created on Thu May 03 13:27:14 2018

@author: Sergio P.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from networkx import DiGraph, draw_networkx_nodes, draw_networkx_edges, draw_networkx_labels
from os import path, makedirs
from math import sqrt
from json import loads, dumps
from sqlite3 import connect
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

class DataList(list):
	def __init__(self, what, by_what, size,
		         y_label_after = '', boxplot_sym = '+',
		         minor_ticks = False, log_y = False,
		         folder = ''):
		self.what = what
		self.by_what = by_what

		for _ in range(size):
			self.append([])

		self.y_label_append = ['', y_label_after]
		endings_to_split = ['veh', 'req']
		ending = self.what.split(' ')[-1]
		if ending in endings_to_split:
			self.y_label = ' '.join(self.what.split(' ')[0:-2])
		else:
			self.y_label = self.what
		self.y_label += self.y_label_append[1]

		self.x_label_append = ['', '']
		self.x_label = self.by_what

		self.xrange = [-1000, 1000]

		self.minor_ticks = minor_ticks
		self.log_y = log_y
		self.boxplot_sym = boxplot_sym
		self.folder = folder

		plt.rc('font',family='Times New Roman',size=20)

	def plot(self, save_method):
		fig, ax = plt.subplots()

		xrange_update = False
		for i, data in enumerate(self):
			if len(data) == 0:
				value_mean = None
				value_std = None
			else:
				if not xrange_update:
					xrange_update = True
					self.xrange[0] = i
				self.xrange[1] = i

		if self.log_y:
			plt.grid(True, which = 'major', ls = '-')
			ax.set_yscale('log')
		else:
			plt.grid(True, which = 'major', ls = ':')

		meanpointprops = dict(linewidth = 1.5, color = 'k', linestyle = '-.')
		boxprops = dict(linewidth = 1.5, color = 'k')
		medianprops = dict(linewidth = 1.5, color = 'k')
		whiskerprops = dict(linewidth = 1, color = 'k', linestyle = '-')
		if self.xrange != [-1000, 1000]:
			ax.boxplot( self[self.xrange[0]:self.xrange[1]+1],
						notch = False,
						whis = [5, 95],
						sym = self.boxplot_sym,
						positions = range(self.xrange[0],self.xrange[1]+1),
						showmeans = True,
						meanline = True,
						meanprops = meanpointprops,
						boxprops = boxprops,
						medianprops = medianprops,
						whiskerprops = whiskerprops )
		
		meanpointprops['label'] = u'Média'
		medianprops['label'] = u'Mediana'
		element_handle = [Line2D([0],[0],**meanpointprops),
						  Line2D([0],[0],**medianprops)]
		plt.legend( handles = element_handle,
					loc=2, ncol=1, shadow=True,
					fancybox=True, numpoints = 1)

		plt.xlabel(self.x_label)
		plt.ylabel(self.y_label)

		save_method(self.what, self.folder)
		plt.close(fig)

class Resultado:
	
	def __init__(self, ins, optimal_method = 1):
		self.ins = ins
		self.fmt = 'png'
		self.mapa_limites = [-5,5]
		self.optimal_method = optimal_method

		self.rotas = []
		self.tempos = []
		for i in range(self.ins.m):
			self.rotas.append([])
			self.tempos.append([])

		self.instancia_path = self.ins.instancia_path
		self.instancia_name = path.split(self.instancia_path)[1].split('.')[0]

	def save_image_data(self, name, folder = ''):	
		fig_file_name = '{}.{}'.format(name, self.fmt)

		fig_file_path = self.instancia_path
		for i in range(3):
			fig_file_path = path.dirname(fig_file_path)
		fig_file_path = path.join(fig_file_path, 'resultados')
		fig_file_path = path.join(fig_file_path, self.instancia_name)
		fig_file_path = path.join(fig_file_path, folder)

		if not path.isdir(fig_file_path):
			makedirs(fig_file_path)

		fig_file = path.join(fig_file_path,fig_file_name)
		try:
			plt.savefig(fig_file, bbox_inches = 'tight')
		except IOError:
			arg = (self.instancia_name,fig_file_name)
			print u'Arquivo {}/{} nao salvo devido a IOError.'.format(*arg)
		plt.clf()

	def add_trip(self, string):
		data = self.ins.get_pos_requests()

		def aprox(value, target, rang):
			if value > target + rang:
				return False
			elif value < target - rang:
				return False
			else:
				return True

		index, value = string.split('=')
		var, tup = index[:-1].split('[')
		if var == 't':
			i, k = [int(x) for x in tup.split(',')]
			self.tempos[k].append((i,float(value)))
		elif var == 'x' and aprox(float(value), 1.0, 0.0001):
			i, j, k = [int(x) for x in tup.split(',')]
			if i == 0 and j == (2 * self.ins.n) + 1:
				pass
			else:
				self.rotas[k].append((i,j))

	def fig_routes(self):
		fig, ax = plt.subplots()
		colors = ['b', 'g', 'm', 'k', 'c', 'r', 'y', 'w']
		styles = ['solid', 'dotted', 'dashed']*3
		edge_color = []
		pos = {}
		G = DiGraph()

		pos[0] = [2, 5]
		pos[(2 * self.ins.n) + 1] = [8, 5]
		if self.ins.n == 1:
			pos[1] = [4, 5]
			pos[2] = [6, 5]
		else:
			visitas = []

			def domino(data):
				start = cursor = 0
				d = dict(data)
				while True:
					yield cursor
					try:
						cursor = d[cursor]
					except KeyError:
						return

			for rota in self.rotas:
				vertices = list(domino(rota))
				visitas += [i for i in vertices if i > 0 and i <= self.ins.n]

			for i, y_pos in enumerate(list(np.linspace(9,1,self.ins.n))):
				pos[visitas[i]] = [4, y_pos]
				pos[visitas[i]+self.ins.n] = [6, y_pos]

		G.add_nodes_from(range((2 * self.ins.n)+2))
		if self.ins.n <= 10:
			draw_networkx_nodes(G, pos, ax = ax)
		else:
			draw_networkx_nodes(G, pos, ax = ax, node_size = 200)
		draw_networkx_labels(G, pos)

		element_handle = []
		for id_veh, route in enumerate(self.rotas):
			G.add_edges_from(route)
			draw_networkx_edges(G, pos, edgelist = route, edge_color = colors[id_veh], edge_style = styles[id_veh] )
			props = dict(linewidth = 1.5, color = colors[id_veh],
				         label = u'Veículo {}'.format(id_veh), linestyle = styles[id_veh])
			line = Line2D([0],[0],**props)
			element_handle.append(line)
		plt.legend( handles = element_handle,
					loc=2, ncol=1, shadow=True,
					fancybox=True, numpoints = 1)
		kwargs = {
			'axis':'both',
		    'which':'both',      # both major and minor ticks are affected
		    'bottom':False,      # ticks along the edges are off
		    'top':False,         
		    'left':False,
		    'right':False,
		    'labelbottom':False,  # labels along the edges are off
		    'labelleft':False		
		}
		plt.tick_params(**kwargs)		
		plt.grid(False)

		self.save_image_data('routes')

	def fig_requests(self):
		data = self.ins.get_pos_requests()
		fig, ax = plt.subplots()
		center, = ax.plot(0, 0, 'k*', markersize=20)

		for d in data:
			if d[1] > self.mapa_limites[1] or d[2] > self.mapa_limites[1]:
				self.mapa_limites[1] = max(d[0], d[1])
			if d[1] < self.mapa_limites[0] or d[2] < self.mapa_limites[0]:
				self.mapa_limites[0] = min(d[0], d[1])
			ax.text(d[1], d[2], str(d[0]), va = 'center', ha ='center', fontsize = 14)

		pos_drops_x = [d[1] for d in data if d[3] == 'drop']
		pos_drops_y = [d[2] for d in data if d[3] == 'drop']
		drops, = ax.plot(pos_drops_x, pos_drops_y, 'bo', markersize = 20)

		pos_picks_x = [d[1] for d in data if d[3] == 'pick']
		pos_picks_y = [d[2] for d in data if d[3] == 'pick']
		picks, = ax.plot(pos_picks_x, pos_picks_y, 'rs', markersize = 20)

		limites = [(self.mapa_limites[1],self.mapa_limites[1]+1),
				   (-1 * (self.mapa_limites[1]+1),-1 * (self.mapa_limites[1]))]
		for limite in limites:
			plt.axvspan(limite[0], limite[1], facecolor = '#cecece', alpha = 0.5)
			plt.axhspan(limite[0], limite[1], facecolor = '#cecece', alpha = 0.5)

		ticks = range(int(-1 * (self.mapa_limites[1]+1)),int(self.mapa_limites[1]+2),1)
		ax.set_xticks(ticks)
		ax.set_yticks(ticks)		
		plt.grid(True)

		leg = plt.legend([drops, picks, center],
						 ['levar', 'buscar', u'estação'],
			             loc='best', ncol=1, shadow=True,
			             fancybox=True, numpoints = 1)
		leg.get_frame().set_alpha(0.5)
		
		self.save_image_data('requests')
		plt.close(fig)

	def plot_global_result_data(self):
		conn = connect('persistent_data.db')
		c = conn.cursor()

		wheres = {}
		wheres['otimizado'] = 1
		wheres['leilao'] = 0

		for base_folder, where_opt in wheres.iteritems():
			for n_veh_plot in range(1,6):
				folder = 'Instancias de frota {}'.format(str(n_veh_plot).zfill(2))
				w_time_data = DataList(u"Tempo de espera {} veh".format(n_veh_plot),
					                   u"Número de pedidos", 25, folder = base_folder+'\\'+folder)
				t_time_data = DataList(u"Tempo de viagem {} veh".format(n_veh_plot),
					                   u"Número de pedidos", 25, folder = base_folder+'\\'+folder)		
				o_time_data = DataList(u"Tempo de processamento {} veh".format(n_veh_plot),
					                   u"Número de pedidos", 25, ' (s)', '', True, True,
					                   folder = base_folder+'\\'+folder)
				# r_time_data = DataList(u"Razao tempo de viagem real e ideal {} veh".format(n_veh_plot),
				# 					   u"Número de pedidos", 25, folder = folder)

				travel_ratio_dict = {}
				for row in c.execute("SELECT * FROM specific_results WHERE opt = {}".format(where_opt)):
					n_req, n_veh, n_ins, req_id, opt, d_time, i_time, e_time = row
					if n_veh == n_veh_plot and n_req != 0:
						# travel_ratio_dict_key = '{}_{}_{}_{}'.format(n_req,n_veh,n_ins,req_id)
						# travel_ratio_dict[travel_ratio_dict_key] = []
						# travel_ratio_dict[travel_ratio_dict_key].append(e_time - i_time)
						w_time_data[n_req].append(i_time - d_time)
						t_time_data[n_req].append(e_time - i_time)

				# for row in c.execute('''SELECT * FROM requests'''):
				# 	n_req, n_veh, n_ins, req_id, x, y = row[0], row[1], row[2], row[3], row[7], row[8]
				# 	if n_veh == n_veh_plot and n_req != 0:
				# 		distance = sqrt(x**2 + y**2)
				# 		travel_ratio_dict_key = '{}_{}_{}_{}'.format(n_req,n_veh,n_ins,req_id+1)
				# 		try:
				# 			travel_ratio_dict[travel_ratio_dict_key].append(distance)
				# 		except KeyError:
				# 			pass

				# for k, v in travel_ratio_dict.iteritems():
				# 	print k, v
				# 	# try:
				# 	if v[0] >= v[1] and v[1] != 0:
				# 		r_time_data[int(k.split('_')[0])].append(v[0]/v[1])
				# 	# except ValueError:
				# 		# pass

				for row in c.execute("SELECT * FROM global_results WHERE opt = {}".format(where_opt)):
					n_req, n_veh, runtime = row[0], row[1], row[8]
					if n_veh == n_veh_plot and n_req != 0:
						o_time_data[n_req].append(runtime)

				w_time_data.plot(self.save_image_data)
				t_time_data.plot(self.save_image_data)
				o_time_data.plot(self.save_image_data)
				# r_time_data.plot(self.save_image_data)

		# 	for n_req_plot in range(2,15):
		# 		folder = 'Instancias de req {}'.format(str(n_req_plot).zfill(2))
		# 		w_time_data = DataList(u"Tempo de espera {} req".format(n_req_plot),
		# 			                   u"Frota veicular", 25, folder = base_folder+'\\'+folder)
		# 		t_time_data = DataList(u"Tempo de viagem {} req".format(n_req_plot),
		# 			                   u"Frota veicular", 25, folder = base_folder+'\\'+folder)

		# 		for row in c.execute("SELECT * FROM specific_results WHERE opt = {}".format(where_opt)):
		# 			n_req, n_veh, n_ins, req_id, opt, d_time, i_time, e_time = row
		# 			if n_req == n_req_plot:
		# 				w_time_data[n_veh].append(i_time - d_time)
		# 				t_time_data[n_veh].append(e_time - i_time)

		# 		w_time_data.plot(self.save_image_data)
		# 		t_time_data.plot(self.save_image_data)


		# d_requ_data = DataList(u"Distancia do terminal",
		# 					   u"Número de pedidos", 25)
		# t_requ_data = DataList(u"Instante desejado de atendimento",
		# 	                   u"Número de pedidos", 25)

		# for row in c.execute("SELECT * FROM requests"):
		# 	n_req, desired_time, x, y = row[0], row[5], row[7], row[8]
		# 	distance = sqrt(x**2 + y**2)
		# 	if n_req != 0:
		# 		t_requ_data[n_req].append(desired_time)
		# 		d_requ_data[n_req].append(distance)

		# d_requ_data.plot(self.save_image_data)
		# t_requ_data.plot(self.save_image_data)

		conn.close()

	def result_data_DB_leilao_specific(self, id_req, desired_time, ini_time, end_time):

		n_req, v_veh, n_ins = [int(x) for x in self.instancia_name.split('_')]
		data = (n_req, v_veh, n_ins, id_req, self.optimal_method, desired_time, ini_time, end_time)
		conn = connect('persistent_data.db')
		c = conn.cursor()
		c.execute(''' REPLACE INTO specific_results VALUES (?,?,?,?,?,?,?,?)''', data)

		conn.commit()
		conn.close()

	def result_data_DB_leilao_global(self, rtime, obj, w_times_mean, w_times_std, t_times_mean, t_times_std, t_traveled):

		n_req, v_veh, n_ins = [int(x) for x in self.instancia_name.split('_')]
		data = (n_req, v_veh, n_ins, self.optimal_method, w_times_mean, w_times_std, t_times_mean, t_times_std, rtime, obj, t_traveled)
		conn = connect('persistent_data.db')
		c = conn.cursor()
		c.execute(''' REPLACE INTO global_results VALUES (?,?,?,?,?,?,?,?,?,?,?)''', data)

		conn.commit()
		conn.close()

	def result_data_DB(self, rtime, obj):
		req_data = self.ins.get_pos_requests()
		tau = self.ins.get_tau()
		n_req, n_veh, n_ins = [int(x) for x in self.instancia_name.split('_')]
		w_times = np.array([])
		t_times = np.array([])
		specific_data = list()
		t_traveled = 0
		for veh, trips in enumerate(self.rotas):
			for trip in trips:
				t_traveled += tau[trip]
		for req in req_data:
			desired_time = req[4]
			ini_time = None
			for id_veh, data_veh in enumerate(self.rotas):
				for tup in data_veh:
					if req[0] in tup:
						id_veh_service = id_veh
			for tup in self.tempos[id_veh_service]:
				if tup[0] == req[0]:
					ini_time = tup[1]
				elif tup[0] == req[0]+self.ins.n:
					end_time = tup[1]
			w_times = np.append(w_times, ini_time - desired_time)
			t_times = np.append(t_times, end_time - ini_time)
			specific_data.append( (n_req, n_veh, n_ins, req[0], self.optimal_method, desired_time, ini_time, end_time) )
		global_data = [(n_req, n_veh, n_ins, self.optimal_method,
			            w_times.mean(), w_times.std(),
			            t_times.mean(), t_times.std(),
			            rtime, obj, t_traveled)]

		conn = connect('persistent_data.db')
		c = conn.cursor()
		for data in global_data:
			c.execute(''' REPLACE INTO global_results VALUES (?,?,?,?,?,?,?,?,?,?,?)''', data)
		for data in specific_data:
			c.execute(''' REPLACE INTO specific_results VALUES (?,?,?,?,?,?,?,?)''', data)

		conn.commit()
		conn.close()

	def reset_data_DB(self):
		n_req, n_veh, n_ins = [int(x) for x in self.instancia_name.split('_')]
		data = (n_req, n_veh, n_ins, self.optimal_method)
		conn = connect('persistent_data.db')
		c = conn.cursor()
		c.execute(''' DELETE FROM global_results
					  WHERE n_req = {} and
					        n_veh = {} and
					        n_ins = {} and
					        processo = "{}"  '''.format(*data))
		c.execute(''' DELETE FROM specific_results
					  WHERE n_req = {} and
					        n_veh = {} and
					        n_ins = {} and
					        processo = "{}"  '''.format(*data))
		conn.commit()
		conn.close()

	def print_routes(self):
		print self.rotas






























