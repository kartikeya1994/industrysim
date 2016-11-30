from tools import log
import operator
import heapq
class Simulator:
	def __init__(self, machines, policy, epoch_length, max_epochs, max_labor):
		self.machines = machines
		self.policy = policy
		self.epoch_length = epoch_length
		self.max_epochs = max_epochs
		self.max_labor = max_labor
		
		self.init_variables()

	def init_variables(self):
		self.pending_jobs = []
		self.time = 0
		self.epoch = 0
		self.curr_labor = self.max_labor

		for m in self.machines:
			m.total_reset()

	def reset(self, machines=None, policy=None, epoch_length=None, max_epochs=None):
		log('Reset')
		if machines is not None:
			self.machines = machines
		if policy is not None:
			self.policy = policy
		if epoch_length is not None:
			self.epoch_length = epoch_length
		if max_epochs is not None:
			self.max_epochs = max_epochs

		self.init_variables()

	def run_epoch(self, policy=None):
		#input: policy to run epoch by
		#returns: EpochResult object that contains variables describing the state at end of epoch
		if policy is not None:
			self.policy = policy

		self.plan_epoch() #create job scheduling for each machine, incorporate PM, and evaluate breakdowns (CMs)

		for time in range(self.epoch_length):
			# check for events at each machine at this time instance
			for m in self.machines:
				if len(m.job_queue) == 0 or m.front_start_time() > time:
					# no more jobs, or job starts later
					m.state = 'IDLE'
				elif m.front_start_time() < time: # job has already been started
					if m.job_queue.jobs[0].job_type == 'JOB':
						m.decrement_front_job()
					if m.front_job_type() == 'PM' or m.front_job_type() == 'CM':
						if m.waiting:
							#check if labor is available
							if m.labor_req_front() satisfies self.curr_labor: #TODO
								m.state = m.front_job_type()
								m.decrement_front_job()
						else:
							# decrement remaining job time
							m.decrement_front_job()
					if m.front_job_proc_time() == 0:
						#job is finished
						m.front_job_done() # TODO
				elif m.front_start_time() == time:
					if m.front_job_type() == 'JOB':
						m.state = 'JOB'
						m.decrement_front_job()
					if m.front_job_type() == 'PM'  or m.front_job_type() == 'CM':
						if m.labor_req_front() satisfies self.curr_labor: #TODO
							m.state = m.front_job_type()
							m.decrement_front_job()
						else:
							#wait
							m.state = 'WAIT'
				else:
					raise Exception('No if-elif block satisfied')

	def plan_epoch(self):
		# schedule jobs and PM onto machines for one epoch
		new_jobs = self.get_new_jobs() #TODO: get jobs required to produce this epoch

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

			# readd popped machines to machine list
			heapq.heappush(self.machines,m)
			while popped_machines:
				m = popped_machines.pop()
				heapq.heappush(self.machines, m)

		# add PM jobs
		end_of_last_pm = 0
		perform_pm = self.policy.pm_plan.keys()
		for m in self.machines:
			if m.name in perform_pm:
				ret_val = m.add_job(perform_pm[name], after=end_of_last_pm)
				if ret_val is not None:
					end_of_last_pm = ret_val
					m.maintenance_task.pm_scheduled = True



