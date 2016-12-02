def weibull(eta, beta, age):
	from random import random
	import math
	b = age**beta
	a = (1/eta)**beta
	#return b-Math.log(1-Math.random())/a, (1/p)-t0;
	return int((b-math.log(1.0-random())/a)**(1.0/beta)-age)

def normal(mu=None, sigma=None, params=None):
	from random import normalvariate as n
	if params is not None:
		return int(n(params['mu'],params['sigma']))
	return max(1,int(n(mu, sigma)))

def log(msg):
	print(msg)