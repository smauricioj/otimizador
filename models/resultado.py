# -*- coding: utf-8 -*-
"""
Created on Thu May 03 13:27:14 2018

@author: Sergio P.
"""
import matplotlib.pyplot as plt
from numpy import linspace
from networkx import DiGraph, draw_networkx_nodes, draw_networkx_edges, draw_networkx_labels
from os import path, makedirs
from math import cos, sin

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

	def save_data(self, name):	
		fig_file_name = '{}.{}'.format(name, self.fmt)

		instancia_path = self.ins.instancia_path
		instancia_name = path.split(instancia_path)[1].split('.')[0]

		fig_file_path = instancia_path
		for i in range(3):
			fig_file_path = path.dirname(fig_file_path)
		fig_file_path = path.join(fig_file_path, 'resultados')
		fig_file_path = path.join(fig_file_path, instancia_name)

		if not path.isdir(fig_file_path):
			makedirs(fig_file_path)

		fig_file = path.join(fig_file_path,fig_file_name)
		try:
			plt.savefig(fig_file, bbox_inches = 'tight')
		except IOError:
			arg = (instancia_name,fig_file_name)
			print u'Arquivo {}/{} não salvo devido a IOError.'.format(*arg)
		plt.clf()

	def addTrip(self, string):
		data = self.ins.get_pos_requests()

		index, value = string.split('=')
		var, tup = index[:-1].split('[')
		if var == 'T':
			i, k = [int(x) for x in tup.split(',')]
			self.tempos[k].append((i,float(value)))
		elif var == 'x' and float(value) == 1:
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

			for i, y_pos in enumerate(list(linspace(9,1,self.ins.n))):
				pos[visitas[i]] = [4, y_pos]
				pos[visitas[i]+self.ins.n] = [6, y_pos]

		G.add_nodes_from(range((2 * self.ins.n)+2))
		draw_networkx_nodes(G, pos, ax = ax)
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
		plt.grid(True)
		self.save_data('routes')

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
		
		self.save_data('requests')
