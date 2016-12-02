# industrysim

WIP: A simple Open-AI-Gym-like sandbox for training algorithms for integrated scheduling of jobs and maintenance in a job-shop industry.

Include `entities.py`, `engine.py` and `tools.py` in your source folder.

```
from engine import IndustrySim

#initialize
env = IndustrySim(params)

#run one epoch
epoch_result = env.run_epoch(policy)

#reset to init state
env.reset()
```

Check out `example.py` for description of simulation parameters for a simple one machine case. 

Dependencies: `terminaltable` for tablular output. Install with `pip`.
   
