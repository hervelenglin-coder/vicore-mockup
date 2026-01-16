$(window).on('load', function ()  {
  'use strict'

  /* display the right system info in the modal, when displayed */
const systemStatusModal = document.getElementById('systemStatusModal')
if (systemStatusModal) {
    
  systemStatusModal.addEventListener('show.bs.modal', event => {
    // Button that triggered the modal
    const button = event.relatedTarget
    // Extract info from data-bs-* attributes
    const system = button.getAttribute('data-system')
    const modalTitle = systemStatusModal.querySelector('.modal-title')
    modalTitle.textContent = `System Status Details for system ${system}`

    
      
    $.get( `/heartbeat/${system}`,function(data) {       
        
        const hbTime = new Date(data.time);
        document.getElementById("tdHeartTime").innerText = hbTime.toLocaleDateString() + " "+ hbTime.toLocaleTimeString();
        $('#txtNoHeartBeat').collapse("hide");
        $('#tblHeartBeatData').collapse("show");
        //Do the cameras
        const camTableBody =  $('#tblCam tbody');
        camTableBody.empty();//remove the previous row otherwise it grow indefinitely
        for(let i=0; i < data.cameras.length; i++)
          {
            let row = document.createElement("tr");
            let camIDElment = document.createElement("td");
            camIDElment.innerText = data.cameras[i];
            let camTempElement = document.createElement("td");
            camTempElement.innerText = data.temperatures[i];
            row.appendChild(camIDElment);
            row.appendChild(camTempElement);
            camTableBody.append(row);//This is jquerry, so it's just append
          }
          //Anything else that creeps into the status can go here.
          //I don't see much point in displaying the system number, given we display it else where
    })
    .fail(function( jqXHR, textStatus, errorThrown ) {
      const spanSystem = systemStatusModal.querySelector('#systemIDNoHB') 
      spanSystem.innerText = system;
      $('#txtNoHeartBeat').collapse("show");
      $('#tblHeartBeatData').collapse("hide");
      console.log(jqXHR);
      console.log(textStatus);
      console.log(errorThrown );
  });


  })
}
}
)