from enum import Enum
from dataclasses import dataclass
from queue import deque

class BoxContent(Enum):
    empty = ' '
    wall = '#'
    block = 'X'
    player = 'P'
    target = 'O'
    block_and_target = '@'
    @property
    def value(self):
        if self == BoxContent.wall:
            return "#"
        elif self == BoxContent.block:
            return "▀"
        else:
            return " "
class Direction(Enum):
    up = 0
    down = 1
    left = 2
    right = 3
    @property
    def value(self):
        if self == Direction.up:
            return (-1, 0)
        elif self == Direction.down:
            return (1, 0) 
        elif self == Direction.left:
            return (0, -1) 
        elif self == Direction.right:
            return (0, 1)
        else:
            raise Exception("unknown direction")
    @property
    def opposite(self):
        if self == Direction.up:
            return Direction.down
        elif self == Direction.down:
            return Direction.up
        elif self == Direction.left:
            return Direction.right
        elif self == Direction.right:
            return Direction.left
        else:
            raise Exception("unknown direction")

@dataclass
class Box:
    content: BoxContent
    x: int
    y: int
    traversable_t : int
    id: int = -1

class Puzzle:
    def __init__(self, board):
        self.targets =  None       
        self.player = None
        self.boxes = []
        self.board =  self.create_board(board)
        self.time = 0
        self.set_traversable_boxes()
    
    @property
    def current_state(self):
        if self.player is None:
            raise Exception("player not found")
        ls = [(self.player.x, self.player.y)]
        for box in self.boxes:
            ls.append((box.x, box.y))
        return tuple(ls)

    def create_board(self, board):
        new_board = []
        box_id = 0
        targets = [ ] 
        for i, row in enumerate(board):
            new_row = []
            for j, col in enumerate(row):
                tmp = Box(BoxContent(col), i, j,-1)
                new_row.append(tmp)
                
                if tmp.content == BoxContent.player:
                    self.player = tmp
                elif tmp.content in [BoxContent.block, BoxContent.block_and_target]: 
                    self.boxes.append(tmp)
                    tmp.id = box_id
                    box_id += 1
                if tmp.content in [BoxContent.target , BoxContent.block_and_target]:
                    targets.append((i, j ))

            new_board.append(new_row)

        self.targets = targets
        return new_board

    def print_board(self, show_possible_moves=False):
        for row in self.board:
            for box in row:
                buff = box.content.value
                if (box.x, box.y) in self.targets:
                    buff = "X"
                if box.content == BoxContent.block:
                    buff = str(box.id)
                if self.is_reachable(box):
                    buff = "."
                if box.content == BoxContent.player:
                    buff = "P"
                if show_possible_moves:
                    if box in [x[0] for x in self.possible_moves()]:
                        buff = "!"
                print(buff, end=" ")

            print()
        print()

    def is_travelable(self, box):
        return  box.content in (BoxContent.empty,BoxContent.player, BoxContent.target)

    def is_reachable(self, box):
        return box.traversable_t == self.time 
    
    def set_traversable_boxes(self):
        def dfs(box):
            if self.is_reachable(box):
                return
            box.traversable_t = self.time
            for i, j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                if self.is_travelable(self.board[box.x+i][box.y+j]):
                    dfs(self.board[box.x+i][box.y+j])
        if self.player is None:
            raise Exception("player not found")

        self.time += 1
        dfs(self.player)

    def possible_moves(self):
        result = []
        for box in self.boxes:
            for dir in Direction:
                i, j = dir.value
                oi, oj = dir.opposite.value
                if self.is_reachable(self.board[box.x+i][box.y+j]) and self.is_travelable(self.board[box.x+oi][box.y+oj]):
                    result.append((box,dir.opposite))

        return result

    def swap(self, box1, box2):
        if box1.content == BoxContent.wall or box2.content == BoxContent.wall:
            return
        board = self.board
        board[box1.x][box1.y], board[box2.x][box2.y] = board[box2.x][box2.y], board[box1.x][box1.y]
    
        (box1.x, box1.y), (box2.x, box2.y) = (box2.x, box2.y), (box1.x, box1.y)
        box1.traversable_t = -1
        box2.traversable_t = -1


    def move_block(self, block, dir):
        i, j = dir.value
        oi, oj = dir.opposite.value
        if self.is_reachable(self.board[block.x+oi][block.y+oj]) and self.is_travelable(self.board[block.x+i][block.y+j]):
            empty = self.board[block.x+i][block.y+j]
            player = self.player
            self.swap(block, empty)
            self.swap(player, empty)
            self.set_traversable_boxes()


    def go_to_state(self, state):
        for box in self.boxes:
            self.swap(box, self.board[state[box.id+1][0]][state[box.id+1][1]])
        self.swap(self.player, self.board[state[0][0]][state[0][1]])
        self.set_traversable_boxes()

    def is_solved(self):
        for box in self.boxes:
            if (box.x, box.y) not in self.targets:
                return False
        return True
            
    def print_solution(self, tail,  prev):
        path = []
        head = tail
        while True:
            path.append(head)
            if head in prev:
                head = prev[head]
            else:
                break
        print("Solution length: ", len(path))
        for s in path[::-1]:
            print('-'*50)
            self.go_to_state(s)
            self.print_board()
        

    def solve(self):
        cs = self.current_state
        history = {cs[1:] : [cs[0]]}
        prev = {}
        def visited(node):
            tmp = self.current_state
            self.go_to_state(node)
            player = node[0]
            boxes  = node[1:]
            if boxes not in history:
                self.go_to_state(tmp)
                return False
            for p_ in history[boxes]:
                if self.is_reachable(self.board[p_[0]][p_[1]]):
                    self.go_to_state(tmp)
                    return True
            self.go_to_state(tmp)
            return False

        def visit(node):
            if node[1:] in history:
                history[node[1:]].append(node[0])
            else:
                history[node[1:]]=[node[0]]
            prev[node] = self.current_state

        q = deque([cs])
        while len(q) != 0 : 
            root = q.popleft()
            self.go_to_state(root)
            if self.is_solved():
                print("Solved.")
                print("History items: ", len(history))
                print("Total states: ", sum(map(len, history.values())))
                return root, prev 
            for box, dir in self.possible_moves():
                self.move_block(box, dir)
                child = self.current_state
                self.go_to_state(root)
                
                if not visited(child):
                    q.append(child)
                    visit(child)
       

