
var maxtime; 
var timer;
var myname;
var mytoken;

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


        $("#timecount").html('倒计时 <b>'+msg+'</b>');

        //if (maxtime == 5 * 60)alert("距离结束仅剩5分钟");
        --maxtime;
        //console.log(maxtime);
    } else{
        //console.log(maxtime);
        clearInterval(timer);
        alert("时间到，结束!");
    }
}
//timer = setInterval("CountDown()", 1000);   


// 比赛时间、队伍信息 刷新一次

function get_math() {
    $.getJSON('/timedelta',
        function (result) {         
            document.title = result['name'];
            $("#banner").text(result['name']);

            timeleft = result['timeleft'];
            maxtime = result['timecount'];
            //console.log(maxtime);
            timer = setInterval("CountDown()", 1000);   
        }
        );   


    $.getJSON('/team',
        function (result) {
            $("#ssh_info").html("");        

            var token = result['token'];
            var name = result['teamname'];            
            myname=name;
            mytoken = token;

            $("#myform").attr("action","flag?token=" + token );
            $("#mytoken").text("curl -d 'flag=flag' http://xxxx:9000/flag?token=" + token);
            $("#ctoken").text(token);   
            $("#teamname").text(myname);       
            $("#teamname2").text(myname);    

            for (x in result['containers']){                 
                var cname = result['containers'][x]['typename'];
                var score = result['containers'][x]['score'];
                //var ip = result[x]['ip'];
                var ssh_user = result['containers'][x]['sshaccount'];
                var ssh_password = result['containers'][x]['sshpassword'];
                var ssh_port = result['containers'][x]['sshport'];
                var serviceport = result['containers'][x]['serviceport'];
                $("#ssh_info").append('<tr>'+
                '<td>'+cname+'</td>' +
                //'<td>'+token+'</td>' +
                '<td>'+ssh_user+'</td>'+
                '<td>'+ssh_password+'</td>'+
                '<td>'+ssh_port+'</td>'+
                '</tr>');
    
            
            }
        }
    );
}
get_math();                         // 比赛时间、队伍信息 刷新一次
//setInterval('get_math()', 2*1000); // 比赛时间、队伍信息 token 每30秒刷新一次



function show_mycontainers(data){
    /*
    <ul id="mycontainer">
        <li>
            <p class="li-title">unknow</p>
            <p class="li-img state_2"></p>    # state_2 正常 state_3 被攻击 state_4 check state_5 check&被攻击
            <p class="li-state">题目状态正常</p>
            <p class="li-number">10365.5T</p>
            <p class="li-value">当前分值</p>

        </li>
    <ul>
    */
    $("#mycontainer").html("");
    for(x in data)
    {
        var stat=2;
        if(data[x]['attack_stat']==0 && data[x]['check_stat']==1)stat=4;
        if(data[x]['attack_stat']==1 && data[x]['check_stat']==1)stat=5;
        if(data[x]['attack_stat']==1 && data[x]['check_stat']==0)stat=3;

        stattype = 'state_'+stat;
        //console.log(stattype);
        var li ='<li>'+
            '<p class="li-title">'+data[x]['container']+'</p>' +
            '<p class="li-img '+stattype+'"></p> ' +  
            '<p class="li-state">题目状态</p>' +
            '<p class="li-number">'+data[x]['score']+'</p>' +
            '<p class="li-value">当前分值</p>' +
            '</li>';
        $("#mycontainer").append(li);
    }


}




