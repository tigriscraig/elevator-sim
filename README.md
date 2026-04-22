# elevator project

## problem statement

- Provide code that simulates an elevator. You are free to use any language.
- Upload the completed project to GitHub (public) for discussion during interview.
- Document all assumptions and any features that weren’t implemented.
- The result should be an executable, or script, that can be run with the following inputs and generate the following outputs.

     Inputs: [list of floors to visit] (e.g. elevator start=12 floor=2,9,1,32)
     Outputs: [total travel time, floors visited in order] (e.g. 560 12,2,9,1,32)
     Program Constants: Single floor travel time: 10


## usage

### setup

install python3
install pip
pip install pytest


### running the tests

```
pytest
```

### Run the simulator

Elevator.py takes input lines from standard input and writes lines to standard out.

```
python elevator.py < in.txt > out.txt
```

input
```
[start floor] [comma separated floors to visit]
````

output
```
[total time] [comma separated floors visited]
```

## design discussion

### approach

possible options for what to show in project

- readability of code (yes)
- testability (yes)
- clean design/expandability (yes)
- visualization (maybe, but only as an optional playground for ai-coding)
- knowledge of specific language(s) (maybe, python relevant and good for prototyping)
- complexity of algorithm (no, plan for ability to iterate instead)
- commits for mock human MR review (no, just look at end state)
- speed of dev (no, n/a for take-home)

### assumptions

- unlimited passenger capacity
- loading/unloading on a floor takes 10 seconds.
- all floor request made before the sim starts
- no zig-zagging, e.g., once elevator is going a direction, drop off all in that direction before reversing.
  -- this is a human factors assumption for how people expect elevators to work.

### future ideas

- requests incoming over time and location (not all at the start)
- improved control algorithm(s) / heuristics
  - min average wait time
  - square of expected wait time.
- validation of input/control signals
- visualization of the sim (from live and/or replay data)
- different elevator architectures
  - multiple cars
  - express cars (e.g. skip floors 2-19)
- models of request demand (e.g., workplace 9am arrive at 1, lunchtime)
- more realistic acceleration physics
- large-scale batch data analysis to aid design of building elevators and controls
