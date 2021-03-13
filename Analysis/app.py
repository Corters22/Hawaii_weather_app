import numpy as np
import datetime as dt
from datetime import timedelta, datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    print("List all available API routes")
    return (
        f'<h1>Hawaiian weather API from 1/1/2010-8/23/2017</h1>'
        f'<h2>Available routes:</h2>'
        f'1. For precipitation levels for each day between 8/23/2016 and 8/23/2017<br/>'
        f'<a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a><br/><br/>'
        f'2. For a list of stations:<br/>'
        f'<a href="/api/v1.0/stations">/api/v1.0/stations</a><br/><br/>'
        f'3. For temperature observation for station USC00519281 for each day between 8/23/2016 and 8/23/2017:<br/>'
        f'<a href="/api/v1.0/tobs">/api/v1.0/tobs</a><br/><br/>'
        f'4. For the minimum, maximum and average temperature for your choice of start date until 8/23/2017:<br/>'
        f'<small>Hint: the date must be in YYYY-MM-DD format</small><br/>'
        f'<a href="/api/v1.0/">/api/v1.0/<i>start_date</i></a><br/><br/>'
        f'5. For the minimum, maximum and average temperature for your choice of start and end dates:<br/>'
        f'<small>Hint: the dates must be in YYYY-MM-DD format and the be within the available dates 2010-01-01 and 2017-08-23.</small><br/>'
        f'<a href="/api/v1.0/">/api/v1.0/<i>start_date</i>/<i>end_date</i></a>'
    )

@app.route('/api/v1.0/precipitation')
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    print('prcp dictionary')
    #Query all prcp levels by date
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    
    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value
    date_list = []
    prcp_list = []
    for date, prcp in results:
        date_list.append(date)
        prcp_list.append(prcp)

    prcp_dict = dict(zip(date_list, prcp_list))

    return jsonify(prcp_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query all stations
    results = session.query(Station.station).all() 
    session.close()  

    all_stations = list(np.ravel(results))
    #Return a JSON list of stations from the dataset
    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def temp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query most recent date
    max_date = session.query(func.max(Measurement.date)).first()
    #Convert date to datetime from string
    x= datetime.strptime(max_date[0], '%Y-%m-%d')
    #Get the date 1 year from most recent date
    min_date = x - dt.timedelta(days=365)
    #Convert date back to string
    min_date = min_date.strftime('%Y-%m-%d')
    #Query all dates and temperature observations of the most active station for the last year of data
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=min_date)

    session.close()
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    tobs_list = []
    for date, tobs in results:
        tobs_dict =  {}
        tobs_dict['date'] = date
        tobs_dict['temp observ'] = tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start_date>')
def date(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Return a JSON list of the minimum temperature, the average temperature,
    # and the max temperature for a given start or start-end range
    tmax = session.query(func.max(Measurement.tobs)).filter(Measurement.date>= start_date).scalar()
    tmin = session.query(func.min(Measurement.tobs)).filter(Measurement.date>= start_date).scalar()
    tavg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>= start_date).scalar()

    session.close()

    start_date_dict = {'Maximum temperature': tmax,
                        'Minimum temperature': tmin,
                        'Average temperature': tavg}

    return jsonify(start_date_dict)
        
@app.route('/api/v1.0/<start_date>/<end_date>')
def range_date(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Return a JSON list of the minimum temperature, the average temperature,
    # and the max temperature for a given start or start-end range
    tmax = session.query(func.max(Measurement.tobs)).filter(Measurement.date>= start_date).\
        filter(Measurement.date<= end_date).scalar()
    tmin = session.query(func.min(Measurement.tobs)).filter(Measurement.date>= start_date).\
        filter(Measurement.date<= end_date).scalar()
    tavg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>= start_date).\
        filter(Measurement.date<= end_date).scalar()

    session.close()

    range_date_dict = {'Maximum temperature': tmax,
                        'Minimum temperature': tmin,
                        'Average temperature': tavg}

    return jsonify(range_date_dict)

if __name__ == '__main__':
    app.run(debug=True)    

