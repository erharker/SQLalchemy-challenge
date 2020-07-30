#dependencies
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



app= Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Hawaii Climate Analysis<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    session.close()

    all_prcp_dates=[]
    for date, prcp in results:
        rain_dict={}
        rain_dict["date"]=date
        rain_dict["prcp"]=prcp
        all_prcp_dates.append(rain_dict)
    
    return jsonify(all_prcp_dates)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    stations = session.query(Station.name).filter(Measurement.station == Station.station).group_by(Measurement.station).all()
    session.close()
    station_list=list(np.ravel(stations))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session=Session(engine)
    temp_data = (session.query(Measurement.date, Measurement.tobs).\
        order_by(Measurement.date).\
        filter(Measurement.date >= year_ago).\
        filter((Measurement.station) == "USC00519281")
        .all())
    session.close()
    temp_list=list(np.ravel(temp_data))
    return jsonify(temp_data)   

@app.route("/api/v1.0/YYYY-MM-DD<start_date>")
def start(start_date):
    session=Session(engine)
    return_temps= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()
    return jsonify(return_temps) 

@app.route("/api/v1.0/YYYY-MM-DD<start_date>/<end_date>")
def startend(start_date, end_date):
    session=Session(engine)
    return_temps= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    return jsonify(return_temps) 


# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