function get_temps() {

    $.getJSON('/team',
        function (result) {
            var data=new Array(); //{'container':'pwnable','stat':1,'score':999},

            for(x in result['containers']){
                data.push({'container':result['containers'][x]['typename'],
                            'attack_stat':result['containers'][x]['attack_stat'],
                            'score':result['containers'][x]['score'],
                            'check_stat':result['containers'][x]['check_stat'],
                        });
            }
            //console.log(data);
            show_mycontainers(data);

        });
            



    $.getJSON('/teams',
        function (result) {
            $("#team").html("");
            //console.log(myname);
            //$('#teams_tr').append("<th>1111</th>");
            var a=new Array();
            var p = 0;

            var o = '<th>名次</th><th>战队</th><th>得分</th>';

            for(j in result['typename'])
            {
                o += "<th>"+result['typename'][j]+"</th>";
                a[p]=result['typename'][j];
                p++;
            }

            $('#teams_tr').html("");
            $('#teams_tr').append(o);
            $('#teams_tr').append('<th>变化</th>');


            for (x in result['teams']){
                var name = result['teams'][x]['name'];
                //var token = result[x]['token'];
                var score = result['teams'][x]['scoresum'];
                var rank = result['teams'][x]['rank'];
                var change = result['teams'][x]['delta'];
                var arrowspan = ['<span class="arrow arrow_up"></span>','<span class="arrow arrow_line"></span>','<span class="arrow arrow_down"></span>'];
                var se=1;
                if (change > 0) se=0;
                if (change < 0) se=2;
                
                tmp=new Array();

                for(x2 in  result['teams'][x]['containers'])
                {
                    for(x3 in a){
                        if(a[x3]== result['teams'][x]['containers'][x2]['typename']){
                            //tmp[x3]=result['teams'][x]['containers'][x2]['score'] +'|' +result['teams'][x]['containers'][x2]['attack_stat']+'|'+result['teams'][x]['containers'][x2]['check_stat'] ;
                            console.log(result['teams'][x]['containers']);
                            var stat=2;
                            if(result['teams'][x]['containers'][x2]['attack_stat']==0 && result['teams'][x]['containers'][x2]['check_stat']==1)stat=4;
                            if(result['teams'][x]['containers'][x2]['attack_stat']==1 && result['teams'][x]['containers'][x2]['check_stat']==1)stat=5;
                            if(result['teams'][x]['containers'][x2]['attack_stat']==1 && result['teams'][x]['containers'][x2]['check_stat']==0)stat=3;

                            stattype = 'state_'+stat;
                            console.log(stattype);

                            tmp[x3]='<span class="tag '+stattype+'"></span>';

                        }
                    }
                }
                trstring = '<tr>';

                if (rank < 4)
                    {trstring += '<td><span class="icon">'+rank+'</span></td>'  ;}
                else
                    {trstring += '<td>'+rank+'</td>'  ;}



                trstring+='<td><img src="/static/images/team.png" alt=""> '+name+'</td>'+
                //'<td>'+token+'</td>'+
                '<td>'+score+'</td>';

                for(i=0;i<tmp.length;i++) trstring+='<td>'+tmp[i]+'</td>';
                //'<td>'+ip+'</td>'+



                trstring+='<td>'+change+arrowspan[se]+'</td>';
                trstring+='</tr>';
                $("#team").append(trstring);

                if(name == myname){
                    $("#cround_rank").html(rank);
                    $("#cscroe").html(score); 
                }
            }
        }
    );



    
    $.getJSON('/rounds2',
        function (result) {
            $("#attacklist").html("");
            for (x in result){
                var typename = result[x]['typename'];
                var teamname = result[x]['teamname'];
                var time = result[x]['time'];

                // <li>用户<span class="user01">Mini</span>攻击了<span class="user02">httpd</span><span class="fr">2019-10-22&nbsp;12:23:25</span></li>
                // attacklist
                $("#attacklist").append('<li>用户 <span class="user01">'+ teamname +
                '</span> 攻击了 <span class="user02">'+ typename +
                '</span><span class="fr"> ' + time +
                '</span></li>');
            }
        }
    );

    $.getJSON('/rounds',
        function (result) {
            $("#rounds").html("");
            for (x in result){
                var _id = result[x]['id'];
                var msg = result[x]['msg'];
                var score = result[x]['score'];
                var rounds = result[x]['rounds'];
                var time = result[x]['time'];
                $("#rounds").append('<tr>'+
                '<td>'+_id+'</td>' +
                '<td>'+msg+'</td>'+
                '<td>'+score+'</td>'+
                '<td>'+rounds+'</td>'+
                '<td>'+time+'</td>'+
                '</tr>');
            }
        }
    );

    $.getJSON('/current_rounds',
        function (result) {
            $("#cround").html(result);           
        }
    );
    
    
    $.getJSON('/info/2',
        function (result) {
            $("#infos").html("");
            for (x in result){
                var infos = result[x]['id'];
                $("#infos").append('<ul>'+
                '<li>'+infos+'</li>' +
                '</ul>');
                //alert(infos)
            }
            
        }
    );
}
get_temps();

setInterval('get_temps()', 5*1000); // 队伍情况每一秒刷新一次
