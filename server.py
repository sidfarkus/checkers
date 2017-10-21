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
  color = IntegerField()
  position = TextField()
  is_kinged = BooleanField()

  def letter_position(self):
    return self.position[0]

  def number_position(self):
    return self.position[1]

class Board():
  def __init__(self, all_pieces):
    self.pieces = [[] for _ in range(8)]
    for piece in all_pieces:
      row = int(piece.number_position) + 1
      col = ['ABCDEFGH'[i] for i in range(8)].index(piece.letter_position)
      self.pieces[row][col] = piece

def setup_db():
  db.connect()
  db.create_tables([Turn, Piece], safe=True)
  db.close()

def seed_data():
  db.connect()
  if len(models.Turn.select()) == 0:
    models.Turn.create()
    positions = product(['ABCDEFGH'[i] for i in range(8)], map(str, range(8))
    models.Piece.create()
  db.close()

setup_db()
seed_data()

@app.route("/")
def index():
  board = Board(models.Piece.select())
  return render_template('index.html', board=board)