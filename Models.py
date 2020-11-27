#import part
from app import db

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.relationship('VenueGenres',backref='Venue')
    image_link = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=True, nullable=True)
    facebook_link = db.Column(db.String(120), nullable=False)
    seeking_description = db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f'{self.id} ,{self.name},{self.city},{self.state},{self.address},{self.phone},{self.genres},{self.image_link},' \
               f'{self.seeking_talent},{self.website},facebook:=> {self.facebook_link},{self.seeking_description} '

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class VenueGenres(db.Model):
    __tablename__='VenueGenres'

    genres_id=db.Column(db.Integer,primary_key=True)
    genres=db.Column(db.String(),nullable=False)
    Venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)

    def __repr__(self):
        return f'id: {self.genres_id} , Genres: {self.genres} , Venue id: {self.Venue_id}'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    genres = db.relationship('ArtistGenres',backref='Artist')
    image_link = db.Column(db.String(500))
    seeking_description = db.Column(db.String())
    facebook_link = db.Column(db.String(120), nullable=False)
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
        return f'{self.id} ,{self.name},{self.city},{self.state},{self.phone},{self.genres},{self.image_link},         ' \
               f'{self.seeking_talent}  ,   {self.website},facebook:=> {self.facebook_link},       {self.seeking_description} '

class ArtistGenres(db.Model):
    __tablename__='ArtistGenres'

    genres_id=db.Column(db.Integer,primary_key=True)
    genres=db.Column(db.String(),nullable=False)
    artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)

    def __repr__(self):
        return f'id: {self.genres_id} , Genres: {self.genres} , Venue id: {self.artist_id}'



class Show(db.Model):
    __tablename__ = 'Show'

    id_show = db.Column(db.Integer, primary_key=True)
    Venue_Id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    Artist_Id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    Date = db.Column(db.DateTime, nullable=False)



