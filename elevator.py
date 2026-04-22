import sys
import logging

# control constants
STOP = 0
GO_UP = 1
GO_DOWN = -1

IDLE = 0
GOING_UP = 1
GOING_DOWN = -1

# time constant to move a floor OR load/unload passengers
UPDATE_TIME = 10

class Elevator(object):
    def __init__(self, f=1, logger=None):
        # list of floor requests, in order of reciept.
        self._requests = []

        # list of floors visited
        self._visited = []
        self._timer = 0
        
        # 1 is up, -1 is down, is stopped.
        self._floor = f
        self._move = 0
        self._last_move = 0

        self._logger = logger or logging.getLogger('dummy')
        
    def add_request(self, f):
        self._requests.append(f)

    def add_requests(self, fs):
        self._requests.extend(fs)

    def has_requests(self):
        return len(self._requests)>0

    def visit_floor(self):
        if self._floor in self._requests:
                self._move = 0
                self._requests = [r for r in self._requests if r != self._floor]
        self._visited.append(self._floor)

    def update(self):
        self._timer += UPDATE_TIME
        if not self._move:
            self.visit_floor()
        else:
            self._floor += self._move

        self.control()

    # control the elevator by setting the move direction.
    def control(self):
        # stop to drop off a passenger.
        if self._floor in self._requests:
            self._move = STOP
            return

        # keep going until reach a drop off floor.
        if self._move:
            return

        # nothing to do.
        if not self._requests:
            self._move = STOP
            self._last_move = IDLE
            return

        # still work to do in the last direction. (no zigzag)
        max_f = max(self._requests)
        min_f = min(self._requests)
        if self._last_move > 0 and max_f > self._floor:
            self._move = GO_UP
            return
        elif self._last_move < 0 and min_f < self._floor:
            self._move = GO_DOWN
            return

        # heuristically choose up/down.
        # - "first" request get priority.
        if self._requests[0] > self._floor:
            self._move = GO_UP
            return
        else:
            self._move = GO_DOWN
            return


    def run(self, max_ticks=None):
        t = 0
        while True:
            t += 1
            if max_ticks and t > max_ticks:
                break

            self._logger.debug(str(self))
            self.update()
            
            if not self.has_requests():
                break

        self._logger.debug(str(self))

    def format_run_log(self):
        return '{} {}'.format(self._timer, ','.join(map(str,self._visited)))

    def pretty_move(self):
        if self._move > 0:
            return '/\\/\\'
        elif self._move < 0:
            return '\\/\\/'
        else:
            return 'stop'

    def __str__(self):
        return "{} Elevator<fl {} {} reqs {}>".format( self._timer, self._floor, self.pretty_move(), self._requests) 
                                                              
def main(lines=sys.stdin):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stderr))
    #logger.addHandler(logging.FileHandler("out.log"))

    for line in lines:
        floors = [int(x) for x in line.split()]
        e = Elevator(floors[0], logger=logger)
        for f in floors[1:]:
            e.add_request(f)
        e.run()
        print(e.format_run_log())
    
if __name__ == '__main__':
    main()






    
