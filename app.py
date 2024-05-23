from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session link
session = Session(engine)

#Setup Flask
app = Flask(__name__)

# Define Flask Route
#Route 1: Homepage and List of Available Routes
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

#Route 2: Precipitation Data
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last 12 months."""
    # Calculate the date one year ago from the last date in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary
    precipitation_dict = dict(precipitation_data)
    
    return jsonify(precipitation_dict)

#Route 3: Stations
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset."""
    # Query all stations
    stations = session.query(Station.station).all()
    
    # Convert list of tuples into normal list
    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)

# Route 4: Temperature Observations
@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the previous year."""
    # Find the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Calculate the date one year ago from the last date in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query the temperature observations for the most active station for the last year
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    
    return jsonify(temperature_data)

# Route 5: Temperature Statistics for a Given Date Range
@app.route("/api/v1.0/<start>")
def start_stats(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start date."""
    # Query the minimum, average, and maximum temperatures for dates greater than or equal to the start date
    stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    return jsonify(stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_stats(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given date range."""
    # Query the minimum, average, and maximum temperatures for dates between the start and end dates
    stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    return jsonify(stats)

# Step 4: Run the App
if __name__ == '__main__':
    app.run(debug=True)
