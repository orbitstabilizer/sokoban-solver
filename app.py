from flask import Flask, render_template, request
from solve import Puzzle

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_board', methods=['POST'])
def create_board():
    board_size_input = request.form.get('board-size')
    m, n = None, None
    error = None

    if board_size_input:
        try:
            m, n = map(int, board_size_input.split('x'))
            if m <= 0 or n <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            error = "Invalid board size format. Please use the format 'mxn' (e.g., 7x7) with positive integers."

    return render_template('index.html', m=m, n=n, error=error)

@app.route('/solve', methods=['POST'])
def solve():
    m, n = map(int, request.form.get('board-size').split('x'))
    board = []
    for row in range(m):
        row_data = []
        for col in range(n):
            input_name = f"board-row-{row}-col-{col}"
            cell_content = request.form.get(input_name, "")
            row_data.append(cell_content)
        board.append(row_data)
    print(board)
    puzzle_ = Puzzle(board)
    puzzle_.print_board()
    print("Started solving..")
    root, prev = puzzle_.solve()
    puzzle_.print_solution(root, prev)


    return render_template('index.html', m=m, n=n, submitted_board=board)

if __name__ == '__main__':
    app.run(debug=True,port=5001)
