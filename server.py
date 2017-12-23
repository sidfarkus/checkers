from flask import Flask, render_template, url_for, redirect, request
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

    def position(self):
        return "{}{}".format('ABCDEFGH'[self.coord[1]], self.coord[0] + 1)

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

    def space_at_position(self, position):
        row, col = Space.position_to_coord(position)
        return list(self.rows())[row][1][col]

    def rows(self):
        for r, row in enumerate(self.pieces):
            yield r, [Space((r, col), row[col]) for col in range(Board.COLS)]
    
    def piece_by_id(self, id):
        all_pieces = [p for row in self.pieces for p in row if p]
        return next(filter(lambda p: str(p.id) == id, all_pieces), None)

    def can_move(self, from_piece, to_space):
        if to_space.piece is not None:
            return False

        row, col = Space.position_to_coord(from_piece.position)
        if from_piece.color == 'red':
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
        'H8',
    ]
    if len(Turn.select()) == 0:
        Turn.create(whose='black')
        Piece.delete().execute()
        for red_pos in red_start:
            Piece.create(color='red', position=red_pos, is_kinged=False)
        for black_pos in black_start:
            Piece.create(color='black', position=black_pos, is_kinged=False)

setup_db()
seed_data()

def is_selected(whose_turn, piece, request):
    return whose_turn == piece.color and str(piece.id) == request.args.get('id', '')

def selected_class(whose_turn, piece, request):
    if is_selected(whose_turn, piece, request):
        return 'selected' 
    return ''

def is_valid_move(board, space, request):
    id = request.args.get('id', '')
    if id:
        piece = board.piece_by_id(id)
        return board.can_move(piece, space)

def move_piece_class(turn, board, space, request):
    piece = board.piece_by_id(request.args.get('id', ''))
    if piece and turn == piece.color and is_valid_move(board, space, request):
        return 'highlighted'
    return 'disabled'

def move_piece_url(board, space, request):
    if is_valid_move(board, space, request):
        return url_for('move', id=request.args.get('id', ''), pos=space.position())
    return '#'

@app.route("/")
def index():
    turn = Turn.select().order_by(Turn.id.desc()).get().whose
    board = Board(Piece.select())
    return render_template('index.html', board=board, turn=turn, is_selected=is_selected, selected_class=selected_class, move_piece_class=move_piece_class, move_piece_url=move_piece_url)

@app.route("/move")
def move():
    turn = Turn.select().order_by(Turn.id.desc()).get()
    board = Board(Piece.select())
    piece = board.piece_by_id(request.args.get('id', ''))
    if piece.color != turn.whose:
        return redirect('/')

    position = request.args.get('pos', '')
    if board.can_move(piece, board.space_at_position(position)):
        piece.position = position
        piece.save()
        turn.whose = 'black' if turn.whose == 'red' else 'red'
        turn.save()
    return redirect('/') 

if __name__ == '__main__':
    app.run(debug=True)
