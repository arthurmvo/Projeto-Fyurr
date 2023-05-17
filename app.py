#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
import collections
collections.Callable = collections.abc.Callable # Had to do that because I was getting an error on the collections module in python 3.11 version.
from flask import render_template
from flask_moment import Moment
import logging
from config import DatabaseURI
from logging import Formatter, FileHandler
from forms import *
from models import app, db, Artist, Venue
from sqlalchemy import desc
from artist.artist import artist_bp
from show.show import show_bp
from venue.venue import venue_bp

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object(DatabaseURI)
moment = Moment(app)
db.init_app(app)


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
# Blueprints.
#----------------------------------------------------------------------------#

app.register_blueprint(artist_bp, url_prefix = '/artists')
app.register_blueprint(venue_bp, url_prefix = '/venue')
app.register_blueprint(show_bp, url_prefix = '/show')


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venues = Venue.query.order_by(desc(Venue.created_date)).limit(10).all()
  artists = Artist.query.order_by(desc(Artist.created_date)).limit(10).all()
  return render_template('pages/home.html', venues=venues, artists=artists)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
  
@app.errorhandler(400)
def server_error(error):
    return render_template('errors/400.html'), 400
  
@app.errorhandler(405)
def server_error(error):
    return render_template('errors/405.html'), 405


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
