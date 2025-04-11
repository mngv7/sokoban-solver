
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

    def test_check_elem_action_seq_wh_1(self):
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

    def test_check_elem_action_seq_wh_13(self):
        wh = Warehouse()
        wh.load_warehouse("./warehouses/warehouse_13.txt")

        # Test 1
        answer = check_elem_action_seq(wh, ['Right', 'Down'])
        expected_answer = (
            '####   \n'
            '#. ##  \n'
            '#.  #  \n'
            '#. @#  \n'
            '##$$###\n'
            ' # $  #\n'
            ' #    #\n'
            ' #  ###\n'
            ' ####  '
        )
        assert answer == expected_answer, f"Test 1 failed! Expected:\n{expected_answer}\nBut got:\n{answer}"

        # Test 2
        answer = check_elem_action_seq(wh, ['Down', 'Right', 'Right'])
        expected_answer = 'Impossible'
        assert answer == expected_answer, f"Test 2 failed! Expected: {expected_answer}, but got: {answer}"


    def test_check_elem_action_seq_wh_125(self):
        wh = Warehouse()
        wh.load_warehouse("./warehouses/warehouse_125.txt")

        # Test 1
        answer = check_elem_action_seq(wh, ['Down', 'Left', 'Down', 'Left'])
        expected_answer = (
            '      #####  \n'
            '      #   ## \n'
            '      # $  # \n'
            '######## # ##\n'
            '# .  # $$   #\n'
            '#       @ # #\n'
            '#...#####$  #\n'
            '#####   #####'
        )
        assert answer == expected_answer, f"Test 1 failed! Expected:\n{expected_answer}\nBut got:\n{answer}"

        # Test 2
        answer = check_elem_action_seq(wh, ['Down', 'Left', 'Left'])
        expected_answer = 'Impossible'
        assert answer == expected_answer, f"Test 2 failed! Expected: {expected_answer}, but got: {answer}"



    # @pytest.mark.skip("Not implemented")
    def test_solve_weighted_sokoban_wh8a(self):
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

    def test_solve_weighted_sokoban_wh9(self):
        wh = Warehouse()    
        wh.load_warehouse( "./warehouses/warehouse_09.txt")
        # first test
        answer, cost = solve_weighted_sokoban(wh)

        expected_answer = ['Up', 'Right', 'Right', 'Down', 'Up', 'Left', 'Left', 'Down', 'Right', 'Down', 'Right', 'Left', 'Up', 'Up', 'Right', 'Down', 'Right',
                            'Down', 'Down', 'Left', 'Up', 'Right', 'Up', 'Left', 'Down', 'Left', 'Up', 'Right', 'Up', 'Left'] 
        expected_cost = 396
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

    def test_solve_weighted_sokoban_wh47(self):
        wh = Warehouse()    
        wh.load_warehouse( "./warehouses/warehouse_47.txt")
        # first test
        answer, cost = solve_weighted_sokoban(wh)

        expected_answer = ['Right', 'Right', 'Right', 'Up', 'Up', 'Up', 'Left', 'Left', 'Down', 'Right', 'Right', 'Down', 'Down', 'Left', 'Left', 'Left', 'Left', 'Up',
                        'Up', 'Right', 'Right', 'Up', 'Right', 'Right', 'Right', 'Right', 'Down', 'Left', 'Up', 'Left', 'Down', 'Down', 'Up', 'Up', 'Left', 'Left',
                        'Down', 'Left', 'Left', 'Down', 'Down', 'Right', 'Right', 'Right', 'Right', 'Right', 'Right', 'Down', 'Right', 'Right', 'Up', 'Left',
                        'Left', 'Left', 'Left', 'Left', 'Left', 'Down', 'Left', 'Left', 'Up', 'Up', 'Up', 'Right', 'Right', 'Right', 'Up', 'Right', 'Down', 'Down',
                        'Up', 'Left', 'Left', 'Left', 'Left', 'Down', 'Down', 'Down', 'Right', 'Right', 'Up', 'Right', 'Right', 'Left', 'Left', 'Down', 'Left',
                        'Left', 'Up', 'Right', 'Right'] 
        expected_cost = 179
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

    
    #@pytest.mark.skip
    def test_solve_weighted_sokoban_wh7(self):
        wh = Warehouse()    
        wh.load_warehouse( "./warehouses/warehouse_07.txt")
        # first test
        answer, cost = solve_weighted_sokoban(wh)

        expected_answer = ['Up', 'Up', 'Right', 'Right', 'Up', 'Up', 'Left', 'Left', 'Down', 'Down', 'Right', 'Up', 'Down', 'Right', 'Down', 'Down', 'Left', 'Up',
                            'Down', 'Left', 'Left', 'Up', 'Left', 'Up', 'Up', 'Right'] 
        expected_cost = 26
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

    pytest.mark.skip("takes ages to run")
    def test_solve_weighted_sokoban_wh147(self):
        wh = Warehouse()    
        wh.load_warehouse( "./warehouses/warehouse_147.txt")
        # first test
        answer, cost = solve_weighted_sokoban(wh)

        expected_answer = ['Left', 'Left', 'Left', 'Left', 'Left', 'Left', 'Down', 'Down', 'Down', 'Right', 'Right', 'Up', 'Right', 'Down', 'Right', 'Down',
                            'Down', 'Left', 'Down', 'Left', 'Left', 'Up', 'Up', 'Down', 'Down', 'Right', 'Right', 'Up', 'Right', 'Up', 'Up', 'Left', 'Left', 'Left',
                            'Down', 'Left', 'Up', 'Up', 'Up', 'Left', 'Up', 'Right', 'Right', 'Right', 'Right', 'Right', 'Right', 'Down', 'Right', 'Right', 'Right',
                            'Up', 'Up', 'Left', 'Left', 'Down', 'Left', 'Left', 'Left', 'Left', 'Left', 'Left', 'Down', 'Down', 'Down', 'Right', 'Right', 'Up', 'Left',
                            'Down', 'Left', 'Up', 'Up', 'Left', 'Up', 'Right', 'Right', 'Right', 'Right', 'Right', 'Right', 'Left', 'Left', 'Left', 'Left', 'Left', 'Down',
                            'Down', 'Down', 'Down', 'Right', 'Down', 'Down', 'Right', 'Right', 'Up', 'Up', 'Right', 'Up', 'Left', 'Left', 'Left', 'Down', 'Left',
                            'Up', 'Up', 'Up', 'Left', 'Up', 'Right', 'Right', 'Right', 'Right', 'Right', 'Down', 'Right', 'Down', 'Right', 'Right', 'Up', 'Left',
                            'Right', 'Right', 'Up', 'Up', 'Left', 'Left', 'Down', 'Left', 'Left', 'Left', 'Left', 'Left', 'Left', 'Right', 'Right', 'Right', 'Right', 'Right',
                            'Right', 'Up', 'Right', 'Right', 'Down', 'Down', 'Left', 'Down', 'Left', 'Left', 'Up', 'Right', 'Right', 'Down', 'Right', 'Up', 'Left',
                            'Left', 'Up', 'Left', 'Left'] 
        expected_cost = 521
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



    
    
    
    
    
    
    
    #@pytest.mark.skip("Not implemented")
    def test_solve_weighted_sokoban_wh5n(self):
        wh = Warehouse()    
        wh.load_warehouse( "./warehouses/warehouse_5n.txt")
        # first test
        answer, cost = solve_weighted_sokoban(wh)

        expected_answer = ['Impossible'] 
        expected_cost = None
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


    
