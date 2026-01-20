const REQUEST_LIMIT = 3;

let fetcherRequests = 0;

let fetchingInterval: number | null = null;

function startFetching() {
  if (fetchingInterval) {
    clearInterval(fetchingInterval);
  }
  fetchingInterval = setInterval(() => {
    if (fetcherRequests < REQUEST_LIMIT) {
      fetch(`http://localhost:8000/all`, {method: "GET"})
        .then((res) => res.json())
        .then((data) => {
          updateInterface(data);
          fetcherRequests--;
        });
      fetcherRequests++;
    }
  }, 16);
}

function stopFetching() {
  if (fetchingInterval) {
    clearInterval(fetchingInterval);
  }
}

function startSimulation() {
  fetch("http://localhost:8000/start", {method: "POST"});
}

function stopSimulation() {
  fetch("http://localhost:8000/stop", {method: "POST"});
}

function resetSimulation() {
  fetch("http://localhost:8000/reset", {method: "POST"});
}
