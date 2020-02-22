from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo

# import scrape file
import scrape_mars

app = Flask(__name__)

# use flask_pymongo to set up a mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

@app.route("/")
def index():
    mars_info = mongo.db.mars_info.find_one()
    return render_template("index.html", mars_info=mars_info)

@app.route("/scrape")
def scraper():
    mongo.db.mars_info.remove()
    mars_info = mongo.db.mars_info
    mars_data = scrape_mars.scrape()
    mars_info.update({}, mars_data, upsert=True)
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)