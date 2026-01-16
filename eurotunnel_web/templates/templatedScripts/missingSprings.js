"use strict";


function get_wheel_img_path(relative_part){
    try{
        if(relative_part)
            return '{{ wheel_img_root }}' + '/' + relative_part;
        else
            return '/static/img/no-img.png';
        }
    catch(err)
    {
        console.log(`Error getting path ${err}`);
    } 
}