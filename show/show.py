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

show_bp = Blueprint('show_bp', __name__, 
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='assets')

@show_bp.route('/shows')
def shows():
  data = []
  for show in Show.query.all():
    time = show.startTime
    artist = Artist.query.filter_by(id=show.artist_id).first()
    venue = Venue.query.filter_by(id=show.venue_id).first()
    aux = {"venue_id":venue.id, "venue_name":venue.name, "artist_id":artist.id, "artist_name" :artist.name,
           "artist_image_link":artist.image_link, "start_time": str(time)}
    data.append(aux)
  return render_template('pages/shows.html', shows=data)

@show_bp.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@show_bp.route('/shows/create', methods=['POST'])
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