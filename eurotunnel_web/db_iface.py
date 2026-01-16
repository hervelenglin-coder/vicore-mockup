from sqlalchemy import select,  text
from sqlalchemy.orm import Session

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Final
from loguru import logger

from eurotunnel_datamodel.DataModel import SpringLocation, TrainPass, CarTypes, TrainPassCars,SpringImageLocation,HumanConfirmations
from eurotunnel_datamodel.DatabaseHelpers import get_session

from eurotunnel_datamodel.ConfigManager import Config_Manager

from eurotunnel_web.confidence_levels import confidence_interface
from eurotunnel_web.display_name_iface import _create_disp_name



#Start of the image path in the database, to be removed - Must end with a /
#THIS DOES NOT AFFECT WHERE IT LOOKS FOR IMAGES ON THE FILESYSTEM !!!
# It exists because the image paths in the database start with /mnt/outgoing, which is not what is mapped elsewhere, so we need to know what part of the path to remove.
wheel_img_path_prefix = '/mnt/outgoing/'

#What method to calculate colours for the Car icons
car_conf_method = 'min' #Options are 'min' for minimum confidence level across all wheels, or 'av' for average confidence level across all wheels

#What method to calculate colours for the Car icons
train_conf_method = 'min' #Options are 'min' for minimum confidence level across all cars, or 'av' for average confidence level across all cars

#What car splitting method to use if the DB column is NULL
fallback_car_split_method = '6c46' #Use '646' for 6-axle locos with 4-axle wagons, or '444' for 4-axles on everything, '6c46' is a variation of 646 where the first car after the loco is a coach

#Whether to exclude locos when calculating whole Train confidence codes
exclude_locos_conf = True

#Whether to exclude passenger coach when calculating whole Train confidence codes
exclude_coaches_conf = True


#figuring out how to make sqlalchemy do this is a ballache at best
#rather than risk it ballsing up the count with the filter I've just lovingly hand crafted it
get_train_passes_sql: Final[str] = 'SELECT * FROM get_train_passes(\'{before}\'::timestamp,{n_passes}::int);'
"""Querry for selecting a number of passes from eithier install
Returns:
    _type_: a format string which you put your own parameters in
"""
get_train_passes_by_install_sql: Final[str] = 'SELECT * FROM get_train_passes(\'{before}\'::timestamp,{n_passes}::int,{install}::int);'



#The timezone the train passes are stored in
installation_timezone = ZoneInfo(Config_Manager.GetCurrentConfig().default_timezone)

get_cars_and_conf: Final[str] = 'SELECT * ' +\
                                        'FROM get_pass_human_confirms_by_car_and_train_pass(:tpid,:car) cthc ' + \
                                        'JOIN car_types ct ON ct.car_type_id = cthc.car_type_id '+ \
                                        'JOIN bogie_type bt ON ct.bogie_type = bt.bogie_type_id ' + \
                                        'ORDER BY cthc.train_pass_order;'

#Loads the config and creates a redis connection

def row_to_dic(row):
    """Convert a database row into a dict object"""
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

def tuple_rows_to_dics(trows):
    res = []
    for row in trows:
        res.append({k: v for k, v in row._mapping.items()})
        if(not row.train_pass_id):
            logger.warning("No train pass ID here!")
    return res

def get_train_pass_info(train_pass_id, db_session = None):
    """
    Retrieve just the basic-level info about a train pass as a dict object.
    If db_session is None, then it will open and close a DB connection automatically.
    If db_session is supplied, then it will use that DB connection, and keep it open.
    """
    close_at_end = False
    try:
        if db_session == None:
            close_at_end = True
            db_session = get_session()
        res = db_session.query(TrainPass).filter(TrainPass.train_pass_id == train_pass_id).first()
        dtp = row_to_dic(res)
        _create_disp_name(dtp)
        return dtp
    finally:
        if close_at_end and db_session:
            db_session.close()

    
def get_n_train_passes(n:int) -> list[dict]:
    """
    Retrieve all of the Train Passes from the DB, as a DB row reader object.
    Results are ordered with the most recent TrainPass first.
    """
    #Rather than maintain this function twice, n passes before now is 
    #effectively n passes: trains can't pass in the future 
    return get_n_train_passes_before(n,datetime.now())
    
def get_n_train_passes_before(n:int, before_time:datetime) -> list[dict]:
    """
    Retrieve all of the Train Passes from the DB, as a DB row reader object.
    Results are ordered with the most recent TrainPass first.
    """
    with get_session() as db_session:
        start_time = before_time.astimezone(installation_timezone)
        logger.info("Loading passes from before: {}",start_time)
        #forcing it to be a string to stop sqlalchemy fucking the timezone up
        #hence also the .format - doing it as a param loses the timezone
        res = db_session.execute(text(get_train_passes_sql.format(before=str(start_time),n_passes=n)))
        return tuple_rows_to_dics(res)
    
    
def get_n_train_passes_before_by_system(n:int, before_time:datetime,installation: int) -> list[dict]:
    """
    Retrieve all of the Train Passes from the DB, as a DB row reader object, for a given install
    Results are ordered with the most recent TrainPass first.    
    """
    with get_session() as db_session:
        start_time = before_time.astimezone(installation_timezone)
        logger.info("Loading passes from before: {} fpr install: {}",start_time,installation)
        #forcing it to be a string to stop sqlalchemy fucking the timezone up
        #hence also the .format - doing it as a param loses the timezone
        res = db_session.execute(text(get_train_passes_by_install_sql.format(before=str(start_time),n_passes=n,install=installation)))
            
        return tuple_rows_to_dics(res)
    
