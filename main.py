import os

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_url_path="/static")

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


class CafeForm(FlaskForm):
    name = StringField(u'Name:', validators=[DataRequired()])
    map_url = StringField(u'Map url', validators=[DataRequired(), URL()])
    img_url = StringField(u'Img url', validators=[DataRequired(), URL()])
    location = StringField(u'Location:', validators=[DataRequired()])
    has_sockets = BooleanField(u'Has Sockets:')
    has_toilet = BooleanField(u'Has Toilets:')
    has_wifi = BooleanField(u'Has Wifi:')
    can_take_calls = BooleanField(u'can take calls:')
    seats = StringField(u'Seats:', validators=[DataRequired()])
    coffee_price = StringField(u'Coffee price: ', validators=[DataRequired()])
    submit = SubmitField(u'Submit')


class EditForm(FlaskForm):
    new_coffee_price = StringField(u'Coffee price: ', validators=[DataRequired()])
    submit = SubmitField(u'Submit')


class cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.String(255), nullable=False)
    coffee_price = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary

    def __repr__(self):
        return f'<Cafe {self.name}>'


ROWS_PER_PAGE = 3


@app.route('/', methods=["GET", "POST"])
def home():
    page = request.args.get('page', 1, type=int)
    cafes = cafe.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('index.html', cafes=cafes)


@app.get("/cafes/cafe")
def get_specific_cafes():
    query_param = request.args.get("q")
    all_cafes = [cafe_name.to_dict() for cafe_name in cafe.query.all()]
    results = []
    for cafe_name in all_cafes:
        if cafe_name[f"{query_param}"] == 1:
            results.append(cafe_name)
    return render_template("index.html", results=results, query=query_param.split("_")[-1].upper())


@app.route("/add", methods=["GET", "POST"])
def add():
    form = CafeForm()
    if form.validate_on_submit() and request.method == "POST":
        add_cafe = cafe(name=form.name.data, map_url=form.map_url.data, img_url=form.img_url.data,
                        location=form.location.data, has_sockets=form.has_sockets.data, has_toilet=form.has_toilet.data,
                        has_wifi=form.has_wifi.data, can_take_calls=form.can_take_calls.data, seats=form.seats.data,
                        coffee_price=form.coffee_price.data)
        db.session.add(add_cafe)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add.html', form=form)


@app.route("/edit", methods=['GET', 'POST'])
def edit_coffee_price():
    edit_form = EditForm()
    if edit_form.validate_on_submit() and request.method == "POST":
        cafe_id = request.args.get('id')
        query_to_update = cafe.query.get(cafe_id)
        query_to_update.coffee_price = f"₹{edit_form.new_coffee_price.data}"
        db.session.commit()
        print(query_to_update.coffee_price)
        return redirect(url_for('home'))

    cafe_id = request.args.get('id')
    book_query = cafe.query.get(cafe_id)
    print(book_query)
    return render_template('edit_coffee_price.html', form=edit_form, cafe=book_query)


@app.route('/delete', methods=['GET', 'POST'])
def delete_entry():
    cafe_id = request.args.get('id')
    query_to_delete = cafe.query.get(cafe_id)
    db.session.delete(query_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.get("/cafes/cafe/<int:cafe_id>")
def show_cafe(cafe_id):
    cafe_to_show = None
    all_cafes = [cafe_name.to_dict() for cafe_name in cafe.query.all()]
    for cafe_name in all_cafes:
        if cafe_name["id"] == cafe_id:
            cafe_to_show = cafe_name
    return render_template("cafe.html", cafe=cafe_to_show, cafe_name=cafe_to_show["name"])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
#     app.run(debug=True)
    db.create_all()
