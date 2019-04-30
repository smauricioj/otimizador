# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:19:23 2018

@author: Sergio P.
"""

import numpy as np
from json import dumps
from os import path, listdir
import matplotlib.pyplot as plt

class Gerador():

	def __init__(self, conf):
		self.conf = conf
		self.map_center = conf['gerador_data']['map_center']
		self.total_time = conf['gerador_data']['total_time']
		self.priori_ratio = conf['gerador_data']['priori_ratio']
		self.dp_ratio = conf['gerador_data']['dp_ratio']

		self.data = {}
		self.data['static_data'] = {}
		self.data['requests'] = []

	def set_data(self, n_total_requests, n_veh, q_veh, t_ser):
		self.n_total_requests = n_total_requests
		self.n_drop_requests = int(round(self.dp_ratio*n_total_requests))
		self.n_pick_requests = n_total_requests - self.n_drop_requests
		self.data['static_data']['number_of_vehicles'] = n_veh
		self.data['static_data']['max_vehicle_capacity'] = q_veh
		self.data['static_data']['service_time'] = t_ser
		self.data['static_data']['total_time'] = self.total_time
		self.data['static_data']['priori_ratio'] = self.priori_ratio
		self.data['static_data']['dp_ratio'] = self.dp_ratio

		def get_requests_by_service_type(self, service_type):

			if service_type == 'pick':
				n_requests = self.n_pick_requests
			else:
				n_requests = self.n_drop_requests

			central_point = True
			while central_point:
				points = np.random.multivariate_normal(mean = self.map_center,
					                                   cov = [[self.map_center[0], 0],
					                                          [0, self.map_center[1]]],
					                                   size = n_requests)
				if self.map_center not in points:
					central_point = False
			points = np.reshape(points, (2, n_requests))

			inside = False
			rate_requests = (float(self.total_time)/n_requests)*0.85 #menor pra garantir o caber dos pedidos no tempo
			while not inside:
				desired_times = np.cumsum(np.random.poisson(rate_requests, n_requests))
				if service_type == 'pick':
					distance = 0
				else:
					distance = np.sqrt( (points[0][-1]**2)+(points[1][-1]**2) )
				if desired_times[-1] + distance <= self.total_time:
					inside = True

			known_times = np.random.normal(2, 1, n_requests)
			known_times = [max(0,a) for a in known_times]
			known_times = desired_times - known_times
			known_times = [round(max(0,a),2) for a in known_times]

			for i in range(n_requests):
				request = {}
				request['max_wait_time'] = 10
				request['max_ride_time'] = 100
				request['known_time'] = np.random.choice([known_times[i],0], p = [1-self.priori_ratio,self.priori_ratio])
				request['desired_time'] = desired_times[i]
				request['service_point_x'] = round(points[0][i] - self.map_center[0], 1)
				request['service_point_y'] = round(points[1][i] - self.map_center[1], 1)
				request['service_type'] = service_type
				self.data['requests'].append(request)

			return desired_times, known_times

		dt_p, kt_p = get_requests_by_service_type(self, 'pick')
		dt_d, kt_d = get_requests_by_service_type(self, 'drop')
		
		self.data['requests'] = sorted(self.data['requests'], key = lambda k: k['known_time'])

		dt = np.append(dt_p, dt_d)
		kt = np.append(kt_p, kt_d)
		urgency_mean = np.mean(dt - kt)
		urgency_std = np.std(dt - kt)

		self.data['static_data']['urgency_mean'] = round(urgency_mean, 2)
		self.data['static_data']['urgency_std'] = round(urgency_std, 2)

		kt = sorted(kt)
		delta = [ float(a_j - a_i) for a_i, a_j in zip(kt, kt[1:]) ]
		tau = self.total_time/float(self.n_total_requests)
		sigma, sigma_c = [], []
		for i, delta_i in enumerate(delta):
			sigma_c_i = tau
			if delta_i < tau:
				if i == 0:
					sigma_i = tau - delta_i
				elif i > 0:
					sigma_i = tau - delta_i + (delta[i-1]*(tau - delta_i))/tau
					sigma_c_i += (delta[i-1]*(tau - delta_i))/tau
			else:
				sigma_i = 0
			sigma.append(sigma_i)
			sigma_c.append(sigma_c_i)
		dynamism = 1 - (np.cumsum(sigma)[-1]/np.cumsum(sigma_c)[-1])

		self.data['static_data']['dynamism'] = round(dynamism, 2)

	def save_ins(self):        	
		n_req = str(self.n_total_requests).zfill(2)
		n_veh = str(self.data['static_data']['number_of_vehicles']).zfill(2)

		instancia_path = self.conf['instancia_path']
		ids = [0]
		for file in listdir(instancia_path):
			if path.isfile(path.join(instancia_path,file)):
				id_n_req, id_n_veh, id_ins = file.split('.')[0].split('_')
				if int(id_n_req) == self.n_total_requests:
					if int(id_n_veh) == self.data['static_data']['number_of_vehicles']:
						ids.append(int(id_ins))
		id_ins = str(max(ids)+1).zfill(3)

		name_file = '{}_{}_{}.json'.format(n_req,n_veh,id_ins)
		instancia_path = path.join(instancia_path,name_file)
		with open(instancia_path, 'w') as file:
			file.write(dumps(self.data, indent = 4, separators = (',', ': ')))
			file.close()

