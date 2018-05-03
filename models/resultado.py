# -*- coding: utf-8 -*-
"""
Created on Thu May 03 13:27:14 2018

@author: Sergio P.
"""
import matplotlib.pyplot as plt
from os import path, makedirs

class Resultado:

	def __init__(self, ins):
		# n, m, Q   = ins.n, ins.m, ins.Q
		# q, s, t   = ins.get_q(), ins.get_s(), ins.get_t()
		# W, R, tau = ins.get_W(), ins.get_R(), ins.get_tau()
		# custo, arcos = tau, tau.keys()    
		# origens, destinos, locais = ins.get_O(), ins.get_D(), ins.get_V()
		# veiculos = ins.get_K()
		self.ins = ins
		self.fmt = 'pdf'

	def save_data(self, name):	
		fig_file_name = '{}.{}'.format(name, self.fmt)

		instancia_path = self.ins.instancia_path
		instancia_name = path.split(instancia_path)[1].split('.')[0]

		fig_file_path = instancia_path
		for i in range(3):
			fig_file_path = path.dirname(fig_file_path)
		fig_file_path = path.join(fig_file_path,'resultados')
		fig_file_path = path.join(fig_file_path,instancia_name)
		if not path.isdir(fig_file_path):
			makedirs(fig_file_path)

		fig_file = path.join(fig_file_path,fig_file_name)
		plt.savefig(fig_file, bbox_inches = 'tight')
		plt.clf()

	def fig_requests(self):
		data = self.ins.get_pos_requests()
		fig, ax = plt.subplots()
		ax.plot(0, 0, 'g*', markersize=15)
		for d in data:
			if d[3] == 'drop':
				fmt = 'bo'
			else:
				fmt = 'ro'
			ax.plot(d[1], d[2], fmt)

		limites = [(5,6),(-6,-5)]
		for limite in limites:
			plt.axvspan(limite[0], limite[1], facecolor = '#cecece', alpha = 0.5)
			plt.axhspan(limite[0], limite[1], facecolor = '#cecece', alpha = 0.5)

		ticks = range(-6,7,1)
		ax.set_xticks(ticks)
		ax.set_yticks(ticks)
		plt.grid(True)
		
		self.save_data('requests')
			
