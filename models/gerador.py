# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:19:23 2018

@author: Sergio P.
"""

import numpy as np
from json import dumps
from os import path, listdir

class Gerador():

	def __init__(self):
		self.n_requests = None
		self.map_range = [[0,0], [0,0]]
		self.time_horizon = None
		self.dp_rate = None
		self.data = {}
		self.data['static_data'] = {}
		self.data['requests'] = []

	def set_static_data(self, n_veh, q_veh, t_ser):
		self.data['static_data']['number_of_vehicles'] = n_veh
		self.data['static_data']['max_vehicle_capacity'] = q_veh
		self.data['static_data']['service_time'] = t_ser

	def set_requests_data(self, n_requests,
		                  x_range = [0,10], y_range = [0,10],
		                  time_horizon = 30,
		                  dp_rate = 0.5):
		self.n_requests = n_requests
		self.map_range = [x_range, y_range]
		self.time_horizon = time_horizon
		self.dp_rate = dp_rate

	def set_requests(self):
		self.data['requests'] = []

		def cap_array(array, rng):
			r = array
			for i, v in enumerate(array):
				if v > rng[1]:
					r[i] = rng[1]
				elif v < rng[0]:
					r[i] = rng[0]
			return r

		desired_times = np.random.poisson(8, self.n_requests)
		desired_times = cap_array(desired_times, [0, self.time_horizon])

		points_x = np.random.poisson(5, self.n_requests)
		points_x = cap_array(points_x, self.map_range[0])

		points_y = np.random.poisson(5, self.n_requests)
		points_y = cap_array(points_y, self.map_range[1])

		for i in range(self.n_requests):
			request = {}
			request['max_wait_time'] = 10
			request['max_ride_time'] = 100
			request['known_time'] = 0
			request['desired_time'] = desired_times[i]
			request['service_point_x'] = points_x[i]-5
			request['service_point_y'] = points_y[i]-5
			choice = np.random.random_sample()
			if choice >= self.dp_rate:
				request['service_type'] = 'pick'
			else:
				request['service_type'] = 'drop'
			self.data['requests'].append(request)

	def save_ins(self):        	
		n_req = str(self.n_requests).zfill(2)
		n_veh = str(self.data['static_data']['number_of_vehicles']).zfill(2)

		actual_path = path.dirname(path.abspath("__file__"))
		instancia_path = path.join(actual_path,'models\\instancias')
		ids = [0]
		for file in listdir(instancia_path):
			id_n_req, id_n_veh, id_ins = file.split('.')[0].split('_')
			if int(id_n_req) == self.n_requests:
				if int(id_n_veh) == self.data['static_data']['number_of_vehicles']:
					ids.append(int(id_ins))
		id_ins = str(max(ids)+1).zfill(3)

		name_file = '{}_{}_{}.json'.format(n_req,n_veh,id_ins)
		instancia_path = path.join(instancia_path,name_file)
		with open(instancia_path, 'w') as file:
			file.write(dumps(self.data, indent = 4, separators = (',', ': ')))
			file.close()

