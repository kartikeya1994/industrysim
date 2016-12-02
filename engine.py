from tools import log, normal
import operator
import heapq
from entities import EpochResult, Job
class IndustrySim:
	def __init__(self, machines=None, epoch_length=None, max_labor=None,
					wages=None, job_demand=None, delay_penalty=None, policy=None):
		self.machines = machines
		self.epoch_length = epoch_length
		self.max_labor = max_labor
		self.wages = wages
		self.job_demand = job_demand
		self.delay_penalty = delay_penalty
		self.policy = policy

		self.epoch = 0
		self.curr_labor = list(self.max_labor)

		self.time=0

	def reset(self):
		self.epoch = 0
		self.curr_labor = list(self.max_labor)

		for m in self.machines:
			m.init_totals()
			m.init_vars()

	def init_next_epoch(self):
		self.time = 0
		self.epoch += 1
		machine_results = []
		for m in self.machines:
			result = m.init_next_epoch()
			machine_results.append(result)
		labor_cost = 0
		for i in range(len(self.wages)):
			labor_cost += self.wages[i]*self.max_labor[i]
		return EpochResult(self.epoch, machine_results, labor_cost)

	def get_new_jobs(self):
		new_jobs = []
		for i in range(self.job_demand['num']):
			j = Job('JOB', normal(self.job_demand['mu'],self.job_demand['sigma']), due_after=normal(self.job_demand['due_after']['mu'],self.job_demand['due_after']['sigma']), job_subtype='A')
			new_jobs.append(j)
		return new_jobs

	def release_labor(self, labor):
		for i in range(len(self.curr_labor)):
			self.curr_labor[i] += labor[i]

	def attempt_maintenance(self, machine):
		#attempt to start maintenance
		if machine.labor_req_met(self.curr_labor): #requirement met, begin maintenance
			# reserve labor of front job of machine
			machine.adjust_start_times(self.time)
			req = machine.labor_req()
			for i in range(len(self.curr_labor)):
				self.curr_labor[i] -= req[i]
			self.decrement_front_job(machine)
		else:
			machine.set_status('WAITING')
			machine.time_spent['waiting'] += 1

	def run_epoch(self, policy=None):
		#input: policy to run epoch by
		#returns: EpochResult object that contains variables describing the state at end of epoch
		if policy is not None:
			self.policy = policy

		log('Epoch: '+str(self.epoch))

		self.plan_epoch() #create job scheduling for each machine, incorporate PM, and evaluate breakdowns (CMs)

		self.simulate_epoch()

		return self.init_next_epoch()
		

	def plan_epoch(self):
		# schedule jobs and PM onto machines for one epoch
		new_jobs = self.get_new_jobs() #TODO: job subtypes

		#add pending jobs from previous epoch
		for m in self.machines:
			new_jobs += m.get_leftover_jobs()

		#sort jobs depending upon policy
		if self.policy.job_sched == 'SJF':
			new_jobs.sort(key=operator.attrgetter('proc_time'),reverse=True)
		elif self.policy.job_sched == 'EDF':
			new_jobs.sort(key=operator.attrgetter('due_after'),reverse=True)

		#add jobs equally to each machine that is compatible with the job
		heapq.heapify(self.machines) # length of job queue is comparator
		while new_jobs:
			j = new_jobs.pop()

			#find machine with least queue length that is compatible with j
			popped_machines = []
			m = heapq.heappop(self.machines)
			while j.job_subtype not in m.compatible_jobs:
				popped_machines.append(m)
				m = heapq.heappop(self.machines)

			m.add_job(j)

			# re-add popped machines to machine list
			heapq.heappush(self.machines,m)
			while popped_machines:

				m = popped_machines.pop()
				heapq.heappush(self.machines, m)

		# add PM jobs
		end_of_last_pm = 0
		perform_pm = self.policy.pm_plan.keys()
		for m in self.machines:
			if m.name in perform_pm:
				if end_of_last_pm < self.epoch_length:
					end_of_last_pm = m.add_job(self.policy.pm_plan[m.name], after=end_of_last_pm)
					m.maintenance_task.pm_scheduled = True
			m.evaluate_breakdowns()

		for m in self.machines:
			log('Age: '+str(m.maintenance_task.age)+', Schedule: '+str(m.job_queue))

	def simulate_epoch(self):
		while self.time < self.epoch_length:
			# check for events at each machine at this time instance
			for m in self.machines:
				if len(m.job_queue) == 0 or m.front_start_time() > self.time:
					# no more jobs, or job starts later
					m.set_status('IDLE')
					m.time_spent['idle'] += 1

				elif m.front_job_type() == 'JOB' or m.front_started():
					self.decrement_front_job(m)

				elif m.front_job_type() == 'PM'  or m.front_job_type() == 'CM':
					self.attempt_maintenance(m)
				
				else:
					raise Exception('No if-elif block satisfied while evaluating front job')
			self.time += 1

	def decrement_front_job(self, machine):
		result = machine.decrement_front_job(self.time, self.delay_penalty)
		if result is not None:
			#result is not None if maintenance job is finished
			#result contains labor req of job that is done
			self.release_labor(result)