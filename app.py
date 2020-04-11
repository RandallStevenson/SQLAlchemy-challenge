import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base=automap_base()
Base.prepare(engine,reflect=True)
Station=Base.classes.station
Measurement=Base.classes.measurement
session=Session(bind=engine)
max_stn='USC00519281'

from flask import Flask, jsonify
app=Flask(__name__)
fd=dt.date(2016,8,23)
@app.route("/")
def home():
    return (
        f"Routes available ... <br/><br/>"
        f"Home                      : / <br/>" 
        f"Precipitation             : /api/v1.0/precipitation <br/>"
        f"Stations                  : /api/v1.0/stations <br/>"
        f"Temperatures              : /api/v1.0/tobs <br/>"
        f"Temperatures from Date    : /api/v1.0/<start> (Use YYYY-MM-DD format) <br/>"
        f"Temperatures between Dates: /api/v1.0/<start>/<end> (Use YYYY-MM-DD format) <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Base=automap_base()
    Base.prepare(engine,reflect=True)
    Station=Base.classes.station
    Measurement=Base.classes.measurement
    session=Session(bind=engine)
    max_stn='USC00519281'
    sel=[Measurement.date,Measurement.prcp]
    prcp_query=session.query(*sel).\
        filter(Measurement.station==max_stn).\
        filter(Measurement.date<fd).all()
    prcp_df=pd.DataFrame(prcp_query,columns=['date','prcp'])
    prcp_df.set_index(prcp_df['date'],inplace=True)
    prcp_df=prcp_df.drop(['date'],axis=1)
    prcp_dict=prcp_df.to_dict()['prcp']
    session.close()
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def statns():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Base=automap_base()
    Base.prepare(engine,reflect=True)
    Station=Base.classes.station
    Measurement=Base.classes.measurement
    session=Session(bind=engine)
    max_stn='USC00519281'
    fr_stn=session.query(Station.station,Station.name)
    stn_list=pd.DataFrame(fr_stn,columns=["station","name"])
    stn_list.set_index(stn_list["station"],inplace=True)
    stn_list=stn_list.drop(["station"],axis=1)
    session.close()
    return jsonify(stn_list.to_dict()['name'])

@app.route("/api/v1.0/tobs")
def temps():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Base=automap_base()
    Base.prepare(engine,reflect=True)
    Station=Base.classes.station
    Measurement=Base.classes.measurement
    session=Session(bind=engine)
    max_stn='USC00519281'
    sel=[Measurement.date,Measurement.tobs]
    daily_temps=session.query(*sel).\
        filter(Measurement.station==max_stn).\
        filter(Measurement.date>fd).all()
    temp_df=pd.DataFrame(daily_temps,columns=["date","tobs"])
    temp_df.set_index(temp_df['date'],inplace=True)
    temp_df=temp_df.drop(['date'],axis=1)
    temp_dict=temp_df.to_dict()['tobs']
    session.close()
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>")
def tempfrom(start):
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Base=automap_base()
    Base.prepare(engine,reflect=True)
    Station=Base.classes.station
    Measurement=Base.classes.measurement
    session=Session(bind=engine)
    max_stn='USC00519281'
    sd_yr=int(start[0:4])
    sd_mo=int(start[5:7])
    sd_dy=int(start[8:10])
    start_date=dt.date(sd_yr,sd_mo,sd_dy)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    tempfrom_query=session.query(*sel).\
        filter(Measurement.station==max_stn).\
        filter(Measurement.date>start_date).all()
    tempfrom_dict={'min_temp':tempfrom_query[0][0],'avg_temp':round(tempfrom_query[0][1],1),'max_temp':tempfrom_query[0][2]}
    session.close()
    return jsonify(tempfrom_dict)

@app.route("/api/v1.0/<start>/<end>")
def tempbetween(start,end):
    sd_yr=int(start[0:4])
    sd_mo=int(start[5:7])
    sd_dy=int(start[8:10])
    start_date=dt.date(sd_yr,sd_mo,sd_dy)
    ed_yr=int(end[0:4])
    ed_mo=int(end[5:7])
    ed_dy=int(end[8:10])
    end_date=dt.date(ed_yr,ed_mo,ed_dy)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    tempin_query=session.query(*sel).\
        filter(Measurement.station==max_stn).\
        filter(Measurement.date>start_date).\
        filter(Measurement.date<end_date).all()
    tempin_dict={'min_temp':tempin_query[0][0],'avg_temp':round(tempin_query[0][1],1),'max_temp':tempin_query[0][2]}
    session.close()
    return jsonify(tempin_dict)

if __name__=="__main__":
    app.run(debug=True)