def car_row_to_web_dict(c) -> dict:
    carnum = '0000'
    id_type = ''
    if c.car_num is not None and c.car_num > 0:
        carnum = str(c.car_num)
        if c.rfid_tag_code and c.rfid_tag_code.startswith("ETMR-"):
            id_type = "RFID: " + c.rfid_tag_code
        elif c.rake_id is not None:
            id_type = "Coupon: C." + str(c.rake_id)    
    conf = c.min_confidence
    
    return {
        'car_num': c.train_pass_order,
        'disp_name': carnum,
        'idtype': id_type,
        'min_conf': c.min_confidence,
        'conf_code': confidence_interface.GetConfidenceInterface().confidence_level_car_and_spring(conf,c.all_confirmed),
        'car_icon': c.icon_head, #Default to head icon - caller should deal with converting to tail if needed
        'nbg': c.num_bogies,
        'nax': c.axles_per_bogie,
        'lead': c.leading_end,
        'bogie_svg': c.svgname,
        'springs_checked': c.springs_checked
        
        }

def get_train_pass_cars(train_pass_id:int ,  db_session = None) -> list[dict]:
    """
    Get a list of all the cars making up the train with the specified train_pass_id.
    Returns a list of dict objects representing the info for each car.
    If include_wheels is True, then each car also contains a 'wheels' element which details the status and image path for each wheel on the car.
    Using include_wheels makes the result significantly larger, so only include this if you need it.
    If db_session is None, then it will open and close a DB connection automatically.
    If db_session is supplied, then it will use that DB connection, and keep it open.
    """
  
    try:
        if db_session == None:
            db_session = get_session()
        
        #any value below 0 for car means all cars. It is the default but I didn't want to define the SQL twice
        cars = db_session.execute(text(get_cars_and_conf), {'tpid': train_pass_id, 'car':-1})

       
    finally:
       if db_session:
            db_session.close()

    result = []
    tail_icons = []
    for car in cars:
        cdic = car_row_to_web_dict(car)
        tail_icons.append(car.icon_tail)
        result.append(cdic)
    for i in range(len(result)):
        if tail_icons[i] and result[i]['car_num'] >= len(result) / 2:  #I expect this selection will need adjusting for PAX trains
            result[i]['car_icon'] = tail_icons[i]

    return result

def get_car_info_with_wheels(train_pass_id: int, train_order: int, db_session: Session | None = None):
    close_at_end = False
    try:
        if db_session == None:
            close_at_end = True
            db_session = get_session()
            
        row = db_session.execute(text(get_cars_and_conf), {'tpid': train_pass_id, 'car':train_order}).first()   
        
        if row is None:
            return None
        
        cdic = car_row_to_web_dict(row)
        
        axfirst = row.first_train_axle
        axlast = axfirst + cdic['nbg'] * cdic['nax']

        stmt = select(SpringLocation,HumanConfirmations.present_not_absent) \
                .join(HumanConfirmations, isouter=True) \
                .where(SpringLocation.train_pass_id == train_pass_id, SpringLocation.train_axle_number >= axfirst, SpringLocation.train_axle_number < axlast) \
                .order_by(SpringLocation.train_axle_number,SpringLocation.cam_pos)
        springs = db_session.execute(stmt)
        
        spring_res = []
        for s in springs:
            car_ax = s[0].train_axle_number - axfirst + 1 #Car axle number, one-based
            imgpath = s[0].best_image_path
            if imgpath.startswith(wheel_img_path_prefix):
                imgpath = imgpath[len(wheel_img_path_prefix):]
            spring_res.append({
                'ax': car_ax,
                'conf_code': confidence_interface.GetConfidenceInterface().confidence_level_car_and_spring(s[0].confidence,s[1]),
                'conf': round(s[0].confidence, 2),
                'img': imgpath,
                'pos': s[0].cam_pos,
                'spring_id':s[0].spring_location_id,
                'human_confirm':s[1], # it's a bool, where None means no human confirmation
                'has_human_confirm':bool(s[1] != None) #In theory this is redundant; you can just test for null, but make it explict
            })
        cdic['springs'] = spring_res
        
    finally:
        if close_at_end and db_session:
            db_session.close()

    return cdic 

def get_train_pass_conf_codes(train_passes):
    result = []
    with get_session() as db_session:
        for tp in train_passes:
            info = get_train_pass_info(tp.train_pass_id, db_session)
            (cars, train_conf) = get_train_pass_cars(tp.train_pass_id,  db_session)
            info['conf'] = train_conf
            info['conf_code'] = confidence_interface.GetConfidenceInterface().confidence_level_train(train_conf)
            result.append(info)
    return result

def get_train_pass_info_with_cars(train_pass_id):
    info = get_train_pass_info(train_pass_id)
    cars = get_train_pass_cars(train_pass_id)
    info['cars'] = cars
    return info

def get_all_image_paths_for_spring(spring_location: int)->list[str]:
    """Gets all the images for a given spring.
    Only relevant if spring not detected

    Args:
        spring_location (int): the id of the spring location you want the images for
        
    """
    stmt = select(SpringImageLocation).where(SpringImageLocation.spring_location_id == spring_location) 
    with get_session() as db_session:    
        all_results = db_session.execute(stmt).all()
        spring_locs = [s[0].image_path for s in all_results]
        return spring_locs
        