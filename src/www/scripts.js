// -------------------------------------------------------------------------
// Utility scripts.
//
// Author: Bernhard Bablok
// License: GPL3
//
// Website: https://github.com/bablokb/cp-pi5-webswitch
//
// -------------------------------------------------------------------------

var old_state = null;

async function get_status() {

  // fetch status
  const response = await fetch("/get_status");
  const status = await response.json();

  // set initial state
  if (old_state === null) {
    pi5_slider = document.getElementById("pi5_slider");
    pi5_slider.classList.remove("pi5_changing");
    if (!status.pi5_state) {
      pi5_slider.classList.add("pi5_off");
    } else {
      pi5_slider.classList.add("pi5_on");
      pi5_switch = document.getElementById("pi5_switch");
      pi5_switch.checked = true;
    }
    old_state = status.pi5_state;
  }

  // return current status
  return status.pi5_state;
}

async function toggle_power() {
  pi5_switch = document.getElementById("pi5_switch");
  pi5_switch.disabled = true;

  slider = document.getElementById("pi5_slider");
  pi5_slider.classList.remove("pi5_off","pi5_on");
  pi5_slider.classList.add("pi5_changing");

  // send boot/shutdown request
  const response = await fetch("/toggle_power");
  const status = await response.json();

  // start timer for new status
  state_timer();
}

async function state_timer() {
  timer_active = true;
  const new_state = await get_status();
  if (new_state === old_state) {
    // no state change, check again in one second
    setTimeout(state_timer,1000);
  } else {
    // state changed, update color of control
    pi5_slider = document.getElementById("pi5_slider");
    pi5_slider.classList.remove("pi5_changing");
    if (new_state) {
      pi5_slider.classList.add("pi5_on");
    } else {
      pi5_slider.classList.add("pi5_off");
    }
    old_state = new_state;
    // re-activate switch
    pi5_switch = document.getElementById("pi5_switch");
    pi5_switch.disabled = false;
  }
}
