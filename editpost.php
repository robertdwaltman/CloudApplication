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
<title>Edit Your NotTweet</title>
<style>
body{
	background-color: linen;
	font-family: Arial, Helvetica, sans-serif;
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

form {width: 90%;}
label {float: left; width: 150px;}
input[type=text] {float: left; width: 100%; margin-bottom: 5px;}
textarea{float: left; width: 100%; margin-bottom: 5px;}
.clear{clear: both; height: 0; line-height: 0;}
</style>
<script>

function tryAddNew(newContents){
	//this function edits an existing post
	document.getElementById("newPostResponse").innerHTML="";
	if(newContents == ""){
		document.getElementById("newPostResponse").innerHTML+= "Error: You must enter text to post.<br>";
	} else {
		xmlhttp = new XMLHttpRequest();
		xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            	//redirect to main display page
                window.location.href = "http://web.engr.oregonstate.edu/~waltmanr/projectdisplay.php";
            }
        }
        var statement = "username="+username+"&password="+password+"&action=editposting&posting=" + newContents + "&postid=" + postid;
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
}
?>
	<script>
		//this passes the php session variables into the javascript code
		var postid = <?php echo json_encode($_POST['postid']); ?>;
		var username = <?php echo json_encode($_SESSION['username']); ?>;
		var password = <?php echo json_encode($_SESSION['password']); ?>;
	</script>
	<div id="newPost">
		<form >
				<textarea rows="4" name="newContents" id="newContents" placeholder="Enter your post here..."></textarea>
				<br>
				<br class="clear"/>
				<div id="submitbutton"><button type="button" name="submitbutton" onclick="tryAddNew(newContents.value)">Submit</button></div>
		</form>
	</div>
	<div id="newPostResponse">
	</div>



</body>
<script>
//this segment retrieves the contents of the post to be edited
//which allows the app to auto-fill the text input box with the existing
//post contents
xmlhttp = new XMLHttpRequest();
xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
    	var JSONobject = JSON.parse(xmlhttp.responseText);
    	document.getElementById("newContents").value = JSONobject.contents;
    }
}
var statement = "http://twittercopy-1104.appspot.com?postid=" + postid +"&display=posting";
xmlhttp.open("GET", statement, true);
xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xmlhttp.send();
</script>
</html>