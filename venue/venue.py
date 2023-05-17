from flask import (
    Blueprint,
    render_template, 
    request, 
    flash, 
    redirect,
    url_for,
    abort,
    jsonify
)
from models import Venue, Show, Artist, db
from datetime import datetime
from forms import *
import sys

venue_bp = Blueprint('venue_bp', __name__, 
                    template_folder='templates')

@venue_bp.route('/venues')
def venues():  
  # Querying for cites and states of all venues and unique them
  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  response = []
  for area in areas:
    result = Venue.query.filter(Venue.state == area.state).filter(Venue.city == area.city).all()
    venue_data = []

    # Creating venues' response
    for venue in result:
      
      venue_data.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(db.session.query(Show).filter(Show.startTime > datetime.now()).all())
        })

    response.append({
      'city': area.city,
      'state': area.state,
      'venues': venue_data
      })

  return render_template('pages/venues.html', areas=response)

@venue_bp.route('/venues/search', methods=['POST'])
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
        if (show.venue_id == venue.id) & (show.startTime > datetime.utcnow()):
          i += 1
      data.append({"id" : venue.id, "name" : venue.name, "num_upcoming_shows" : i})
    response = {"count" : count, "data" : data}
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@venue_bp.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.startTime < datetime.now()
    ).\
    all()
  
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.startTime > datetime.now()
    ).\
    all()

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
    "past_shows":[{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
    "upcoming_shows": [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }   
  
  # print(data) 

  return render_template('pages/show_venue.html', venue=data)


@venue_bp.route('/venues/create', methods=['POST', 'GET'])
def create_venue():
  if request.method == 'POST':
          
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
        return redirect(url_for('create_venue'))
    else:
        error_in_insert = False
        # print(form.data)


    try:
        print('entrou no try')
        venue = Venue(
        name=name,city=city,state=state, address=address, phone=phone,genres=genres,
        image_link=image_link, facebook_link=facebook_link, website_link=website_link, looking_talent=looking_talent,seeking_desc=seeking_desc)
        
        db.session.add(venue)
        db.session.commit()

    except:
        print(sys.exc_info())
        error_in_insert = True
        db.session.rollback()
    finally:
        db.session.close()
    
    if not error_in_insert:
        print('Venue ' + request.form['name'] + ' was successfully listed!')
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))
    else:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        print("Error in create_venue()")
        # internal server error
        abort(500)
  else:
      form = VenueForm()
      print("abriu o formulario")
      return render_template('forms/new_venue.html', form=form)


@venue_bp.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    my_venue = Venue.query.filter_by(id=venue_id).first()
    venue_name = my_venue.name
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + venue_name + ' was successfully deleted!')
  except:
    print('deu ruim')
    db.session.rollback()
  finally: 
    db.session.close()
  return jsonify({'success': True })


@venue_bp.route('/venues/<int:venue_id>/edit', methods=['POST', 'GET'])
def edit_venue(venue_id):
    if request.method == 'POST':
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
        print(looking_talent)
        seeking_desc = form.seeking_description.data
        
        if not form.validate():
            flash(form.errors)
            return redirect(url_for('edit_venue'))
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
            print(f'Exception "{e}" in edit_venue()')
        
        finally:
            db.session.close()
            
        if not error_in_edit:
            flash('Venue ' + request.form['name'] + ' was successfully edited!')
            return redirect(url_for('venue_bp.show_venue', venue_id=venue_id))
        else:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
            print("Error in edit_venue_submission()")
            # internal server error
            abort(500)
    else:
        form = VenueForm()
        venue = Venue.query.filter_by(id=venue_id).first()
        form.genres.data = venue.genres
        return render_template('forms/edit_venue.html', form=form, venue=venue)        
    
