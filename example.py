from entities import Policy, Machine, MaintenanceTask
from engine import IndustrySim
import time

#define simulation parameters for 1 machine case
epoch_length = 168
max_epochs=100
max_labor=[1,2,3]
wages = [2500, 1000, 500] # per epoch
num_machines = 1
job_demand = {
	'mu':8.0,
	'sigma':2.0,
	'num':int(num_machines*epoch_length/9), 
	'due_after': {
		'mu':160.0,
		'sigma':100.0
	}
}
delay_penalty = 10
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

eta = 1000.0
beta = 2.0
age = 0.0

name = 'FnC1'
compatible_jobs = {'A', 'B'}
pm_plan={'FnC1':'HIGH'}

mt_task = MaintenanceTask(eta=eta, beta=beta, age=age, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
machine = Machine(name=name, compatible_jobs=compatible_jobs, maintenance_task=mt_task, epoch_length=epoch_length)

policy = Policy('SJF', pm_plan)

env = IndustrySim(machines=[machine], epoch_length=epoch_length, max_labor=max_labor,
					wages=wages, job_demand=job_demand, delay_penalty=delay_penalty)

#begin simulation
for i in range(max_epochs):
	epoch_result = env.run_epoch(policy=policy)
	print(str(epoch_result))
	print('')