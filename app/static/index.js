var interval;
var wikiDict={};
var loginOption = document.getElementById("login");
var createOption = document.getElementById("create");
loginOption.addEventListener("click", function(){optionClick(loginOption)}, false);
createOption.addEventListener("click", function(){optionClick(createOption)}, false);
document.addEventListener("click", optionForm, false);
document.getElementById("submit").addEventListener("click", inputCheck, false);
document.getElementById("subreddit").addEventListener("keypress", hideWarning, false);
setup_data();


function httpObject(){
var xmlhttp;
if (window.XMLHttpRequest)
  {// code for IE7+, Firefox, Chrome, Opera, Safari
  xmlhttp=new XMLHttpRequest();
  }
else
  {// code for IE6, IE5
  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }

return xmlhttp;
}


//requests a list of recent, favorites and random subreddits from the server and attaches eventlisteners to each button
function setup_data(){
var recent, favorites, random;

var xmlhttp = httpObject();
xmlhttp.open("GET","http://127.0.0.1:8000/setup_data", true);
xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
xmlhttp.send();

xmlhttp.onreadystatechange=function(){
  if (xmlhttp.readyState==4 && xmlhttp.status==200)
    {
        var setup_data = JSON.parse(xmlhttp.responseText);
        recent = setup_data.recent;
        favorites = setup_data.favorites;
        random = setup_data.random;
        var recentSelector =  subSelector(0);
        var favSelector =  subSelector(0);
        var randomSelector =  subSelector(0);
        document.getElementById("recent-button").addEventListener("click", function(){recentSelector("recent", recent)});
        document.getElementById("favorites-button").addEventListener("click", function(){favSelector("favorites", favorites)});
        document.getElementById("random-button").addEventListener("click", function(){randomSelector("random", random)});

    }
}
}

//cycles through the list subObj each time a button is clicked.
function subSelector(index){
return function innerSelector(buttonType, subObj){
if(subObj.length ===0){
    return;
}
else{
    if(buttonType==="recent"){
        if(index == 10 || (subObj.length -1) < index)
            index=0;
        runAJAX(subObj[index])
        index++;
    }
    else if(buttonType==="favorites"){
        if(index ==7)
             index=0;
        runAJAX(subObj[index])
        index++;
    }
    else{
        var max = subObj.length - 1;
        var randomNumber = Math.floor(Math.random() * max)

        runAJAX(subObj[randomNumber]);
    }
}
}
}

//displays or hides the login or create form when clicked on
function optionClick(e){

if(e.children[0].style.visibility==="hidden"){
    e.children[0].style.visibility="visible";
}
else{
    e.children[0].style.visibility="hidden";
}
}

//hides the visible login or create form when clicked anywhere outside of it
function optionForm(){
if(document.getElementById("login-form").style.visibility==="visible" && document.getElementById("login-container").querySelector(":hover")===null) {
    document.getElementById("login-form").style.visibility="hidden";
}
else if(document.getElementById("create-form").style.visibility==="visible" && document.getElementById("create-container").querySelector(":hover")===null){
    document.getElementById("create-form").style.visibility="hidden";
}
}

//creates the elements needed to display every related subreddits as well as the eventlisteners needed to display their information
function createGraph(subredditList, i){
var par = document.createElement("P");
par.className = "Ograph";
var t = document.createTextNode(subredditList[i] + " " + subredditList[i+1]);
par.appendChild(t);
document.getElementById("part4b").appendChild(par);
wikiDict[subredditList[i]] = getInformation(subredditList[i]);
par.addEventListener("mouseover", function( event ) {
    document.getElementById("part5b").innerHTML = wikiDict[subredditList[i]];
});
}

//fetches possible meaning, definitions or summary of every related subreddits via Google/Wiki API
function getInformation(subreddit){
$.getJSON("https://ajax.googleapis.com/ajax/services/search/web?v=1.0&hl=en&gl=en&userip=&q=" + subreddit + " en.wikipedia&start=0&rsz=1&callback=?", subreddit, function (data) {
    if(data!==undefined){
        if(data.responseData.results.length !== 0){
            $.getJSON("https://en.wikipedia.org/w/api.php?&format=json&action=query&generator=search&gsrsearch=" + data.responseData.results["0"].url.slice(30) + "&utf8&gsrlimit=1&gsrwhat=nearmatch&prop=extracts&exintro&redirects&exchars=1059&callback=?", subreddit, function(data){
                setInformation(subreddit,data);
            });
        }
        else
             wikiDict[subreddit]="No preview available";
    }
    else{
        $.getJSON("https://en.wikipedia.org/w/api.php?&format=json&action=query&generator=search&gsrsearch=" + subreddit + "&utf8&gsrlimit=1&gsrwhat=nearmatch&prop=extracts&exintro&redirects&exchars=1059&callback=?", subreddit, function(data){
                if(data.hasOwnProperty("query")===false){
                    $.getJSON("https://en.wikipedia.org/w/api.php?&format=json&action=query&generator=search&gsrsearch=" + subreddit + "&utf8&gsrlimit=1&gsrwhat=text&prop=extracts&exintro&exchars=1059&callback=?",subreddit, function(data){
                        if(data.hasOwnProperty("query")===false){
                            $.getJSON("https://en.wikipedia.org/w/api.php?&format=json&action=query&list=search&srsearch=" + subreddit + "&exchars=1059&callback=?",subreddit, function(data){
                                $.getJSON("https://en.wikipedia.org/w/api.php?&format=json&action=query&generator=search&gsrsearch=" + data.query.searchinfo.suggestion + "&utf8&gsrlimit=1&gsrwhat=text&prop=extracts&exintro&exchars=1059&callback=?",subreddit, function(data){
                                    setInformation(subreddit, data);
                                });
                            });
                        }
                        else{
                            setInformation(subreddit, data);
                        }
                    });
                }
                else{
                    setInformation(subreddit, data);
                }

        });
    }
});
}

