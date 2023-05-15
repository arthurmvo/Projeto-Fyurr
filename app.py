#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import collections
collections.Callable = collections.abc.Callable # Had to do that because I was getting an error on the collections module in python 3.11 version.
from flask_migrate import Migrate
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

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
    
    shows = db.relationship('Show', backref = 'artist')
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key = True)
  startTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete= "CASCADE"), nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), nullable = False)

  def __repr__(self):
    return f'<id: {self.id} Artist: {self.artist_id}, Venue {self.venus_id}>'
  


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  num_venues = Venue.query.all()
  all_shows = Show.query.all()
  data = []
  for venue in num_venues:
    i = 0
    strVenue = []
    for show in all_shows:
      if (show.venue_id == venue.id & show.startTime > datetime.utcnow):
        i += 1
    strVenue.append({"id" : venue.id, "name": venue.name, "num_upcoming_shows":i})
    data.append({"city": venue.city, "state": venue.state, "venues" : strVenue})

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  s_keyword = request.form.get('search_term','')
  all_venues = Venue.query.all()
  all_shows = Show.query.all()
  count = 0
  i = 0
  response = {}
  data = []
  for venue in all_venues:
    if (s_keyword.lower() in venue.name.lower()):
      count += 1
      for show in all_shows:
        if (show.venue_id == venue.id & show.startTime > datetime.utcnow):
          i += 1
      data.append({"id" : venue.id, "name" : venue.name, "num_upcoming_shows" : i})
    response = {"count" : count, "data" : data}
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  
  print(venue.genres)
  venue_shows = Show.query.filter_by(venue_id=venue_id).all()
  pastShowsCount = nextShowsCount = 0
  pastShows = nextShows = []
  for show in venue_shows:
    id_artista = show.artist_id
    artista = Artist.query.get(id_artista)
    if show.startTime < datetime.utcnow:
      nextShowsCount += 1
      nextShows.append({"artist_id" : artista.id, "artist_name": artista.name, "artist_image_link" : artista.image_link,
                  "start_time" : show.startTime})
    else:
      pastShowsCount += 1
      pastShows.append({"artist_id" : artista.id, "artist_name": artista.name, "artist_image_link" : artista.image_link,
                      "start_time" : show.startTime})
  # data = {}
  aux = venue.genres.split(",")
  genres = []
  for genre in aux:
    replacing = genre.replace("{","")
    replacing = replacing.replace("}","")
    genres.append(replacing)

  
  # print(genres)    
  data = {
    "id": venue_id,
    "name": venue.name,
    "genres": genres, 
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.looking_talent,
    "seeking_description": venue.seeking_desc,
    "image_link": venue.image_link,
    "past_shows":pastShows,
    "upcoming_shows": nextShows,
    "past_shows_count": pastShowsCount,
    "upcoming_shows_count": nextShowsCount,
  }   
  
  # print(data) 

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  form = VenueForm(request.form)
  
  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data.strip()
  address = form.address.data.strip()
  phone = form.phone.data
  image_link = form.image_link.data.strip()
  facebook_link = form.facebook_link.data.strip()
  website_link = form.website_link.data.strip()
  genres = form.genres.data
  looking_talent = form.seeking_talent.data
  seeking_desc = form.seeking_description.data.strip()

  if not form.validate():
    flash(form.errors)
    # print(form.data)
    return redirect(url_for('create_venue_submission'))
  else:
    error_in_insert = False
    # print(form.data)

  try:

    venue = Venue(
      name=name,city=city,state=state, address=address, phone=phone,genres=genres,
      image_link=image_link, facebook_link=facebook_link, website_link=website_link, looking_talent=looking_talent,seeking_desc=seeking_desc)
    
    db.session.add(venue)
    db.session.commit()

  except Exception as e:
    error_in_insert = True
    db.session.rollback()
    print(f'Exception "{e}" in create_venue_submission()')
  finally:
    db.session.close()
  
  if not error_in_insert:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print("Error in create_venue_submission()")
      # internal server error
    abort(500)
    
  

@app.route('/venues/<venue_id>', methods=['DELETE'])

