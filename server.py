from flask import Flask, render_template
from peewee import *
from itertools import product

app = Flask(__name__)
db = SqliteDatabase('checkers.db')


class BaseModel(Model):
    class Meta:
        database = db


class Turn(BaseModel):
    whose = CharField()


class Piece(BaseModel):
    color = TextField()
    position = TextField()
    is_kinged = BooleanField()

class Space():
    def __init__(self, coord, piece=None):
        self.coord = coord # (2, 4)
        self.piece = piece

    @classmethod
    def position_to_coord(_clazz, position_str):
        row = int(position_str[1:]) - 1
        col = ['ABCDEFGH'[i] for i in range(Board.ROWS)].index(position_str[0])
        return row, col

class Board():
    ROWS = 8
    COLS = 8

    def __init__(self, all_pieces):
        self.pieces = [[None for _ in range(Board.COLS)] for _ in range(Board.ROWS)]
        for piece in all_pieces:
            row, col = Space.position_to_coord(piece.position)
            self.pieces[row][col] = piece

    def rows(self):
        for r, row in enumerate(self.pieces):
            yield r, [Space((r, col), row[col]) for col in range(Board.COLS)]
    
    def piece_by_id(self, id):
        all_pieces = [p for row in self.pieces for p in row if p]
        return next(filter(lambda p: str(p.id) == id, all_pieces), None)

    def can_move(self, from_piece, to_space):
        row, col = Space.position_to_coord(from_piece.position)
        if from_piece.color == 'red':
            print(row, col, to_space.coord)
            return row + 1 == to_space.coord[0] and \
                   (col + 1 == to_space.coord[1] or \
                    col - 1 == to_space.coord[1])
        else:
            return row - 1 == to_space.coord[0] and \
                   (col + 1 == to_space.coord[1] or \
                    col - 1 == to_space.coord[1])

def setup_db():
    db.connect()
    db.create_tables([Turn, Piece], safe=True)
    db.close()

def seed_data():
    red_start = [
        'A1',
        'C1',
        'E1',
        'G1',
        'B2',
        'D2',
        'F2',
        'H2',
        'A3',
        'C3',
        'E3',
        'G3'
    ]
    black_start = [
        'B6',
        'D6',
        'F6',
        'H6',
        'A7',
        'C7',
        'E7',
        'G7',
        'B8',
        'D8',
        'F8',
        'H8'
    ]
    if len(Turn.select()) == 0:
        Turn.create(whose='black')
        for red_pos in red_start:
            Piece.create(color='red', position=red_pos, is_kinged=False)
        for black_pos in black_start:
            Piece.create(color='black', position=black_pos, is_kinged=False)

setup_db()
seed_data()

def is_selected(piece, request):
    if str(piece.id) == request.args.get('id', ''):
        return 'selected' 
    return ''

def is_valid_move(board, space, request):
    id = request.args.get('id', '')
    if id:
        piece = board.piece_by_id(id)
        if board.can_move(piece, space):
            return 'highlighted'
    return ''

@app.route("/")
def index():
    turn = Turn.select().order_by(Turn.id.desc()).get().whose
    board = Board(Piece.select())
    return render_template('index.html', board=board, turn=turn, is_selected=is_selected, is_valid_move=is_valid_move)