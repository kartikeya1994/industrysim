from random import random, normalvariate as n
import theano
import theano.tensor as T
import theano.tensor.nnet as nnet
import numpy as np
from adam import Adam
from copy import deepcopy

def weibull(eta, beta, age):
	import math
	b = age**beta
	a = (1.0/eta)**beta
	#log("b={} a={}".format(b,a))
	return int((b-math.log(1.0-random())/a)**(1.0/beta)-age)

def normal(mu=None, sigma=None, params=None):
	if params is not None:
		return int(n(params['mu'],params['sigma']))
	return max(1,int(n(mu, sigma)))

def log(msg):
	#print(msg)
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
	def __init__(self, dim_input, dim_hidden_layers, dim_output, do_dropout=False):
		# dim_hidden_layers in a list with ith element being no. of nodes in hidden layer i
		self.W = []
		self.B = []
		self.L2 = 0.0
		self.do_dropout = do_dropout
		self.layers = []
		self.testing = False
		self.X = T.dmatrix()
		self.Y = T.dmatrix() # reward times action vector
		self.num_machines = dim_output/3
		for i in range(len(dim_hidden_layers)+1):
			w = None
			b= None
			lyr = None
			if i==0:
				#inputs to first hidden layer
				w = theano.shared(np.array(np.random.rand(dim_input,dim_hidden_layers[0]), dtype=theano.config.floatX))
				b = theano.shared(np.array(np.random.rand(dim_hidden_layers[0]), dtype=theano.config.floatX))
				lyr = self.layer(self.X, w, b, dropout=do_dropout)
			elif i==len(dim_hidden_layers):
				#last hidden layer to output layer
				w = theano.shared(np.array(np.random.rand(dim_hidden_layers[i-1],dim_output), dtype=theano.config.floatX))
				b = theano.shared(np.array(np.random.rand(dim_output), dtype=theano.config.floatX))
				lyr = self.softmax_layer(self.layers[i-1], w, b) # output layer

			else:
				#hidden layer to hidden layer
				w = theano.shared(np.array(np.random.rand(dim_hidden_layers[i-1],dim_hidden_layers[i]), dtype=theano.config.floatX))
				b = theano.shared(np.array(np.random.rand(dim_hidden_layers[i]), dtype=theano.config.floatX))
				lyr = self.layer(self.layers[i-1],w,b, dropout=do_dropout)
			self.W.append(w)
			self.B.append(b)
			self.L2 += (w**2).sum() + (b**2).sum()
			self.layers.append(lyr)
		#cost equation
		#loss = T.sum(T.log(T.dot(self.layers[-1], self.Y.T)))#+ L1_reg*L1 + L2_reg*L2
		#loss = T.sum(self.layers[-1] - self.Y) + 0.0001*self.L2
		loss = T.sum(T.square(self.layers[-1]-self.Y)) #+ self.L2*0.00001
		
		updates = Adam(loss, self.W+self.B) #+ Adam(loss, self.B)
		
		#compile theano functions
		self.backprop = theano.function(inputs=[self.X, self.Y], outputs=loss, updates=updates)
		self.run_forward_batch = theano.function(inputs=[self.X], outputs=self.layers[-1])

	def layer(self, x, w, b, dropout=False):
		m = T.dot(x,w) + b
		h = nnet.relu(m)
		if dropout:
			return self.dropout(h)
		else:
			return h

	def softmax_layer(self, x, w, b):
		# last layer is softmax layer since it represents probabilities of actions to pick, and should sum to 1
		o = self.layer(x,w,b)#.reshape((2,))
		for i in range(0,self.num_machines,3):
			T.set_subtensor(o[i:i+3], T.nnet.softmax(o[i:i+3]))
		return o


	def dropout(self, layer):
		"""p is the probablity of dropping a unit
		"""
		p=0.5
		if self.testing:
			return layer*p
		else:
			rng = np.random.RandomState(99999)
			srng = theano.tensor.shared_randomstreams.RandomStreams(rng.randint(999999))
			# p=1-p because 1's indicate keep and p is prob of dropping
			mask = srng.binomial(n=1, p=1-p, size=layer.shape)
			# The cast is important because
			# int * float32 = float64 which pulls things off the gpu
			return layer * T.cast(mask, theano.config.floatX)


	def run_forward(self, state, testing=False):
		self.testing = testing
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

	def save(self, file_name='NN.pickle'):
		from six.moves import cPickle
		f = open(file_name, 'wb')
		cPickle.dump(self, f, protocol=cPickle.HIGHEST_PROTOCOL)
		f.close()

	@staticmethod
	def load(file_name='NN.pickle'):
		f = open(file_name, 'rb')
		NN = cPickle.load(f)
		f.close()
		return NN

	@staticmethod
	def clone(nn):
		#deepcopy passed object and return copy
		return deepcopy(nn)


	