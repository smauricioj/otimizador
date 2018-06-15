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
from math import cos, sin
from json import loads, dumps
from sqlite3 import connect

class DataList(list):
	def __init__(self, what, by_what, size,
		         y_label_after = '', boxplot_sym = '+',
		         minor_ticks = False, log_y = False):
		self.what = what
		self.by_what = by_what

		self.mean = {}
		self.mean['data'] = []
		self.mean['plot_marker'] = '*'

		self.std = {}
		self.std['data'] = []
		self.std['plot_marker'] = 's'

		for _ in range(size):
			self.append([])

		self.y_label_append = ['', y_label_after]
		if self.what.split(' ')[-1] == 'veh':
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

	def plot(self, save_method):
		fig, ax = plt.subplots()

		xrange_update = False
		for i, data in enumerate(self):
			if len(data) == 0:
				value_mean = None
				value_std = None
			else:
				value_mean = np.array(data).mean()
				value_std = np.array(data).std()
				if not xrange_update:
					xrange_update = True
					self.xrange[0] = i
				self.xrange[1] = i
			self.mean['data'].append(value_mean)
			self.std['data'].append(value_std)

		if self.log_y:
			plt.grid(True, which = 'minor', ls = ':')
			plt.grid(True, which = 'major', ls = '-')
			method = ax.semilogy
		else:
			plt.grid(True, which = 'major', ls = ':')
			method = ax.plot

		method(range(0,len(self.mean['data'])), self.mean['data'],
				linestyle = ' ', marker = self.mean['plot_marker'],
				markersize = 10, label = u'Média')

		ax.boxplot(self[self.xrange[0]:self.xrange[1]+1],
					notch = False,
					sym = self.boxplot_sym,
					positions = range(self.xrange[0],self.xrange[1]+1))
		plt.xlabel(self.x_label)
		plt.ylabel(self.y_label)
		plt.legend( loc='best', ncol=1, shadow=True,
					fancybox=True, numpoints = 1)
		save_method(self.what)

class Resultado:
	
	def __init__(self, ins):
		self.ins = ins
		self.fmt = 'pdf'
		self.mapa_limites = [-5,5]

		self.rotas = []
		self.tempos = []
		for i in range(self.ins.m):
			self.rotas.append([])
			self.tempos.append([])

		self.instancia_path = self.ins.instancia_path
		self.instancia_name = path.split(self.instancia_path)[1].split('.')[0]

	def save_image_data(self, name):	
		fig_file_name = '{}.{}'.format(name, self.fmt)

		fig_file_path = self.instancia_path
		for i in range(3):
			fig_file_path = path.dirname(fig_file_path)
		fig_file_path = path.join(fig_file_path, 'resultados')
		fig_file_path = path.join(fig_file_path, self.instancia_name)

		if not path.isdir(fig_file_path):
			makedirs(fig_file_path)

		fig_file = path.join(fig_file_path,fig_file_name)
		try:
			plt.savefig(fig_file, bbox_inches = 'tight')
		except IOError:
			arg = (self.instancia_name,fig_file_name)
			print u'Arquivo {}/{} não salvo devido a IOError.'.format(*arg)
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
		if var == 'T':
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
		for id_vei, route in enumerate(self.rotas):
			G.add_edges_from(route)
			draw_networkx_edges(G, pos, edgelist = route, edge_color = colors[id_vei])
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
						 ['drops', 'picks', 'center'],
			             loc='best', ncol=1, shadow=True,
			             fancybox=True, numpoints = 1)
		leg.get_frame().set_alpha(0.5)
		
		self.save_image_data('requests')

	def plot_global_result_data(self):
		conn = connect('persistent_data.db')
		c = conn.cursor()

		t_requ_data = DataList(u"Instante desejado de atendimento", u"Número de pedidos", 25)
		for n_veh_plot in range(1,5):
			w_time_data = DataList(u"Tempo de espera {} veh".format(n_veh_plot), u"Número de pedidos", 25)
			t_time_data = DataList(u"Tempo de viagem {} veh".format(n_veh_plot), u"Número de pedidos", 25)

			for row in c.execute("SELECT * FROM specific_results"):
				n_req, n_veh, n_ins, req_id, opt, d_time, i_time, e_time = row
				if n_req != 0:
					t_requ_data[n_req].append(d_time)
					if n_veh == n_veh_plot:
						w_time_data[n_req].append(i_time - d_time)
						t_time_data[n_req].append(e_time - i_time)

			w_time_data.plot(self.save_image_data)
			t_time_data.plot(self.save_image_data)
		t_requ_data.plot(self.save_image_data)
		
		o_time_data = DataList(u"Tempo de processamento", u"Número de pedidos", 25, ' (s)', '', True, True)

		for row in c.execute("SELECT * FROM global_results"):
			n_req, runtime = row[0], row[8]
			if n_req != 0:
				o_time_data[n_req].append(runtime)

		o_time_data.plot(self.save_image_data)

		e_time_data = DataList(u"Espera", u"Instante desejado de atendimento", 50, '', '')

		for row in c.execute("SELECT * FROM specific_results"):
			n_req, n_veh, n_ins, req_id, opt, d_time, i_time, e_time = row
			if n_req != 0:
				e_time_data[int(d_time)].append(i_time - d_time)
		e_time_data.plot(self.save_image_data)

		conn.close()

	def result_data_DB(self, rtime, obj):
		req_data = self.ins.get_pos_requests()
		n_req, v_veh, n_ins = [int(x) for x in self.instancia_name.split('_')]
		opt = 1
		w_times = np.array([])
		t_times = np.array([])
		specific_data = []
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
			specific_data.append( (n_req, v_veh, n_ins, req[0], opt, desired_time, ini_time, end_time) )
		global_data = [(n_req, v_veh, n_ins, opt, w_times.mean(), w_times.std(), t_times.mean(), t_times.std(), rtime, obj)]

		conn = connect('persistent_data.db')
		c = conn.cursor()
		for data in global_data:
			c.execute(''' REPLACE INTO global_results VALUES (?,?,?,?,?,?,?,?,?,?)''', data)
		for data in specific_data:
			c.execute(''' REPLACE INTO specific_results VALUES (?,?,?,?,?,?,?,?)''', data)

		conn.commit()
		conn.close()






























