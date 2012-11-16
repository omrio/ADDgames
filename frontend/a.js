var counter = 0;

var screenWidth = 320;
var screenHeight = 480;
var screenRatio = screenWidth / screenHeight;

document.ontouchmove = function(e) {
  e.preventDefault();

  var text = ""

  $.each(e.changedTouches,function(i,v) {
    var widthpx = Math.round(v.screenX / screenWidth * 255 * screenRatio);
    var heightpx = Math.round(v.screenY / screenHeight * 255);

    if (fake.readyState === 1) {
      fake.send(widthpx + " " + heightpx);
    }

    text += widthpx + " " + heightpx + "<br />"
    text += "<a href='#' onclick='location.reload()'>reload</a>"
  })
  counter++;
  $('body').css('background-color','#eed').html(fake.readyState + " " + text);
}

ADDController = function(display_ws,controller_id) {
  var obj = {
    connection : null,
    chunk : [obj.controller_num,' '],
    stringMsgType : [5],
    controller_num : parseInt((Math.random() * 10000) + 1000),

    addMsg : function(type,length,data) {
      var msg = String.fromCharCode(type,length);

      msg += data
      obj.chunk.push(msg)
    },
    sendChunk : function() {
      if (obj.connection && obj.connection.readyState == 1 && obj.chunk.length > 0) {
        console.log('a')
        console.log(obj.chunk)
        obj.connection.send(obj.chunk.join(''));
      }
      obj.chunk = [obj.controller_num,' '];
    },
    parseChunk : function(c) {
      var parsedChunk = [],
          state = 0, // 0=Get type, 1=Get length, 2=Get contents
          l = 0, // Data bytes counter
          msg, // Object to be pushed to chunk array
          contents = [], // Data string
          isStringMsg;

      $.each(c,function(i,v) {
        var value = v.charCodeAt(0);
        var that = this;

        switch(state) {
          case 0:
            if (contents.length) {
              if (isStringMsg) {
                msg.contents = contents.join('')
              } else {
                msg.contents = contents;
              }
              parsedChunk.push(msg);

              contents = [];
            }

            msg = { type : value };

            state++;
            break;
          case 1:
            l = value;
            isStringMsg = ($.inArray(msg.type,that.stringMsgType))

            state++;
            break;
          case 2:
            isStringMsg ? contents.push(v) : contents.push(v.charCodeAt(0));

            l--;
            if (l === 0) {state = 0;}
            break;
        }
      })

      if (contents.length) {
        msg.contents = contents.join('');
        parsedChunk.push(msg);

        contents = [];
      }

      return parsedChunk;
    }
  }

  obj.connection = new WebSocket(display_ws);
  obj.connection.onopen = function() {
    var msg = controller_id + ' ' + String.fromCharCode(100,0);
    console.log('Sending ' + msg);
    obj.connection.send(msg);
  }
  obj.connection.onmessage = function(e) { console.log(obj.parseChunk(e.data)); };
  setInterval(obj.sendChunk,50);

  return obj;
}
var ADDC = ADDController('ws://ec2-184-72-215-229.compute-1.amazonaws.com:8888/' + gameid + '/controller/' + obj.controller_num, obj.controller_num);
// var ADDC = ADDController('ws://10.0.0.118:8888/' + gameid + '/controller/' + controller_num, controller_num);
