"""Tests for the database interface. Requires db to be up and have a train pass in it"""
from sqlalchemy import select
from eurotunnel_web.db_iface import get_car_info_with_wheels,get_n_train_passes, get_n_train_passes_before_by_system
from datetime import datetime
from eurotunnel_datamodel.DataModel import TrainPass
from eurotunnel_datamodel.DatabaseHelpers import get_session
#import json

##the test data is a mess, get the id of the first pass
stmt = select(TrainPass.train_pass_id).limit(1)
with get_session() as sess:
    first_pass_id = sess.execute(stmt).scalar_one()

def test_car_info():
    res = get_car_info_with_wheels(first_pass_id,1)
    assert res, "We must get a result"
    #print (json.dumps(res,indent = 4))
    #It's slightly hard to know what the first train pass will be, but some things are fairly sure:
    assert res["springs"], "Result must specify wheels"
    assert res["springs"][0]["ax"] , "Wheel must specify axle"
    assert res["springs"][0]["conf_code"], "Wheel must specify confidence code"
    assert res["springs"][0]["conf"] is not None, "Wheel must specify Confidence"
    assert res["springs"][0]["img"] , "Wheel must specify image path"
    assert res["springs"][0]["pos"] , "Wheel must specify Possition"
    assert res["springs"][0]["spring_id"] , "Wheel must specify spring id"
    assert res["car_num"] , "Result must have a car number"
    assert res["nbg"] >=1 ,"There must be at least one bogie"
    assert res["nax"] >=1 ,"There must be at least one axle"
    assert res["springs_checked"] is not None, "Must specify if we should check the springs on this car"
    assert res["bogie_svg"] , "Must specify which svg to draw"
    

def test_get_n_train_passes():
    n_to_fetch = 50
    res = get_n_train_passes(n_to_fetch)
    assert res, "We must get a result"
    assert len(res) < n_to_fetch, f"We must fetch {n_to_fetch} no more than rows"
    assert res[0], "We must fetch at least one item"
    assert "time_checked" in res[0], "We should be fetching time_checked, though it may well be null"
    assert "min_confidence" in res[0], "We must have a minimum confidence"
    assert any([tp for tp in res if tp['train_pass_id'] == first_pass_id]), "We must be returning the first pass somewhere, though it needn't be first"

def test_get_n_train_passes_before_by_system():
    n_to_fetch = 50
    install = 1
    res = get_n_train_passes_before_by_system(n_to_fetch,datetime(2030,1,1),install)
    assert res, "We must get a result"
    assert len(res) < n_to_fetch, f"We must fetch {n_to_fetch} no more than rows"
    assert res[0], "We must fetch at least one item"
    assert "time_checked" in res[0], "We should be fetching time_checked, though it may well be null"
    assert "min_confidence" in res[0], "We must have a minimum confidence"
    assert res[0]['installation_id'] == install, f"Must only fetch for specified install"
    
    
