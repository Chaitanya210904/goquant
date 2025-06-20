let startButton = document.getElementById('startButton');
let stopButton = document.getElementById('stopButton');
let transcriptContent = document.getElementById('transcriptContent');

let socket;

startButton.onclick = () => {
  startButton.disabled = true;
  stopButton.disabled = false;
  transcriptContent.innerHTML = '';

  socket = new WebSocket('ws://localhost:8000/ws');

  socket.onmessage = function (event) {
    const message = JSON.parse(event.data);
    transcriptContent.innerHTML += `\nBOT: ${message.bot}\nUSER: ${message.user || ''}`;
  };

  socket.onopen = () => {
    console.log('WebSocket connection established');
    socket.send(JSON.stringify({ action: 'start' }));
  };

  socket.onerror = (error) => console.error('WebSocket Error:', error);
};

stopButton.onclick = () => {
  startButton.disabled = false;
  stopButton.disabled = true;
  socket.send(JSON.stringify({ action: 'stop' }));
  socket.close();
};