# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from sqlalchemy import text
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import func
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
db = SQLAlchemy(app,session_options={'expire_on_commit':False})
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

from Models import *

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
    format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
    format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  CityList = Venue.query.distinct(Venue.city, Venue.state)

  data = []

  for item in CityList:
    allVenue = Venue.query.filter_by(state=item.state).filter_by(city=item.city)

    venues = []
    for ven in allVenue:
      query = Show.query.filter_by(Venue_Id=ven.id).filter(Show.Date > datetime.utcnow())
      venues.append({
        "id": ven.id,
        "name": ven.name,
        "num_upcoming_shows": query.count()
      })
    data.append({
      "city": item.city,
      "state": item.state,
      "venues": venues
    })

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venueName = request.form.get('search_term')


  Venuedata = Venue.query.filter(Venue.name.ilike("%" + venueName + "%"))
  response = {
    "count": Venuedata.count(),
  }
  data = []
  for ven in Venuedata:
    data.append({
      "id": ven.id,
      "name": ven.name,
      "num_upcoming_shows": Show.query.filter_by(Venue_Id=ven.id).filter(Show.Date > datetime.utcnow()).count()
    })

  response["data"] = data

  return render_template('pages/search_venues.html', results=response,
                         search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venuedata = Venue.query.filter_by(id=venue_id)[0]
  if venuedata == None:
      return abort(404)
  past_shows = []
  upcoming_shows = []
  ShowArtist = Show.query.filter_by(Venue_Id=venue_id).filter(Show.Date < datetime.utcnow())
  for past_show in ShowArtist:
    past_shows.append({
      "artist_id": past_show.Artist_Id,
      "artist_name": Artist.query.filter_by(id=past_show.Artist_Id)[0].name,
      "artist_image_link": Artist.query.filter_by(id=past_show.Artist_Id)[0].image_link,
      "start_time": str(past_show.Date)
    })

  ShowArtist = Show.query.filter_by(Venue_Id=venue_id).filter(Show.Date > datetime.utcnow())
  for upShow in ShowArtist:
    upcoming_shows.append({
      "artist_id": upShow.Artist_Id,
      "artist_name": Artist.query.filter_by(id=upShow.Artist_Id)[0].name,
      "artist_image_link": Artist.query.filter_by(id=upShow.Artist_Id)[0].image_link,
      "start_time": str(upShow.Date)
    })

  QueryGenres=VenueGenres.query.filter_by(Venue_id=venue_id)

  data = {
    "id": venuedata.id,
    "name": venuedata.name,
    "genres": QueryGenres,
    "address": venuedata.address,
    "city": venuedata.city,
    "state": venuedata.state,
    "phone": venuedata.phone,
    "website": venuedata.website,
    "facebook_link": venuedata.facebook_link,
    "seeking_talent": venuedata.seeking_talent,
    "seeking_description": venuedata.seeking_description,
    "image_link": venuedata.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows) ,
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  seeking_talent=False
  seeking_description=''
  if request.form.get('seeking_talent')=='y':
    seeking_talent=True
    seeking_description=request.form.get('seeking_description')

  image_link=request.form.get('image_link')
  if ('https://' not in image_link):
    image_link='https://'+image_link

  facebook_link=request.form.get('facebook_link')
  if ('http://' not in facebook_link):
    facebook_link='http://'+facebook_link
  website=request.form.get('website')
  if 'http://' not in website:
    website='http://'+website



  venue = Venue(name=request.form.get('name'),seeking_talent=seeking_talent,seeking_description=seeking_description,
                website=website ,city=request.form.get('city'), state=request.form.get('state'),
                address=request.form.get('address'),image_link=image_link,
                phone=request.form.get('phone'), facebook_link=facebook_link)
  try:

    error = False
    db.session.add(venue)
    db.session.commit()
    listOfGenres=request.form.getlist('genres')
    for item in listOfGenres:
      venueGenre=VenueGenres(genres=item,Venue_id=venue.id)
      db.session.add(venueGenre)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error == True:
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    data = Venue.query.filter_by(id=venue_id)
    data.delete()
    data=Show.query.filter_by(Venue_Id=venue_id)
    data.delete()
    data=VenueGenres.query.filter_by(Venue_id=venue_id)
    data.delete()
    db.session.commti()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  query = Artist.query.all()
  for row in query:
    data.append({
      "id": row.id,
      "name": row.name
    })


  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

   query = Artist.query.filter(Artist.name.ilike("%" + request.form.get('search_term') + "%"))
   data = []
   print(query)
   for row in query:
    data.append({
      "id": row.id,
      "name": row.name,
      "num_upcoming_shows": Show.query.filter_by(Artist_Id=row.id)
    })

    response = {
       "count": query.count(),
       "data": data
    }


    return render_template('pages/search_artists.html', results=response,
                         search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist=Artist.query.get(artist_id)
  pastshows = []
  upShows = []
  pastShowVenuo =  db.session.query(Show).join(Venue).filter(Show.Artist_Id==artist_id).filter(Show.Date < datetime.now())
  upShowVenuo = db.session.query(Show).join(Venue).filter(Show.Artist_Id==artist_id).filter(Show.Date > datetime.now())

  for past in pastShowVenuo:

    pastshows.append({
      "venue_id": past.Venue_Id,
      "venue_name": past.Venue.name,
      "venue_image_link": past.Venue.image_link,
      "start_time": str(past.Date)
    })

  for upshow in upShowVenuo:

    upShows.append({
      "venue_id": upshow.Venue_Id,
      "venue_name": upshow.Venue.name,
      "venue_image_link": upshow.Venue.image_link,
      "start_time": str(upshow.Date)
    })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastshows,
    "upcoming_shows": upShows,
    "past_shows_count": len(pastshows),
    "upcoming_shows_count": len(upShows),
  }

  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  artist = {
    "id": artist.id,
    "name": artist.name,
    "genres": ArtistGenres.query.filter_by(artist_id=artist_id),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_talent": artist.seeking_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error=False
  artist=Artist.query.get(artist_id)
  try:
    error=False

    ArtistGenres.query.filter_by(artist_id=artist_id).delete()
    db.session.commit()
    ListGenres=request.form.getlist('genres')
    for genre in ListGenres:
      artistGenres=ArtistGenres(artist_id=artist_id,genres=genre)
      db.session.add(artistGenres)

    db.session.commit()
    if artist.name != request.form.get('name') and request.form.get('name')!='':
      artist.name=request.form.get('name')
    if artist.city != request.form.get('city') and request.form.get('city')!='':
      artist.city=request.form.get('city')
    if artist.state != request.form.get('state') and request.form.get('state')!='':
      artist.state=request.form.get('state')


    if artist.phone != request.form.get('phone') and request.form.get('phone')!='':
      artist.phone=request.form.get('phone')

    if artist.image_link != request.form.get('image_link'):
      image_link=request.form.get('image_link')
      if 'https://' in image_link:
        artist.image_link=image_link
      else:
        artist.image_link='https://'+image_link

    if artist.facebook_link != request.form.get('facebook_link'):
      facebook_link=request.form.get('facebook_link')
      if 'http://' in facebook_link :
        artist.facebook_link=facebook_link
      else:
        artist.facebook_link='http://'+facebook_link

    if artist.website != request.form.get('website'):
      website=request.form.get('website')
      if 'http://' in website :
        artist.website=website
      else:
        artist.website='http://'+website

    if artist.seeking_talent != request.form.get('seeking_talent') and request.form.get('seeking_talent')=='y':
      artist.seeking_talent=True
      if artist.seeking_description != request.form.get('seeking_description') :
        artist.seeking_description=request.form.get('seeking_description')
    if artist.seeking_talent != request.form.get('seeking_talent') and request.form.get('seeking_talent')!='y':
      artist.seeking_talent=False
      artist.seeking_description=''


    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error==True:
    flash('An error occurred. Artist ' + Artist.query.get(artist_id).name + ' could not be Edit.')
  else:
    flash('Artist ' + Artist.query.get(artist_id).name + ' was successfully Edit!')
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  VenueQuery=Venue.query.get(venue_id)
  ListGenres=VenueGenres.query.filter_by(Venue_id=venue_id)
  venue = {
    "id": venue_id,
    "name": VenueQuery.name,
    "genres": ListGenres,
    "address": VenueQuery.address,
    "city": VenueQuery.city,
    "state": VenueQuery.state,
    "phone": VenueQuery.phone,
    "website": VenueQuery.website,
    "facebook_link": VenueQuery.facebook_link,
    "seeking_talent": VenueQuery.seeking_talent,
    "seeking_description": VenueQuery.seeking_description ,
    "image_link": VenueQuery.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error=False
  venue=Venue.query.get(venue_id)
  try:
    error=False
    VenueGenres.query.filter_by(Venue_id=venue_id).delete()
    db.session.commit()
    ListGenres=request.form.getlist('genres')
    for genre in ListGenres:
      venueGenres=VenueGenres(Venue_id=venue_id,genres=genre)
      db.session.add(venueGenres)

    db.session.commit()
    if venue.name != request.form.get('name') and request.form.get('name')!='':
      venue.name=request.form.get('name')
    if venue.city != request.form.get('city') and request.form.get('city')!='':
      venue.city=request.form.get('city')
    if venue.state != request.form.get('state') and request.form.get('state')!='':
      venue.state=request.form.get('state')
    if venue.phone != request.form.get('phone') and request.form.get('phone')!='':
      venue.phone=request.form.get('phone')
    if venue.image_link != request.form.get('image_link'):
      image_link=request.form.get('image_link')
      if 'http://' in image_link:
        venue.image_link=image_link
      else:
        venue.image_link='http://'+image_link
    if venue.facebook_link != request.form.get('facebook_link'):
      facebook_link=request.form.get('facebook_link')
      if 'http://' in facebook_link :
        venue.facebook_link=facebook_link
      else:
        venue.facebook_link='http://'+facebook_link

    if venue.website != request.form.get('website'):
      website=request.form.get('website')
      if 'http://' in website :
        venue.website=website
      else:
        venue.website='http://'+website

    if   request.form.get('seeking_talent')=='y':
      venue.seeking_talent=True
      venue.seeking_description=request.form.get('seeking_description')
    if   request.form.get('seeking_talent')!='y':
      venue.seeking_talent=False
      venue.seeking_description=''
    db.session.commit()
  except:
    error=True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  if error==True:
    flash('An error occurred. Venue ' + Venue.query.get(venue_id).name + ' could not be Edit.')
  else:
    flash('Venue ' + Venue.query.get(venue_id).name + ' was successfully Edit!')



  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  seeking_talent=False
  seeking_description=''
  if request.form.get('seeking_talent') == 'y':
    seeking_talent=True
    seeking_description=request.form.get('seeking_description')
  image_link=request.form.get('image_link')
  if ('https://' not in image_link):
    image_link='https://'+image_link

  facebook_link=request.form.get('facebook_link')
  if ('http://' not in facebook_link):
    facebook_link='http://'+facebook_link

  website=request.form.get('website')
  if 'http://' not in website:
    website='http://'+website

  artist = Artist(name=request.form.get('name'), city=request.form.get('city'), state=request.form.get('state'),
                  phone=request.form.get('phone'),image_link=image_link,website=website,
                  seeking_talent=seeking_talent,seeking_description=seeking_description, facebook_link=facebook_link)
  try:
    error = False
    db.session.add(artist)
    db.session.commit()
    listOfGenres=request.form.getlist('genres')
    for item in listOfGenres:
      artistGenre=ArtistGenres(genres=item,artist_id=artist.id)
      db.session.add(artistGenre)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error == True:
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  AllShow=Show.query.all()
  for row in AllShow:
    print('row', row.Artist_Id)
    queryVenue=Venue.query.filter_by(id=row.Venue_Id).all()[0]
    queryArtist=Artist.query.filter_by(id=row.Artist_Id).all()[0]

    data.append({
      "venue_id": queryVenue.id,
      "venue_name": queryVenue.name,
      "artist_id": queryArtist.id,
      "artist_name": queryArtist.name,
      "artist_image_link": queryArtist.image_link,
      "start_time": str(row.Date)
    })

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
  NewShow=Show(Venue_Id=request.form.get('venue_id'),Artist_Id=request.form.get('artist_id'),Date=request.form.get('start_time'))
  error=False
  try:
    error=False
    db.session.add(NewShow)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else :
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
