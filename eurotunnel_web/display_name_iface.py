from typing import Final
from sqlalchemy import text

from eurotunnel_web.models.display_names_model import Displaynames
from eurotunnel_web.redis_web import RedisInterfaceWeb

from eurotunnel_datamodel.DatabaseHelpers import get_session



#Getting train service codes is some way off in the future, this is what to display instead
service_code_place_holder: Final[str] = ''#upon reflection I think having (tbc) looks ugly

#There's another instance of this loaded elsewhere, but it's not resource hungry
redis_interface = RedisInterfaceWeb() 

#The function that gets the first tag for a train pass
get_trainpass_firsttag: Final[str] = 'SELECT * FROM get_first_tag(:tp)'

MAX_DISPLAY_NAME_LEN:Final[int]= 30

def generate_train_disp_names(items: list[dict]):
    """_summary_
    Generates display names for a list of train passes, modifying the dicts in place.
    
    Args:
        items (list[dict]): A list of trainpasses, each one must have a train_pass_id key. 
        
    """
    for i in range(len(items)):
       _create_disp_name(items[i])
       
def _create_disp_name(row: dict):
      tpid = row['train_pass_id']
      #try to get it from the cache
      displaynames = redis_interface.get_trainpass_displayname(tpid)
      if displaynames == None:
          #cache miss
         displaynames  = create_display_name_worker(row, tpid)
         redis_interface.set_trainpass_displayname(tpid,displaynames)
      if displaynames == None:
          raise ValueError(" we must generate a display name")
      
      row['disp_name'] = displaynames.long_name
      row['disp_name_short'] = displaynames.short_name

def create_display_name_worker(row:dict, tpid:int) -> Displaynames:
    """This creates the string that is used everywhere to display
    the name of the train pass

    Args:
        row (dict): a train of data, can come from several queries, includes train pass id
        tpid (int): the train pass id, broken out of the row

    Returns:
        _type_: a string ready to display
    """
    ID_STARTS_AT = 5  #The start of the number in the RFID tag
    DELIMITER = "-" #The character that marks the end of the number
    
    def  get_num_only(entire_tag: str) -> str:
        if DELIMITER in entire_tag:
            #I'm not sure if it's possible to have more than 4 digits, better to be safe
            idx_num_end = entire_tag.rindex(DELIMITER)
            return entire_tag[ID_STARTS_AT:idx_num_end]
        #It's not a real tag
        return entire_tag

    tsc = row['train_service_code'] 
    if tsc:
          tsc += " : "
    else:
          tsc = service_code_place_holder
    rfid_part = ''
    if not 'first_tag' in row:        
      with get_session() as db_session:        
          res = db_session.execute(
                        text(get_trainpass_firsttag), { "tp":tpid }
                )           
          first_tag= res.scalar()
          if first_tag:             
            rfid_part = get_num_only(first_tag)
          else:
            rfid_part = ''
    else:      
      rfid_part = get_num_only(row['first_tag'])
      
    long_name: str = tsc + row['time_start'].strftime('%Y %m %d - %H:%M:%S')   +' ' + rfid_part
    if len(long_name) > MAX_DISPLAY_NAME_LEN:
        short_name: str = row['time_start'].strftime('%y %m %d - %H:%M') +' ' + rfid_part
    else:
        short_name = long_name
    return Displaynames(long_name,short_name)