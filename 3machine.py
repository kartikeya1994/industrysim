from entities import Policy, Machine, MaintenanceTask, EpochResult
from engine import IndustrySim
from tools import e_greedy, NN
import numpy as np
import time

# from multiprocessing.dummy import Pool as ThreadPool

# def thread_task(t):
# 	global max_epochs, env, policy
# 	for i in range(max_epochs):
# 		epoch_result = env.run_epoch(policy)
# 	result = env.get_result()
# 	env.reset()
# 	return result

# # function to be mapped over
# def calculateParallel(tasks, threads=4):
# 	pool = ThreadPool(threads)
# 	results = pool.map(thread_task, tasks)
# 	pool.close()
# 	pool.join()
# 	return results

# def evaluate(policy, sim_count=1000):
# 	global max_epochs, env
# 	env.reset()
# 	res = EpochResult(None, None, None)
# 	#for exp in range(sim_count):
# 	tasks = list(xrange(sim_count))
# 	task_res = calculateParallel(tasks)
# 	for t in task_res:
# 		res += t
# 	return res

epoch_length = 168
max_epochs=25
max_labor=[1,2,3]
wages = [2500, 1000, 500] # per epoch
num_machines = 3
job_demand = {
	'mu':8.0,
	'sigma':2.0,
	'num':int(num_machines*epoch_length/15), 
	'due_after': {
		'mu':160.0,
		'sigma':100.0
	}
}
delay_penalty = 5
mt_fixed_cost = {
	'cm':1000,
	'high':400,
	'low':200
}
mt_RF = {
	'cm': 0,
	'high': 0.6,
	'low': 0.2
}
mt_ttr = {
	'cm': {
		'mu':70,
		'sigma':5
		},
	'high': {
		'mu':70,
		'sigma':5
		},
	'low':{
		'mu':15,
		'sigma':1
	}
}
mt_labor = {
	'cm':[1,2,2],
	'high':[1,1,2],
	'low':[0,1,1]
}

beta = 2.0
age = 0.0
compatible_jobs = {'A', 'B'}
machine_names = ['FnC1', 'Lathe', 'Milling']

mt_task1 = MaintenanceTask(eta=300, beta=beta, age=age, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
mt_task2 = MaintenanceTask(eta=300.0, beta=beta, age=1000.0, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
mt_task3 = MaintenanceTask(eta=5000.0, beta=beta, age=1000.0, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
machine1 = Machine(name='FnC1', compatible_jobs=compatible_jobs, maintenance_task=mt_task1, epoch_length=epoch_length)
machine2 = Machine(name='Lathe', compatible_jobs=compatible_jobs, maintenance_task=mt_task2, epoch_length=epoch_length)
machine3 = Machine(name='Milling', compatible_jobs=compatible_jobs, maintenance_task=mt_task3, epoch_length=epoch_length)

"""
State consists of (in order):
machine params:
	pending jobs in last epoch
	machine age
last epoch params:
	free labour
next epoch demand:
	avg due after

reward = objfun, cost

"""
state_size = num_machines*2+4
action_size = num_machines*3
env = IndustrySim(machines=[machine1,machine2, machine3], epoch_length=epoch_length, max_labor=max_labor,
					wages=wages, job_demand=job_demand, delay_penalty=delay_penalty, state_size=state_size)
start = time.time()
env.reset()
res = EpochResult(None, None, None)

nn = NN(dim_input=state_size, dim_hidden_layers=[10,10,10,10], dim_output=action_size, do_dropout=True)

states = np.zeros((max_epochs, state_size))
actions = np.zeros((max_epochs, action_size))
rewards = np.zeros(max_epochs)
state = np.zeros(state_size)

# hyper params
e = 0.1
training_passes = 2000
start = time.time()
for exp in range(training_passes):
	print('Experiment: {}'.format(exp))
	for i in range(max_epochs):
		pm_probs = nn.run_forward(state)
		pm_plan, action_vector = e_greedy(machine_names, pm_probs, e=e)
		#print(pm_plan)
		states[i] = state
		actions[i] = action_vector
		epoch_result, state = env.run_epoch(Policy('SJF', pm_plan))#{}))#{'FnC1':'HIGH', 'Lathe':'HIGH'}))#pm_plan))
		# print(epoch_result)
		rewards[i] = epoch_result.get_objfun()
		returns = nn.get_returns(rewards, actions)
		nn.backprop(states, returns)
	res = env.get_result()
	#print(res)
	env.reset()
print('Training took '+str(time.time()-start)+'s')

validation = 200
avg_obj = 0
high_jobs = {
	'FnC1':0,
	'Lathe':0,
	'Milling':0
}
low_jobs = {
	'FnC1':0,
	'Lathe':0,
	'Milling':0
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