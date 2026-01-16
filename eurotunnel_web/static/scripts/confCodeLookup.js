{
    function confCodeLookup(car){
          'use strict'
        if ((!car['springs_checked']))
            return 'ci-col-0';//code 0 is already used for unchecked
        const current_car_conf = car['conf_code'];
        if(current_car_conf == 5)
        {
            console.warn("springs checked but conf code uknown");
            return 'ci-col-0';
        }
        if(current_car_conf == 0)
            return 'ci-col-human-confirmed'; //special case for human confirmed okay
        if ((current_car_conf > 0) && 
                (current_car_conf < 4)) {
            return 'ci-col-' + current_car_conf;
        } 
        console.warn("Unexpected car confidence value, not displaying",current_car_conf);
        return '';
    }
}