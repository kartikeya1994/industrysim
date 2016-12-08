from random import random
import theano
import theano.tensor as T
import theano.tensor.nnet as nnet
import numpy as np
from adam import Adam
def weibull(eta, beta, age):
	from random import random
	import math
	b = age**beta
	a = (1/eta)**beta
	return int((b-math.log(1.0-random())/a)**(1.0/beta)-age)

def normal(mu=None, sigma=None, params=None):
	from random import normalvariate as n
	if params is not None:
		return int(n(params['mu'],params['sigma']))
	return max(1,int(n(mu, sigma)))

def log(msg):
	print(msg)
	pass

def e_greedy(machine_names, action_probs, e=None):
	# select best action with probability 1-e
	# else select random action with probability e
	# e = None - return action with best prob
	# return pm_plan, one hot vector for pm plan of each machine
	pm_plan = {}
	one_hot = np.zeros(len(action_probs))
	for i in range(0,len(action_probs), 3):
		arg_max = None
		if e is None or random() > e:
			arg_max = np.argmax(action_probs[i:i+3])
		else: # pick random action
			arg_max = int(random()*3)
		one_hot[i+arg_max] = 1
		if arg_max == 0:
			pm_plan[machine_names[i/3]] = 'HIGH'
		elif arg_max == 1:
			pm_plan[machine_names[i/3]] = 'LOW'
	return pm_plan, one_hot

class NN: #TODO update softmax layer
	def __init__(self, dim_input, dim_hidden_layers, dim_output):
		# dim_hidden_layers in a list with ith element being no. of nodes in hidden layer i
		self.W = []
		self.B = []
		self.layers = []
		self.X = T.dmatrix()
		self.Y = T.dmatrix() # reward times action vector
		for i in range(len(dim_hidden_layers)+1):
			w = None
			lyr = None
			if i==0:
				w = theano.shared(np.array(np.random.rand(dim_input,dim_hidden_layers[0]), dtype=theano.config.floatX))
				b = theano.shared(np.zeros((dim_hidden_layers[0],), dtype=theano.config.floatX))
				lyr = self.layer(self.X, w, b)
			elif i==len(dim_hidden_layers):
				w = theano.shared(np.array(np.random.rand(dim_hidden_layers[i-1],dim_output), dtype=theano.config.floatX))
				b = theano.shared(np.zeros((dim_output,), dtype=theano.config.floatX))
				lyr = self.softmax_layer(self.layers[i-1], w, b) # output layer

			else:
				w = theano.shared(np.array(np.random.rand(dim_hidden_layers[i-1],dim_hidden_layers[i]), dtype=theano.config.floatX))
				b = theano.shared(np.zeros((dim_hidden_layers[i],), dtype=theano.config.floatX))
				lyr = self.layer(self.layers[i-1],w,b)
			self.W.append(w)
			self.B.append(b)
			self.layers.append(lyr)
		#cost equation
		loss = T.sum(T.log(T.dot(self.layers[-1],-self.Y.T)))#+ L1_reg*L1 + L2_reg*L2
		#loss = self.layers[-1] - self.Y
		#loss = T.sum(T.square(self.layers[-1]-self.Y))#+ L1_reg*L1 + L2_reg*L2
		
		updates = Adam(loss, self.W+self.B) #+ Adam(loss, self.B)
		
		#compile theano functions
		self.backprop = theano.function(inputs=[self.X, self.Y], outputs=loss, updates=updates)
		self.run_forward_batch = theano.function(inputs=[self.X], outputs=self.layers[-1])

	def layer(self, x, w, b):
		m = T.dot(x,w) + b
		h = nnet.sigmoid(m)
		return h

	def softmax_layer(self, x, w, b):
		# last layer is softmax layer since it represents probabilities of actions to pick, and should sum to 1
		return T.nnet.softmax(self.layer(x,w,b))#.reshape((2,))

	def run_forward(self, state):
		return self.run_forward_batch([state])[0]

	def get_returns(self, rewards, actions, discount=0.97):
		# calculate discounted return for each step
		for i in range(len(rewards)):  
			ret = 0
			future_steps = len(rewards) - i
			decrease = 1
			for j in xrange(future_steps):
				ret += rewards[i+j]*decrease
				decrease *= discount
				rewards[i] = ret
		return actions* rewards[:, np.newaxis]
	