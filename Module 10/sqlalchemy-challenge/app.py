from flask import Flask, jsonify
import numpy as np 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

###2:Setup database and reflect the tables using sqlalchemy
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement 
Station = Base.classes.station

###3:Create an app
app = Flask(_name_)

###4:Create index/home '/' route and Define the home()
@app.route("/")
def home():
    print('Server received request for 'Home' page...")
    return(
        f"This is the Climate App that Kate created.</br>"
        f"You will find the following ROUTES on this server:</br>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>/api/v1.0/<start></li>"
        f"<li>/api/v1.0/<start>/<end></li>"
        f"<li>/about</li>"
        f"</ul>"
    )
          
###5. Define what to do when user hit the /about route
@app.route("/about")
def about(): 
    print("server received request for 'About' page...")
          return(
              f"This is created by Kate, UT Data Analysis course Module 10.</br>"
          )

###6:Create route "api/v1.0/pecipitation" to take the SQL query and return a jsonified dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Servier received request for '/api/v1.0/precipitation'.")
    
    session = Session(engine)
          
    data_prcp = session.query(Measuremetn.date, Measurement.prcp)\
          .order_by(Measurement.date.desc())\
          .filter(Measurement.date > '2016-08-23').all()
          
    session.close()
          
    prcp_dict = {}
    for date, prcp in data_prcp:
          if date not in prcp_dict:
             prcp_dict[date] = []
             prcp_dict[date].append(prcp)
          else:
             prcp_dict[date].append(prcp)
    return jsonify(prcp_dict)
          
          
###7:Create route "/api/v1.0/stations"
@app.route("/api/v1.0/stations")
def station():
    print("Servier received request for '/api/v1.0/stations'.")
    
    session = Session(engine) 
    
    station_names = session.query(Station.name).all()
    
    session.close()

    return jsonify(station_names)
          
### 8. Create route "<li>/api/v1.0/tobs</li>"
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for '/api/v1.0/tobs'.")
     
    session = Session(engine) 
    
    station_12months = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == 'USC00519281')\
        .filter(Measurement.date >= '2016-08-23').all()
    
    session.close()

    # Print the temp data from the most active station from the last year
    station_list = list(np.ravel(station_12months))

    return jsonify(station_list)

### 9. Create route "/api/v1.0/<start>"
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def date_starts(start):
    print("Server received request for '/api/v1.0/<start>'.")
     
    session = Session(engine) 
    
    # Lowest, avgerage, and highest temperature query
    station_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.station == 'USC00519281')\
        .filter(Measurement.date >= start).first()
    
    session.close()

    
    temps_dict = {"Low Temp": station_results[0], "Average Temp": station_results[1], "Hi Temp": station_results[2]}

    return jsonify(temps_dict)

### 10. Create route "/api/v1.0/<start>/<end>"
@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    print("Server received request for '/api/v1.0/<start>/<end>'.")
     
    session = Session(engine) 
    # Query start date, end date, and TOBS data from database and then turn into a dictionary
    station_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.station == 'USC00519281')\
        .filter(Measurement.date <= end)\
        .filter(Measurement.date >= start).first()
   
    session.close()

    # Create dictionary to output
    temps_dict = {"Low Temp": station_results[0], "Average Temp": station_results[1], "Hi Temp": station_results[2]}

    return jsonify(temps_dict)

if __name__ == '__main__':
    app.run(debug=True)