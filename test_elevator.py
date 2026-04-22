import sys
import logging
import pytest


from elevator import *

def test_visit():
    e = Elevator(2)
    e.add_request(1)
    e.add_requests([2,3])
    e.visit_floor()
    assert e._requests == [1,3]

# test data is tuples of
# start floor, [floor requests], move, last move, exp move
testdata = [
    ( 1, [], STOP, IDLE, STOP, "no requests"),
    ( 1, [3, 2, 1], STOP, IDLE, STOP, "passenger to drop"),
    ( 1, [2, 3, 4], STOP, IDLE, GO_UP, "only up requests"),
    ( 10, [2, 3, 4], STOP, IDLE, GO_DOWN, "only down requests"),
    ( 10, [11,1], STOP, IDLE, GO_UP, "up first and closer"),
    ( 10, [9,19], STOP, IDLE, GO_DOWN, "down first and closer"),
    ( 10, [1,19], STOP, GOING_UP, GO_UP, "was going up"),
    ( 10, [1,19], STOP, GOING_DOWN, GO_DOWN, "was going down"),
]

@pytest.mark.parametrize("start,floors,move,last_move,exp_move,name", testdata)
def test_control(start, floors, move, last_move, exp_move, name):
    e = Elevator(start)
    e._last_move = last_move
    for f in floors:
        e.add_request(f)
    e.control()        
    assert e._move == exp_move


# test data is tuples of
# start floor, [floor requests], exp total runtime, [exp floors visited]
testdata = [
    ( 1, [1, 2, 3], 50, [1, 2, 3]),
    ( 12, [2, 9, 1, 32], 470, [12, 9, 2, 1, 32] ),
    ( 1, [99999], 10000, [1])
]

@pytest.mark.parametrize("start,floors,exp_runtime,exp_visited", testdata)
def test_run(start, floors, exp_runtime, exp_visited):
    e = Elevator(start)
    e.add_requests(floors)
    e.run(1000)

    assert e._timer == exp_runtime
    assert e._visited == exp_visited

# test i/o wrapping. logic testing handled above
def test_main(capsys):
    main(lines=["1", "1 1 2 3"])
    captured = capsys.readouterr()
    assert captured.out == '10 1\n50 1,2,3\n'
