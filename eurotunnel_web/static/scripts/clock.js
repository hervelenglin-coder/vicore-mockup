    // Get date time string in format YYYY/MM/DD HH:MM:SS, for display at top of screen
    function get_date_time_display()
    {
        const now = new Date();
        const year = now.getFullYear().toString().padStart(4, "0");
        const month = (now.getMonth() + 1).toString().padStart(2, "0");
        const day = now.getDate().toString().padStart(2, "0");
        const timeString = now.toLocaleTimeString();
        return `${year}-${month}-${day} ${timeString}`;
    }

    $(window).on('load', function ()  {
  'use strict'

        function updateTimeDisplay()
        {
            const timeSpan = document.getElementById('spTime');
            timeSpan.innerText = get_date_time_display();
        }

        //update imediately upon loading
        updateTimeDisplay();
        //update the clock once a second
        setInterval(updateTimeDisplay,1000);
    }
);