def delete_venue(venue_id):
  try:
    myVenue = Venue.query.filter_by(id=venue_id).first()
    venueName = myVenue.name
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + venueName + ' was successfully deleted!')
  except:
    print('deu ruim')
    db.session.rollback()
  finally: 
    db.session.close()
  print('checkpoint1')
  return jsonify({'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  allArtists = Artist.query.all()
  data = []
  for artist in allArtists:
    data.append({"id" : artist.id, "name": artist.name})

  return render_template('pages/artists.html', artists=data);

@app.route('/artists/search', methods=['POST'])
def search_artists():
  s_keyword = request.form.get('search_term','')
  allArtists = Artist.query.all()
  allShows = Show.query.all()
  data = []
  i, count = 0
  
  for artist in allArtists:
    if (s_keyword.lower() in artist.name.lower()):
      count += 1
      for show in allShows:
        if (show.artist_id == artist.id & show.startTime > datetime.utcnow):
          i += 1
      data.append({"id": artist.id, "name": artist.name, "num_upcoming_shows":i})
    response = {"count":count, "data": data}
    
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  
  artist_shows = Show.query.filter_by(artist_id=artist_id).all()
  pastShowsCount = nextShowsCount = 0
  pastShows = nextShows = []
  
  for show in artist_shows:
    
    if show.startTime < datetime.utcnow:
      nextShowsCount +=1
      nextShows.append({"artist_id" : artist.id, "artist_name": artist.name, "artist_image_link" : artist.image_link,
                    "start_time" : show.startTime})
    else:
      pastShowsCount +=1
      pastShows.append({"artist_id" : artist.id, "artist_name": artist.name, "artist_image_link" : artist.image_link,
                    "start_time" : show.startTime})
      
  aux = artist.genres.split(",")
  genres = []
  for genre in aux:
    replacing = genre.replace("{","")
    replacing = replacing.replace("}","")
    genres.append(replacing)
  
  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": genres, 
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_talent,
    "seeking_description": artist.seeking_desc,
    "image_link": artist.image_link,
    "past_shows":pastShows,
    "upcoming_shows": nextShows,
    "past_shows_count": pastShowsCount,
    "upcoming_shows_count": nextShowsCount,
  }   
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  print(artist.looking_talent)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()
  # aartist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  name = form.name.data.strip()
  genres = form.genres.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  website = form.website_link.data
  facebook = form.facebook_link.data
  seeking = form.seeking_venue.data
  description = form.seeking_description.data
  image = form.image_link.data
  
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('edit_artist_submission'))
  else:
    error_in_edit = False
  
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    novoArtista = Artist(id=artist_id, name = name, genres = genres, city = city, state = state, 
                         image_link = image, phone = phone, website_link = website, 
                         facebook_link = facebook, looking_talent = seeking, seeking_desc = description)
    
    Artist.query.filter_by(id=artist_id).delete()
    
    db.session.add(novoArtista)
    db.session.commit()
  
  except Exception as e:
    error_in_edit = True
    db.session.rollback()
    print(f'Exception "{e}" in edit_artist_submission()')
    
  finally:
    db.session.close()
    
  if not error_in_edit:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print("Error in edit_artist_submission()")
      # internal server error
    abort(500)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  
  name = form.name.data
  city = form.city.data
  state = form.state.data
  address = form.address.data
  phone = form.phone.data
  image_link = form.image_link.data
  facebook_link = form.facebook_link.data
  website_link = form.website_link.data
  genres = form.genres.data
  looking_talent = form.seeking_talent.data
  seeking_desc = form.seeking_description.data
  
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('edit_venue_submission'))
  else:
    error_in_edit = False
  try:
    newVenue = Venue(id = venue_id,name=name,city=city,state=state, address=address, phone=phone,genres=genres,
      image_link=image_link, facebook_link=facebook_link, website_link=website_link, looking_talent=looking_talent,seeking_desc=seeking_desc)

    Venue.query.filter_by(id=venue_id).delete()
    
    db.session.add(newVenue)
    db.session.commit()
  
  except Exception as e:
    error_in_edit = True
    db.session.rollback()
    print(f'Exception "{e}" in edit_venue_submission()')
  
  finally:
    db.session.close()
    
  if not error_in_edit:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    print("Error in edit_venue_submission()")
      # internal server error
    abort(500)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  
  name = form.name.data.strip()
  genres = form.genres.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  website = form.website_link.data
  facebook = form.facebook_link.data
  seeking = form.seeking_venue.data
  description = form.seeking_description.data
  image = form.image_link.data
  
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('create_artist_submission'))
  else:
    error_in_create = False
    
  try:
    artista = Artist(name = name, genres = genres, city = city, state = state, 
                         image_link = image, phone = phone, website_link = website, 
                         facebook_link = facebook, looking_talent = seeking, seeking_desc = description)
  
    db.session.add(artista)
    db.session.commit()
  
  except Exception as e:
    error_in_create = True
    db.session.rollback()
    print(f'Exception "{e}" in create_artist_submission()')
  
  finally:
    db.session.close()
    
  if not error_in_create:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print("Error in artist_venue_submission()")
      # internal server error
    abort(500)    

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  for show in Show.query.all():
    time = show.startTime
    artist = Artist.query.filter_by(id=show.artist_id).first()
    venue = Venue.query.filter_by(id=show.venue_id).first()
    aux = {"venue_id":venue.id, "venue_name":venue.name, "artist_id":artist.id, "artist_name" :artist.name,
           "artist_image_link":artist.image_link, "start_time": str(time)}
    data.append(aux)
  # data = Show.query.all()
  # print(data)
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  
  venue_id = form.venue_id.data
  artist_id = form.artist_id.data
  start_time = form.start_time.data
  if not form.validate():
    flash(form.errors)
    # print(form.data)
    return redirect(url_for('create_show_submission'))
  else:
    error_in_show = False
    # print(form.data)
  try:
    
    show = Show(venue_id=venue_id, artist_id = artist_id, startTime = start_time)
    
    db.session.add(show)
    db.session.commit()
  except Exception as e:
    error_in_show = True
    db.session.rollback()
    print(f'Exception "{e}" in create_show_submission()')
  finally:
    db.session.close()
  
  if not error_in_show:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('An error occurred. Show for Artist ' + request.form['artist_id'] + ' in Venue' + request.form['venue_id'] +'could not be listed.')
    print("Error in create_show_submission()")
      # internal server error
    abort(500)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