//Stores the possible meaning, definitions or summary found for each related subreddit in an Object
function setInformation(subreddit, data){
var topWiki;
    try{
        var keys = Object.keys(data.query.pages);
        if(data.query.pages[keys[0]].title === undefined || data === undefined || data.query.pages[keys[0]].title==="Reddit" || data.query.pages[keys[0]].title==="undefined")
            wikiDict[subreddit]="No preview available";
        else
            wikiDict[subreddit]=data.query.pages[keys[0]].extract;
    }catch(err){
        wikiDict[subreddit]="No preview available";
    }
}


function scrollToGraph(){
$("html, body").animate({
    scrollTop: $("#two").offset().top
}, 1000);
}

//Checks user input to make sure it contains valid characters and whether the subreddit is banned or set to private
function inputCheck(){
var searchtype = "Fast";
var subreddit = document.getElementById("subreddit").value;
var flag=true;

var xmlhttp=httpObject();

for(var i=0; i <= subreddit.length; i++){
    if((subreddit.charCodeAt(i) >= 65 && subreddit.charCodeAt(i) <= 90) || (subreddit.charCodeAt(i) >= 97 && subreddit.charCodeAt(i) <= 122)){
        flag=false;
        break;
    }
}

if(flag){
    var warning = document.getElementById("warning-container");
    warning.style.visibility = "visible";
    return;
}
else{
    xmlhttp.open("GET", "https://www.reddit.com/subreddits/search.json?q=" + subreddit +"&limit=1", true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send();

    xmlhttp.onreadystatechange = function(){

        if(xmlhttp.readyState == 4 && xmlhttp.status == 200){
            var validSub = JSON.parse(xmlhttp.responseText);
            try{
                if(validSub.data.children["0"].kind ==="t5" && validSub.data.children["0"].data.public_traffic === true){
                    var subreddit = document.getElementById("subreddit").value;
                    runAJAX(subreddit);
                }
            }
            catch(err){
                var warning = document.getElementById("warning-container");
                warning.style.visibility = "visible";
                return;
            }
            if(!validSub.data.children["0"].data.public_traffic){
                var warning = document.getElementById("warning-container");
                warning.style.visibility = "visible";
                return;
            }
        }
    }

}
}
//Removes the invalid user input warning once the user enters a key inside the input box
function hideWarning(evt){
var warning = document.getElementById("warning-container");
warning.style.visibility="hidden";
}


/*Sends an initial POST request with the users input for the server to process and then follows up with GET requests
to receive a progress report and the POST request results.
*/
function runAJAX(subreddit){
var searchtype = "Fast";
var xmlhttp=httpObject();

xmlhttp.open("POST","http://127.0.0.1:8000/data/",true);
xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
xmlhttp.send("searchtype=" + searchtype + "&subreddit=" + subreddit);

var pbar = document.getElementById("pbar");
pbar.style.visibility = "visible";

interval = setInterval(function () {
var xmlhttp=httpObject();

xmlhttp.open("GET","http://127.0.0.1:8000/data/?searchtype=" + searchtype + "&subreddit=" + subreddit,true);
xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
xmlhttp.send();

xmlhttp.onreadystatechange=function(){
  if (xmlhttp.readyState==4 && xmlhttp.status==200)
    {
    document.getElementById("part4a").innerHTML="Related Subreddits of " + subreddit;
    var svalue = xmlhttp.responseText;
    var evalue = svalue.indexOf(".");
    if(isNaN(svalue)){

        var parent = document.getElementById("part4b");
        var childrens = document.getElementsByClassName("Ograph");
        if(childrens.length > 0){
            var clength = childrens.length;
            for(var c=0; c<clength;c++){
                    parent.removeChild(childrens[0]);
            }
        }
        var jList = JSON.parse(svalue)['subreddits'];
        if(jList.length < 26)
            var jLength = jList.length;
        else
            var jLength = 26;
        for(var i=0; i<jLength; i+=2){
            createGraph(jList, i);
        }
        scrollToGraph();
        clearInterval(interval);
        pbar.style.visibility = "hidden";
        var pdone = document.getElementById("pdone");

    }
    else{
        var pvalue = svalue.substring(0,evalue);
        var pdone = document.getElementById("pdone");
        pdone.innerHTML=pvalue + "%";
        pdone.style.width=pvalue + "%";
    }
    }
}
}, 2000)    ;
}