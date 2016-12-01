epoch_length = 168
max_epochs=10
max_labor=[1,2,2]
num_machines = 1
job_demand = {
	'mu':17,
	'sigma':10,
	'num':num_machines*epoch_length/17, 
	'due_after': {
		'mu':160,
		'sigma':100
	}
}
delay_penalty = 10
cm_cost = 1000
low_cost = 100
high_cost = 400

eta, beta, age, fixed_cost, RF, labor, ttf
