"""
Epoch (step) length: 7 days
Episode length: 6 months = 180 days
Variables that are input to neural network:

Job related (3 types of jobs)
- no. of jobs of each type
- avg due_afer of each job type
- setup time of each type
- due_after range of each job type
- avg penalty cost of each job type

Machine related (8 machines)
- Machine age for each machine
- Job types machine can produce (3 inputs) for each machine
- Cost of PM per machine (low alpha, high alpha)
- Cost of CM per machine

Maintenance Dept:
- No. of maintenance labour of each type(3 inputs)
- Wages per hour of each labour type

Actions: 
Job scheduling: SJF, EDF
Maintenance: 

"""

"""
Thoughts: 
Job scheduling is tricky. 
Need to know attributes of every job for desired scheduling

Makes sense to train two different networks?
One for job sched policy and other for maintenance?
"""

"""
Notes:
introduce feature in NN for unfinished maintenance job
"""

