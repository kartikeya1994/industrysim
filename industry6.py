"""
Description of industry and simulation parameters
"""
from entities import Policy, Machine, MaintenanceTask, EpochResult, PeriodicPolicy

epoch_length = 168
max_epochs=25
max_labor=[1,2,3]
wages = [2500, 1000, 500] # per epoch
num_machines = 6
state_size = num_machines*2+3#+4
action_size = num_machines*3
nn_arch = [10,4,4,4,4,4,4,4,10]

job_demand = {
	'mu':8.0,
	'sigma':2.0,
	'num':int(num_machines*epoch_length/15), 
	'due_after': {
		'mu':160.0,
		'sigma':10.0
	}
}
delay_penalty = 10
mt_fixed_cost = {
	'cm':1000,
	'high':400,
	'low':200
}
mt_RF = {
	'cm': 0.0,
	'high': 0.6,
	'low': 1.0
}
mt_ttr = {
	'cm': {
		'mu':70,
		'sigma':5
		},
	'high': {
		'mu':50,
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
machine_names = ['FnC1', 'Lathe1', 'Milling1', 'FnC2', 'Lathe2', 'Milling2', ]

mt_task1 = MaintenanceTask(eta=600.0, beta=beta, age=1000.0, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
mt_task2 = MaintenanceTask(eta=1500.0, beta=beta, age=1000.0, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
mt_task3 = MaintenanceTask(eta=3000.0, beta=beta, age=1000.0, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
mt_task4 = MaintenanceTask(eta=600.0, beta=beta, age=1000.0, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
mt_task5 = MaintenanceTask(eta=1500.0, beta=beta, age=1000.0, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
mt_task6 = MaintenanceTask(eta=3000.0, beta=beta, age=1000.0, fixed_cost=mt_fixed_cost, 
							RF=mt_RF, labor_req=mt_labor, ttr=mt_ttr)
machine1 = Machine(name='FnC1', compatible_jobs=compatible_jobs, maintenance_task=mt_task1, epoch_length=epoch_length)
machine2 = Machine(name='Lathe1', compatible_jobs=compatible_jobs, maintenance_task=mt_task2, epoch_length=epoch_length)
machine3 = Machine(name='Milling1', compatible_jobs={'A'}, maintenance_task=mt_task3, epoch_length=epoch_length)
machine4 = Machine(name='FnC2', compatible_jobs=compatible_jobs, maintenance_task=mt_task4, epoch_length=epoch_length)
machine5 = Machine(name='Lathe2', compatible_jobs=compatible_jobs, maintenance_task=mt_task5, epoch_length=epoch_length)
machine6 = Machine(name='Milling2', compatible_jobs={'A'}, maintenance_task=mt_task6, epoch_length=epoch_length)
