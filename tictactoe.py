"""
1. setup a board with 9 squares (3x3 array)
    a. enum (x, o, empty)
current_player_state = x
while true:
    2. go user by user, ask for input square (1-9)
    2b. Validate that input square has not yet been used.
        if not valid, continue aka jump to top of loop
    3. take input, fill square to the current_player_state
    4. check for winner from LAST SQUARE only -> current_player_state -> break
         a. (2, 4, 6, 8) -> check for row-win and col-win 
         b. (1, 3, 7, 9) -> check for row-win, col-win, and diag-win
         c. (5) -> check for row-win, col-win, diag-1win, diag-2 win
    4b. check for tie (all squares are not empty) -> print("tie") -> break
    5. set current_player_state = o or x depending on current
"""
import numpy as np

## key: 0 -> empty, -1 -> O; 1 -> X

board = np.zeros((3,3), dtype = int)

num_to_player = {
    1: "X",
    -1: "O",
    0: "-",
}

def print_board(board):
    """
    Print the current board state as a 3x3 ASCII grid
    """
    print("-------------")
    for i in range(3):
        print("|", end=" ")
        for j in range(3):
            print(f"{num_to_player[board[i][j]]}", end=" | ")
        print("\n-------------")

def int_to_row_col_idx(a: int) -> tuple:
    """
    Takes in a num [1,9] -> [0-2][0-2]
    """
    a = a -1
    col_idx = a % 3
    row_idx = a // 3
    return (row_idx, col_idx)

def check_row_win(row_idx):
    if sum(board[row_idx]) in [3,-3]:
        return True
    return False

def check_column_win(col_idx):
    if sum(board[:,col_idx]) in [3,-3]:
        return True
    return False

def check_diagonal_win():
    diag1 = sum([board[int_to_row_col_idx(1)], board[int_to_row_col_idx(5)],board[int_to_row_col_idx(9)]])
    diag2 = sum([board[int_to_row_col_idx(3)], board[int_to_row_col_idx(5)],board[int_to_row_col_idx(7)]])
    return diag1 in [3,-3] or diag2 in [3,-3]

edge_tiles = [2, 4, 6, 8]
corner_tiles = [1,3,7,9]
middle_tile = 5

def main():
    current_state = 1
    turn = 0
    while True:
        #1. get an sanitize input from user
        player = current_state if current_state == 1 else 2
        print(f"Player {player} Enter square number (1-9):")
        square = input()
        try:
            square = int(square)
        except Exception as e:
            raise e
        if square not in range(1, 10):
            print("Error. Not a valid integer or the square is already filled. Please try again.")
            continue
        row_idx, col_idx = int_to_row_col_idx(square)
        if board[row_idx][col_idx] != 0:
            print("Square is already filled")
            continue
        
        # 2. fill the square with current player state
        board[row_idx][col_idx] = current_state

        # 3. check winner or tie
        if check_row_win(row_idx):
            print(f"Player with {current_state} wins")
            break
        
        elif check_column_win(col_idx):
            print(f"Player with {current_state} wins")
            break

        elif check_diagonal_win():
            print(f"Player with {current_state} wins")
            break
        # 4. set new state

        if current_state == 1:
            current_state = -1
        else:
            current_state = 1
        print(f"Board State after turn {turn}")
        turn += 1
        print_board(board)
        # check for tie.
        if turn == 9:
            print("Tie has happened! No one wins.")
            break

if __name__ == "__main__":
    main()