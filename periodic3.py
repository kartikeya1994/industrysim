from entities import Policy, Machine, MaintenanceTask, EpochResult, PeriodicPolicy
from engine import IndustrySim
from tools import e_greedy, NN
import numpy as np
import time

epoch_length = 168
max_epochs=25
max_labor=[1,2,3]
wages = [2500, 1000, 500] # per epoch
num_machines = 3
state_size = num_machines*2+4
action_size = num_machines*3
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
		'mu':30,
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

env = IndustrySim(machines=[machine1, machine2, machine3], epoch_length=epoch_length, max_labor=max_labor,
					wages=wages, job_demand=job_demand, delay_penalty=delay_penalty)
start = time.time()
env.reset()
res = EpochResult(None, None, None)

experiments = 300
start = time.time()
avg_obj = 0
for exp in range(experiments):
	pp = PeriodicPolicy(epoch_interval=5, pm_plan={'FnC1':'HIGH', 'Lathe':'HIGH', 'Milling':'HIGH'})
	for i in range(max_epochs):
		epoch_result = env.run_epoch(pp.get_policy())
	res = env.get_result()
	#print(res)
	avg_obj += res.objfun
	env.reset()
avg_obj/=experiments
print('Avg obj: '+ str(avg_obj))
print('Took '+str(time.time()-start)+'s')