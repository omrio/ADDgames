var fake = new WebSocket('ws://ec2-184-72-215-229.compute-1.amazonaws.com:8888/' + gameid + '/display');
// var fake = new WebSocket('ws://10.0.0.118:8888/' + gameid + '/display');

fake.onmessage = function(e) {console.log("display:",ADDC.parseChunk(e.data)[0])}