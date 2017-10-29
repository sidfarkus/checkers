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

    def letter_position(self):
        return self.position[2]

    def number_position(self):
        return self.position[6]


class Board():
    def __init__(self, all_pieces):
        self.pieces = [['' for _ in range(8)] for _ in range(8)]
        for piece in all_pieces:
            row = int(piece.number_position()) - 1
            col = ['ABCDEFGH'[i] for i in range(8)].index(piece.letter_position())
            self.pieces[row][col] = piece


def setup_db():
    db.connect()
    db.create_tables([Turn, Piece], safe=True)
    db.close()

def seed_data():
    red_start = [
        ('A', 1),
        ('C', 1),
        ('E', 1),
        ('G', 1),
        ('B', 2),
        ('D', 2),
        ('F', 2),
        ('H', 2),
        ('A', 3),
        ('C', 3),
        ('E', 3),
        ('G', 3)
    ]
    black_start = [
        ('B', 6),
        ('D', 6),
        ('F', 6),
        ('H', 6),
        ('A', 7),
        ('C', 7),
        ('E', 7),
        ('G', 7),
        ('B', 8),
        ('D', 8),
        ('F', 8),
        ('H', 8)
    ]
    if len(Turn.select()) == 0:
        Turn.create(whose='black')
        for red_pos in red_start:
            Piece.create(color='red', position=red_pos, is_kinged=False)
        for black_pos in black_start:
            Piece.create(color='black', position=black_pos, is_kinged=False)

setup_db()
seed_data()

@app.route("/")
def index():
    turn = Turn.select().order_by(Turn.id.desc()).get().whose
    board = Board(Piece.select())
    return render_template('index.html', board=board, turn=turn)