def demo():
    board =  [ 
       ['#', '#', '#', '#', '#', '#', '#', '#', '#'], 
       ['#', ' ', ' ', ' ', '#', '#', '#', '#', '#'], 
       ['#', ' ', ' ', 'O', 'X', ' ', '#', '#', '#'], 
       ['#', '#', ' ', 'O', '#', ' ', 'X', 'P', '#'], 
       ['#', '#', ' ', 'O', '#', ' ', 'X', ' ', '#'], 
       ['#', '#', '#', 'O', ' ', ' ', 'X', ' ', '#'], 
       ['#', '#', '#', ' ', ' ', '#', '#', '#', '#'], 
       ['#', '#', '#', '#', '#', '#', '#', '#', '#'], 
    ]
    # targets =frozenset([(2, 3), (3, 3), (4,3), (5, 3)]) 
    puzzle_ = Puzzle(board)
    puzzle_.print_board()
    print("Started solving..")
    root, prev = puzzle_.solve()
    puzzle_.print_solution(root, prev)

def demo2():
    # board =  [ 
    #        [1, 1, 1, 1, 1, 1, 1 ], 
    #        [1, 0, 0, 1, 0, 0, 1 ], 
    #        [1, 0, 0, 2, 0, 0, 1 ], 
    #        [1, 0, 0, 2, 0, 0, 1 ], 
    #        [1, 0, 2, 2, 2, 0, 1 ], 
    #        [1, 1, 0, 0, 3, 1, 1 ], 
    #        [1, 1, 1, 1, 1, 1, 1 ], 
    #     ]
    board =  [ 
           ['#', '#', '#', '#', '#', '#', '#' ], 
           ['#', ' ', ' ', '#', ' ', ' ', '#' ], 
           ['#', ' ', ' ', 'X', ' ', ' ', '#' ], 
           ['#', ' ', 'O', '@', 'O', ' ', '#' ], 
           ['#', ' ', 'X', '@', 'X', ' ', '#' ], 
           ['#', '#', ' ', 'O', 'P', '#', '#' ], 
           ['#', '#', '#', '#', '#', '#', '#' ], 
        ]

    # targets = frozenset([(3, 3), (4, 3), (5, 3), (3,2), (3,4)])
    p = Puzzle(board)
    
    print("Started solving..")
    root, prev = p.solve()
    p.print_solution(root, prev)


if __name__ == '__main__':
    demo()

