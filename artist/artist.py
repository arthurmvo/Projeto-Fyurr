from flask import (
    Blueprint,
    render_template, 
    request, 
    flash, 
    redirect,
    url_for,
    abort,
)
from models import Venue, Show, Artist, db
from datetime import datetime
from forms import *

artist_bp = Blueprint('artist_bp', __name__, 
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='assets')

@artist_bp.route('/artists')
def artists():
  allArtists = Artist.query.all()
  data = []
  for artist in allArtists:
    data.append({"id" : artist.id, "name": artist.name})

  return render_template('pages/artists.html', artists=data);

@artist_bp.route('/artists/search', methods=['POST'])
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
        if (show.artist_id == artist.id) & (show.startTime > datetime.utcnow()):
          i += 1
      data.append({"id": artist.id, "name": artist.name, "num_upcoming_shows":i})
    response = {"count":count, "data": data}
    
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@artist_bp.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  
  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
  filter(
      Show.artist_id == artist_id,
      Show.venue_id == Venue.id,
      Show.startTime < datetime.now()
  ).\
  all()

  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
  filter(
      Show.artist_id == artist_id,
      Show.venue_id == Venue.id,
      Show.startTime > datetime.now()
  ).\
  all()
  
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
    "past_shows":[{
            'venue_id': venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in past_shows],
    "upcoming_shows": [{
            'venue_id': venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }   

  return render_template('pages/show_artist.html', artist=data)



@artist_bp.route('/artists/<int:artist_id>/edit', methods=['POST', 'GET'])
def edit_artist(artist_id):
    if request.method == 'POST':
        
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

        try:
            new_artist = Artist(id=artist_id, name = name, genres = genres, city = city, state = state, 
                                image_link = image, phone = phone, website_link = website, 
                                facebook_link = facebook, looking_talent = seeking, seeking_desc = description)
            
            Artist.query.filter_by(id=artist_id).delete()
            
            db.session.add(new_artist)
            db.session.commit()
        
        except Exception as e:
            error_in_edit = True
            db.session.rollback()
            print(f'Exception "{e}" in edit_artist()')
            
        finally:
            db.session.close()
            
        if not error_in_edit:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('artist_bp.show_artist', artist_id=artist_id))
        else:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            print("Error in edit_artist()")
            # internal server error
            abort(500)
    else:
            form = ArtistForm()
            artist = Artist.query.filter_by(id=artist_id).first()
            form.genres.data = artist.genres
            return render_template('forms/edit_artist.html', form=form, artist=artist)
                    


@artist_bp.route('/artists/create', methods=['POST', 'GET'])
def create_artist():
  if request.method == 'POST':
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
        return redirect(url_for('create_artist'))
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
        print(f'Exception "{e}" in create_artist()')
    
    finally:
        db.session.close()
        
    if not error_in_create:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))
    else:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        print("Error in artist_venue_submission()")
        # internal server error
        abort(500)    
  else:
      form = ArtistForm()
      return render_template('forms/new_artist.html', form=form)