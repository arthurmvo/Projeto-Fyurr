from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    genres = db.Column(db.String)
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String)
    website_link = db.Column(db.String)
    looking_talent = db.Column(db.Boolean)
    seeking_desc = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    shows = db.relationship('Show', backref = 'venue')
    
    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    phone = db.Column(db.String)
    genres = db.Column(db.String)
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String)
    website_link = db.Column(db.String)
    looking_talent = db.Column(db.Boolean)
    seeking_desc = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    shows = db.relationship('Show', backref = 'artist')
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key = True)
  startTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
  
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete= "CASCADE"), nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), nullable = False)

  def __repr__(self):
    return f'<id: {self.id} Artist: {self.artist_id}, Venue {self.venus_id}>'
