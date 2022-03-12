function disableBtn(id) {
    var btn = document.getElementById(id);
    btn.classList.remove("pure-button-primary");
    btn.disabled = true;
}

function showBtn(id) {
    var btn = document.getElementById(id);
    btn.disabled = false;
    btn.classList.add("pure-button-primary");
    btn.style.removeProperty("display");
}

function hideBtn(id) {
    document.getElementById(id).style.display = 'none';
}


function showHours() {
    // showBtn("pump-btn-1");
    showBtn("pump-btn-2hr");
    // showBtn("pump-btn-3");
    showBtn("pump-btn-4hr");
    // showBtn("pump-btn-5");
    showBtn("pump-btn-6hr");

    hideBtn("cancel-btn");
}

function showStop() {
    // hideBtn("pump-btn-1");
    hideBtn("pump-btn-2hr");
    // hideBtn("pump-btn-3");
    hideBtn("pump-btn-4hr");
    // hideBtn("pump-btn-5");
    hideBtn("pump-btn-6hr");

    showBtn("cancel-btn");
}

function handleButton(event) {
    event.preventDefault();
    console.log("button pressed");
    console.log(this.id);

    disableBtn(this.id);

    var url = "/pump-on";
    if (this.id === "cancel-btn") {
        url = "/pump-off";
    }

    data = {"button": this.id};

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      }).then(res => {
        console.log("Request complete! response:", res);

        // Update the status
        var pump_status = document.getElementById("pump-status");
        pump_status.innerHTML = "Pump is ON";

        // Update the buttons
        if (url === "/pump-on") {
            showStop();
        } else {
            showHours();
        }

      }).catch((error) => {
         console.log("Request error:", error);
        // FIXME: add message on screen
      });
}


function updatePumpStatus() {
    // console.log("update status");
    fetch("/pump-status")
    .then(res => res.json())
    .then((status) => {
        // console.log('Pump Status:', status);
        // Insert the status into the html
        var pump_status = document.getElementById("pump-status");
        pump_status.innerHTML = "Pump is " + status["running"];

        var pump_runtime = document.getElementById("pump-runtime");
        pump_runtime.innerHTML = status["remaining"];

        if(status["running"] === "ON") {
            showStop();
        } else {
            showHours();
        }

    }).catch(err => { throw err });
    setTimeout(updatePumpStatus, 5000);
}

function onReady() {
    hideBtn("cancel-btn");

    // Handle hours selection
    // document.getElementById("pump-btn-1hr").addEventListener("click", handleButton);
    document.getElementById("pump-btn-2hr").addEventListener("click", handleButton);
    // document.getElementById("pump-btn-3hr").addEventListener("click", handleButton);
    document.getElementById("pump-btn-4hr").addEventListener("click", handleButton);
    // document.getElementById("pump-btn-5hr").addEventListener("click", handleButton);
    document.getElementById("pump-btn-6hr").addEventListener("click", handleButton);
    document.getElementById("cancel-btn").addEventListener("click", handleButton);

    updatePumpStatus();
}

onReady();