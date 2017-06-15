from router import db, bcrypt, login_manager

@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id==userid).first()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    googleAccessToken  = db.Column(db.String(256), unique=True)
    googleRefreshToken = db.Column(db.String(256), unique=True)
    googleTokenExpiry  = db.Column(db.String(128))
    googleTokenURI     = db.Column(db.String(128))
    googleRevokeURI    = db.Column(db.String(128))
    googleEmailAccess  = db.Column(db.Boolean)
    wunderListToken    = db.Column(db.String(256), unique=True)
    wunderListAccess   = db.Column(db.Boolean)
    wunderListId       = db.Column(db.String(256))
    lastBackupTime     = db.Column(db.DateTime)
    labels             = db.relationship("Label", backref="user", lazy='dynamic')
    
    def __repr__(self):
        return '<User %r>' % self.email

    def save(self):
        db.session.add(self)
        db.session.commit()

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

class Label(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    label_id = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_message_read = db.Column(db.String(128))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Label %r User %s>' % (self.id,self.user.email)