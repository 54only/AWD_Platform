function timeAdd0(str) {
    if(str<10){
        str='0'+str;
    }
    return str
}
function CountDown() {
    if (maxtime >= 0) {
        hours = Math.floor(maxtime / (60*60));
        minutes = Math.floor((maxtime % (60*60)) /60);
        seconds = Math.floor(maxtime % 60);
        msg = timeAdd0(hours) + ":" + timeAdd0(minutes) + ":" + timeAdd0(seconds);
        $("#timecount").html(msg);
        --maxtime;
    } else{
        msg = '00:00:00';
        $("#timecount").html(msg);
        clearInterval(timer);
    }
}
function get_math() {
    $.getJSON('/timedelta',
        function (result) {         
            document.title = result['name'];
            $("#banner").text(result['name']);
            timeleft = result['timeleft'];
            maxtime = result['timecount'];
            timer = setInterval("CountDown()", 1000);   
        }
        );   
}
get_math();  



function fresh(){
    //排行榜
    $.getJSON('/teams',
        function (result) {
            $("#score").html("");
            for (x in result['teams']){
                var name = result['teams'][x]['name'];
                //var token = result[x]['token'];
                var score = result['teams'][x]['scoresum'];
                var rank = result['teams'][x]['rank'];
                
                var tr ;
                if(rank<4)
                    tr = '<tr><td><span class="icon_gold">'+ rank +'</span></td><td><span class="icon_tag color_yellow">'+name+'</span></td><td class="color_blue">'+score+'</td></tr>';
                else
                    tr = '<tr><td><span class="">'+ rank +'<td><span class="icon_tag">'+name+'</span></td><td>'+score+'</td></tr>';
            $("#score").append(tr);
            }
        }
    );
    //实时战况
    $.getJSON('/rounds',
        function (result) {
            $("#showrounds").html("");
            for (x in result){
                var _id = result[x]['id'];
                var msg = result[x]['msg'];
                var score = result[x]['score'];
                var rounds = result[x]['rounds'];
                var time = result[x]['time'];
                var date = time.split(' ')[0];
                var thetime = time.split(' ')[1];
                var attackteamname = result[x]['attackteamname'];
                var defanseteamname = result[x]['defanseteamname'];
                var typename = result[x]['typename'];

                $("#showrounds").append('<li><div class="contxt "><span class="data">'+date+'</span>'+
                      '<span class="time">'+thetime+'</span>'+
                      '<span class="team1 color_yellow">'+attackteamname+'</span>'+
                      '<span class="handle color_red">成功攻陷</span>'+
                      '<span class="team2 color_blue">'+defanseteamname+'</span>'+
                      '<span class="state">'+typename+'</span>'+
                    '<span class="fr color_blue">'+score+'分</span></div></li>'
                    );
            }
        }
    );
}


fresh();
setInterval('fresh()', 5*1000); 















