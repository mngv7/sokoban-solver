
'''

Quick "sanity check" script to test your submission 'mySokobanSolver.py'

This is not an exhaustive test program. It is only intended to catch major
blunders!

You should design your own test cases and write your own test functions.

Although a different script (with different inputs) will be used for 
marking your code, make sure that your code runs without errors with this script.


'''


from sokoban import Warehouse
import pytest

try:
    from fredSokobanSolver import taboo_cells, solve_weighted_sokoban, check_elem_action_seq
    print("Using Fred's solver")
except ModuleNotFoundError:
    from mySokobanSolver import taboo_cells, solve_weighted_sokoban, check_elem_action_seq
    print("Using submitted solver")

class TestSokoban:
    def test_taboo_cells_wh_01(self):
        wh = Warehouse()
        wh.load_warehouse("./warehouses/warehouse_01.txt")
        expected_answer = (
            '####  \n'
            '#X #  \n'
            '#  ###\n'
            '#   X#\n'
            '#   X#\n'
            '#XX###\n'
            '####  '
        )
        answer = taboo_cells(wh)
        assert answer == expected_answer

    def test_taboo_cells_wh_03(self):
        wh = Warehouse()
        wh.load_warehouse("./warehouses/warehouse_03.txt")
        expected_answer = (
            '  ####   \n'
            '###XX####\n'
            '#X     X#\n'
            '#X#  # X#\n'
            '#X   #XX#\n'
            '#########'
        )
        answer = taboo_cells(wh)
        assert answer == expected_answer

    def test_taboo_cells_wh_29(self):
        wh = Warehouse()
        wh.load_warehouse("./warehouses/warehouse_29.txt")
        expected_answer = (
            '     ##### \n'
            '     #XXX##\n'
            '     #X  X#\n'
            ' ######X X#\n'
            '##XXXXX# X#\n'
            '#X       ##\n'
            '#X###### # \n'
            '#XXXXXXXX# \n'
            '########## '
        )
        answer = taboo_cells(wh)
        assert answer == expected_answer

    def test_check_elem_action_seq(self):
        wh = Warehouse()
        wh.load_warehouse("./warehouses/warehouse_01.txt")

        # Test 1
        answer = check_elem_action_seq(wh, ['Right', 'Right', 'Down'])
        expected_answer = (
            '####  \n'
            '# .#  \n'
            '#  ###\n'
            '#*   #\n'
            '#  $@#\n'
            '#  ###\n'
            '####  '
        )
        assert answer == expected_answer, f"Test 1 failed! Expected:\n{expected_answer}\nBut got:\n{answer}"

        # Test 2
        answer = check_elem_action_seq(wh, ['Right', 'Right', 'Right'])
        expected_answer = 'Impossible'
        assert answer == expected_answer, f"Test 2 failed! Expected: {expected_answer}, but got: {answer}"


    @pytest.mark.skip("Not implemented")
    def test_solve_weighted_sokoban():
        wh = Warehouse()    
        wh.load_warehouse( "./warehouses/warehouse_8a.txt")
        # first test
        answer, cost = solve_weighted_sokoban(wh)

        expected_answer = ['Up', 'Left', 'Up', 'Left', 'Left', 'Down', 'Left', 
                        'Down', 'Right', 'Right', 'Right', 'Up', 'Up', 'Left', 
                        'Down', 'Right', 'Down', 'Left', 'Left', 'Right', 
                        'Right', 'Right', 'Right', 'Right', 'Right', 'Right'] 
        expected_cost = 431
        print('<<  test_solve_weighted_sokoban >>')
        if answer==expected_answer:
            print(' Answer as expected!  :-)\n')
        else:
            print('unexpected answer!  :-(\n')
            print('Expected ');print(expected_answer)
            print('But, received ');print(answer)
            print('Your answer is different but it might still be correct')
            print('Check that you pushed the right box onto the left target!')
        print(f'Your cost = {cost}, expected cost = {expected_cost}')
