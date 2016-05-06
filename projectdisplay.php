<?php
session_start();
error_reporting(E_ALL);
ini_set('display_errors', 'On');
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name=viewport content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1">
<title>Your NotTweets</title>
<style>
body{
	background-color: linen;
	font-family: Arial, Helvetica, sans-serif;
}
#userPosts{
	background-color: white;
	border-style: solid;
	width: 450px;
	margin-left: auto;
	margin-right: auto;
	margin-bottom: 10px;
	padding-top: 5px;
	padding-right: 15px;
	padding-bottom: 5px;
	padding-left: 15px;
}
#newPost{
	background-color: white;
	border-style: solid;
	width: 450px;
	margin-left: auto;
	margin-right: auto;
	margin-bottom: 10px;
	padding-top: 5px;
	padding-right: 15px;
	padding-bottom: 5px;
	padding-left: 15px;
}
#newPostResponse{
	color: red;
	margin-right: auto;
	margin-left: auto;
	width: 200px;
}

form {width: 90%;}
label {float: left; width: 150px;}
input[type=text] {float: left; width: 100%; margin-bottom: 5px;}
textarea{float: left; width: 100%; margin-bottom: 5px;}
.clear{clear: both; height: 0; line-height: 0;}
</style>
<script>
//location string variable to be added to request if allowed
var locationString = "";
//get the user's location and populate the locationString variable
if (navigator.geolocation){
        	navigator.geolocation.getCurrentPosition(addString);
        }

function addString(position){
	locationString = "&latitude=" + position.coords.latitude + "&longitude=" + position.coords.longitude;
}
function tryAddNew(newContents){
	//this function creates a new post 
	document.getElementById("newPostResponse").innerHTML="";
	if(newContents == ""){
		document.getElementById("newPostResponse").innerHTML+= "Error: You must enter text to post.<br>";
	} else {
		xmlhttp = new XMLHttpRequest();
		xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                window.location.href = "http://web.engr.oregonstate.edu/~waltmanr/projectdisplay.php";
            }
        }
        var statement = "username="+username+"&password="+password+"&action=addposting&posting=" + newContents + locationString;
        xmlhttp.open("POST", "http://twittercopy-1104.appspot.com", true);
        xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xmlhttp.send(statement);
	}
}
</script>
</head>
<body>

<?php
if(!isset($_SESSION['username'])){
	/*this fires if the user got here without logging in*/
	echo "<p>You are not logged in. Please log in <a href='project.php'>HERE</a></p>";
	exit;
} else{
	echo "<p>";
	echo htmlspecialchars("Hello, $_SESSION[username]!");
	echo "</p>";
	echo "<p><form action='project.php?logout=true' method='get'><input type='submit' value='Logout'/></form></p>";

	?>
	<script>
	//this passes the PHP session variables into the javascript code
	var username = <?php echo json_encode($_SESSION['username']); ?>;
	var password = <?php echo json_encode($_SESSION['password']); ?>;
	</script>
	<?php
}
?>
	<div id="userPosts">

	</div>

	<div id="newPost">
		<form >
				<textarea rows="4" name="newContents" placeholder="Enter your post here..."></textarea>
				<br>
				<br class="clear"/>
				<div id="submitbutton"><button type="button" name="submitbutton" onclick="tryAddNew(newContents.value)">Submit</button></div>
		</form>
	</div>
	<div id="newPostResponse">
	</div>



</body>
<script>
populatePosts();
	function populatePosts(){
		//this function populates the user's list of posts
		document.getElementById("userPosts").innerHTML = "";
		xmlhttp = new XMLHttpRequest();
		xmlhttp.onreadystatechange = function() {
		    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
		        try {
		    		var JSONobject = JSON.parse(xmlhttp.responseText);
		    		if (JSONobject.length == 0){
		    			//detect if user has no existing posts
		    			document.getElementById("userPosts").innerHTML += "You have no posts. Create a new one below!";
		    		}
		    		else{
		    			//otherwise iterate over every post for this user
			    		var i = 0;
			    		for(i; i < JSONobject.length; i++){
			    			if(JSONobject[i].latitude == null){
			    				JSONobject[i].latitude = "N/A";
			    			}
			    			if(JSONobject[i].longitude == null){
			    				JSONobject[i].longitude = "N/A";
			    			}
			    			//very long output string, note that every delete button has the
			    			//post's id number as its value, which allows for easy deletion and editing
			    			document.getElementById("userPosts").innerHTML+= "<table cellpadding='2'><tr><td>Your post:</td><td>" + JSONobject[i].contents + "</td></tr><tr><td>Timestamp:</td><td>" + JSONobject[i].timestamp + "</td><tr><td>Latitude:</td><td>" + JSONobject[i].latitude + "</td></tr><tr><td>Longitude:</td><td>" + JSONobject[i].longitude + "</td></tr><tr><td><form method='post' action='editpost.php'><button type='submit' name='postid' value='" + JSONobject[i].idnumber + "'>Edit</button></form></td><td><button type='button' onclick='removePost(" + JSONobject[i].idnumber +")' name='"+ JSONobject[i].idnumber +"' value='" + JSONobject[i].idnumber + "'>Remove</button></td></tr></table>";
			    		}
			    		
			    	}
		    	}
		    	catch(err){
		        	document.getElementById("userPosts").innerHTML+=xmlhttp.responseText;
		        }
		    }
		}
		var statement = "http://twittercopy-1104.appspot.com?username="+username+"&display=userposts";
		xmlhttp.open("GET", statement, true);
		xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		xmlhttp.send();
	}

function removePost(postID){
	//this function deletes an existing post
	xmlhttp = new XMLHttpRequest();
		xmlhttp.onreadystatechange = function() {
		    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
		        populatePosts();
		    }
		}
		var statement = "username="+username+"&password="+password+"&action=deleteposting&postid="+postID;
        xmlhttp.open("POST", "http://twittercopy-1104.appspot.com", true);
		xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		xmlhttp.send(statement);

}

</script>
</html>