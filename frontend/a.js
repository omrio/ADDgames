var counter = 0;

var screenWidth = 320;
var screenHeight = 480;
var screenRatio = screenWidth / screenHeight;

var tilt;

window.ondevicemotion = function(e) {
  tilt = event.accelerationIncludingGravity.y
}

function charsFromVar(v,num_iter) {
  var a = []

  for (var i = 0; i < num_iter; i++) {
    a.unshift(v & 65535);
    v = v >> 16;
  }

  return a;
}

document.ontouchstart = function(e) {
  var text = ""

  $.each(e.changedTouches,function(i,v) {
    var widthpx = Math.round(v.screenX / screenWidth * 255 * screenRatio);
    var heightpx = Math.round(v.screenY / screenHeight * 255);

    var tstamp = charsFromVar(new Date().getTime(),4);
    var fTilt = charsFromVar(tilt.toFixed(3)*1000 + 10000,1);

    var msg = String.fromCharCode(widthpx,heightpx);

    $.each(tstamp,function(j,w) {
      msg += String.fromCharCode(w)
    });

    $.each(fTilt,function(j,w) {
      msg += String.fromCharCode(w)
    });
    
    ADDC.addMsg(1,7,msg);

    text += widthpx + " " + heightpx + "<br />"
  })

  text += "touchdown!<br /><a href='#' onclick='location.reload()'>reload</a><br />";

  $('body').html(text);
}

document.ontouchend = function(e) {
  var text = ""

  $.each(e.changedTouches,function(i,v) {
    var widthpx = Math.round(v.screenX / screenWidth * 255 * screenRatio);
    var heightpx = Math.round(v.screenY / screenHeight * 255);

    var tstamp = charsFromVar(new Date().getTime(),4);
    var fTilt = charsFromVar(tilt.toFixed(3)*1000 + 10000,1);

    var msg = String.fromCharCode(widthpx,heightpx);

    $.each(tstamp,function(j,w) {
      msg += String.fromCharCode(w)
    });

    $.each(fTilt,function(j,w) {
      msg += String.fromCharCode(w)
    });
    
    ADDC.addMsg(2,7,msg);

    text += widthpx + " " + heightpx + "<br />"
  })

  text += "DONE!<br />" + tilt + "<br><a href='#' onclick='location.reload()'>reload</a><br />" + ADDC.connection.readyState;

  $('body').html(text);
}

document.ontouchmove = function(e) {
  e.preventDefault();

  var text = ""

  $.each(e.changedTouches,function(i,v) {
    var widthpx = Math.round(v.screenX / screenWidth * 255 * screenRatio);
    var heightpx = Math.round(v.screenY / screenHeight * 255);

    if (fake.readyState === 1) {
      ADDC.addMsg(2,2,String.fromCharCode(widthpx,heightpx));
      text += ADDC.chunk.length + "<br>";
    }

    text += gameid + "<br />"
    text += widthpx + " " + heightpx + "<br />"
    text += "<a href='#' onclick='location.reload()'>reload</a>"
  })
  counter++;
  $('body').css('background-color','#eed').html(fake.readyState + " " + text);
}

ADDController = function(display_ws,controller_id) {
  var obj = {
    connection : null,
    chunk : [],
    stringMsgType : [5],

    addMsg : function(type,length,data) {
      var msg = String.fromCharCode(type,length);

      msg += data
      obj.chunk.push(msg)
    },
    sendChunk : function() {
      if (obj.connection && obj.connection.readyState == 1 && obj.chunk.length > 0) {
        obj.connection.send(obj.chunk.join(''));
      }
      obj.chunk = [];
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
var cid = parseInt((Math.random() * 10000) + 1000);
gameid = 60
var ADDC = ADDController('ws://10.0.0.118:8887/' + gameid + '/controller/' + cid,cid);
// var ADDC = ADDController('ws://10.0.0.118:8888/' + gameid + '/controller/' + controller_id, controller_id);
