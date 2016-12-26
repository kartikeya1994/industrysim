from entities import Policy, Machine, MaintenanceTask, EpochResult, PeriodicPolicy
from engine import IndustrySim
from tools import e_greedy, NN
import numpy as np
import time
from industry import epoch_length, max_epochs, max_labor, wages, num_machines, job_demand
from industry import delay_penalty, mt_fixed_cost, mt_RF, mt_ttr, mt_labor, beta, age
from industry import compatible_jobs, machine_names, mt_task1, mt_task2, mt_task3
from industry import machine1, machine2, machine3

env = IndustrySim(machines=[machine1, machine2, machine3], epoch_length=epoch_length, max_labor=max_labor,
					wages=wages, job_demand=job_demand, delay_penalty=delay_penalty)
start = time.time()
env.reset()
res = EpochResult(None, None, None)

experiments = 300
start = time.time()
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
for exp in range(experiments):
	pp = PeriodicPolicy(machine_names=machine_names, epoch_interval=5)
	for i in range(max_epochs):
		epoch_result = env.run_epoch(pp.get_policy())
	res = env.get_result()
	print(res)
	avg_obj += res.objfun
	for mr in res.machine_results:
		high_jobs[mr.name] += mr.mt_jobs_done['high']
		low_jobs[mr.name] += mr.mt_jobs_done['low']
	env.reset()
avg_obj/=experiments
print('Avg obj: '+ str(avg_obj))
print('Total high: '+str(high_jobs))
print('Total low: '+ str(low_jobs))
print('Took '+str(time.time()-start)+'s')