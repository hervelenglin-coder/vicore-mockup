from eurotunnel_datamodel.DataModel import ConfidenceLevels
from eurotunnel_datamodel.DatabaseHelpers import get_session
from eurotunnel_datamodel.ErrorRecording import ReportError
from sqlalchemy import select

confidence_method = 'min_confidence' #Can be 'min_confidence' or 'av_confidence'

class confidence_interface:
    
    instance = None   
    
    def __init__(self):
        with get_session() as sess:
            stmt = select(ConfidenceLevels).order_by(ConfidenceLevels.confidence_level)
            self.confidence_levels = sess.execute(stmt).scalars().all()

    def confidence_level_car_and_spring(self,confidence: float,confirmed_present : bool | None) -> str:
        """Get confidence level code for Cars/Wheels"""

        if confidence < 0:
            return '1'#This will be getting disregarded later anyway - it'll be unchecked
        if confirmed_present:
            return '0'
        for cl in self.confidence_levels:
            if cl.conf_range.contains(confidence): # type: ignore - despite what pylance thinks, contains is a real function
                return str(cl.confidence_level)
            
        ReportError(2,f'Invlaid Confidence Level {confidence}','confidence_level_car_and_spring')     
        return '0'       

    def confidence_level_train(self,confidence) -> str:
        """Get confidence level code for whole Train"""
        
        if confidence < 0:
            return '5'#This will be getting disregarded later anyway - it'll be unchecked
        for cl in self.confidence_levels:
            if cl.conf_range.contains(confidence): # type: ignore - despite what pylance thinks, contains is a real function
                match cl.level_name_en:
                    case "RED":
                        return '5'
                    case "AMBER":
                        return '3'
                    case "GREEN":
                        return '1'        
        ReportError(2,f'Invlaid Confidence Level {confidence}','confidence_level_train')            
        return '0'

    def add_train_conf_codes(self,items :list[dict]):
        for i in range(len(items)):
            if confidence_method in items[i]:
                if(items[i]['n_checked'] < 1):
                    items[i]['conf_code'] = '0'#special conf code for unchecked.
                else:
                    items[i]['conf_code'] = self.confidence_level_train(items[i][confidence_method])


    @staticmethod
    def GetConfidenceInterface():
        if(confidence_interface.instance == None):
            confidence_interface.instance = confidence_interface()
        return confidence_interface.instance