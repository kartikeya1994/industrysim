from entities import Policy, Machine, MaintenanceTask, EpochResult
from engine import IndustrySim
from tools import e_greedy, NN
import numpy as np
import time
from industry import epoch_length, max_epochs, max_labor, wages, num_machines, job_demand
from industry import delay_penalty, mt_fixed_cost, mt_RF, mt_ttr, mt_labor, beta, age
from industry import compatible_jobs, machine_names, mt_task1, mt_task2, mt_task3
from industry import machine1, machine2, machine3, machine5, machine4, machine6
from industry import state_size, action_size, nn_arch

from multiprocessing.dummy import Pool as ThreadPool

def thread_task(t):
	epoch_result, state = t.run_epoch()
	objfun =  epoch_result.get_objfun()
	return objfun

# function to be mapped over
def simulateParallel(tasks, threads=4):
	pool = ThreadPool(threads)
	results = pool.map(thread_task, tasks)
	pool.close()
	pool.join()
	return np.mean(results)

"""
State consists of (in order):
machine params:
	pending jobs in last epoch
	machine age
last epoch params:
	free labour
next epoch demand:
	avg due after
delay penalty

reward = objfun, cost

"""
env = IndustrySim(machines=[machine1,machine2, machine3, machine4, machine5, machine6], epoch_length=epoch_length, max_labor=max_labor,
					wages=wages, job_demand=job_demand, delay_penalty=delay_penalty, state_size=state_size)
start = time.time()
env.reset()
res = EpochResult(None, None, None)

nn = NN(dim_input=state_size, dim_hidden_layers=nn_arch, dim_output=action_size, do_dropout=True)

states = np.zeros((max_epochs, state_size))
actions = np.zeros((max_epochs, action_size))
rewards = np.zeros(max_epochs)
state = np.zeros(state_size)

# hyper params
e = 0.2
training_passes = 20000
start = time.time()

#par = [NN.clone(env), NN.clone(env)]#, (NN.clone(env), pm_plan)]

for exp in range(training_passes):
	print('Training Pass: {}'.format(exp))
	for i in range(max_epochs):
		pm_probs = nn.run_forward(state)
		pm_plan, action_vector = e_greedy(machine_names, pm_probs, e=e)
		#print(pm_plan)
		states[i] = state
		actions[i] = action_vector
		pol = Policy('SJF', pm_plan)
		# for p in par:
		# 	p.set(env)
		# 	p.set_policy(pol)
		#par_objfun = simulateParallel(par)
		epoch_result, state = env.run_epoch(pol)#{}))#{'FnC1':'HIGH', 'Lathe':'HIGH'}))#pm_plan))
		# print(epoch_result)
		rewards[i] = (epoch_result.get_objfun())#+par_objfun)/2.0
	returns = nn.get_returns(rewards, actions)
	nn.backprop(states, returns)
	res = env.get_result()
	#print(res)
	env.reset()
print('Training took '+str(time.time()-start)+'s')

validation = 200
avg_obj = 0
# high_jobs = {
# 	'FnC1':0,
# 	'Lathe':0,
# 	'Milling':0
# }
# low_jobs = {
# 	'FnC1':0,
# 	'Lathe':0,
# 	'Milling':0
# }

high_jobs = {
	'FnC1':0,
	'Lathe1':0,
	'Milling1':0,
	'FnC2':0,
	'Lathe2':0,
	'Milling2':0
}
low_jobs = {
	'FnC1':0,
	'Lathe1':0,
	'Milling1':0,
	'FnC2':0,
	'Lathe2':0,
	'Milling2':0
}

for exp in range(validation):
	for i in range(max_epochs):
		pm_probs = nn.run_forward(state, testing=True)
		pm_plan, action_vector = e_greedy(machine_names, pm_probs,e=None)
		#print(pm_plan)
		states[i] = state
		actions[i] = action_vector
		epoch_result, state = env.run_epoch(Policy('SJF', pm_plan))
	res = env.get_result()
	print(res)
	avg_obj += res.objfun
	for mr in res.machine_results:
		high_jobs[mr.name] += mr.mt_jobs_done['high']
		low_jobs[mr.name] += mr.mt_jobs_done['low']
	env.reset()
avg_obj/=validation
print('Avg obj: '+ str(avg_obj))
print('Total high: '+str(high_jobs))
print('Total low: '+ str(low_jobs))
print('Took '+str(time.time()-start)+'s')
nn.save(filename='NN.pickle')