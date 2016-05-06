<?php
session_start();
error_reporting(E_ALL);
ini_set('display_errors', 'On');
include 'storedInfo.php'; //password file, permissions set to exclude everyone from seeing it
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name=viewport content='width=500'>
<title>Login</title>
<style>
.title{
	margin-left: auto;
	margin-right: auto;
	text-align: center;
	width: 70%;
	font-family: Arial, Helvetica, sans-serif;
}
#loginbox{
	background-color: white;
	border-style: solid;
	width: 450px;
	margin-left:auto;
	margin-right:auto;
	padding-top: 5px;
	padding-right: 15px;
	padding-bottom: 5px;
	padding-left: 15px;
}
#loginResponse{
	color: red;
	margin-right: auto;
	margin-left: auto;
	width: 200px;
}
#registerResponse{
	color: red;
	margin-right: auto;
	margin-left: auto;
	width: 200px;
}
#loginbutton{
	width: 10%;
	margin-right: auto;
	margin-left: auto;
}
form {width: 400px;}
label {float: left; width: 150px;}
input[type=text] {float: left; width: auto; margin-bottom: 5px;}
input[type=password] {float: left; width: auto; margin-bottom: 5px;}
.clear{clear: both; height: 0; line-height: 0;}
/*formatting rules for text input*/
body{
	background-color: linen;
}
</style>
<script>
function tryLogin(userInput, passInput){
	//attemps to log the user in
	document.getElementById("loginResponse").innerHTML="";
	if(userInput == ""){
		document.getElementById("loginResponse").innerHTML+="Error: You must input a username.<br>";
	}
	else if(passInput ==""){
		document.getElementById("loginResponse").innerHTML+="Error: You must input a password.<br>";
	}
	else if(passInput != "" && userInput != ""){
		xmlhttp = new XMLHttpRequest();
		xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            	try {
            		var JSONobject = JSON.parse(xmlhttp.responseText);
            		loginconfirm = new XMLHttpRequest();
            		var loginstatement = "username="+userInput+"&password="+passInput;
            		//create a new request to an internal page, which sets the user's username and password as the session
            		loginconfirm.open("POST", "http://web.engr.oregonstate.edu/~waltmanr/loginconfirm.php", true);
            		loginconfirm.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            		loginconfirm.send(loginstatement);
            		loginconfirm.onreadystatechange = function(){
            			if (loginconfirm.readyState == 4 && loginconfirm.status == 200){
            				//redirect on successful login
            				window.location.href = "http://web.engr.oregonstate.edu/~waltmanr/projectdisplay.php"
            			}
            		}
            	}
            	catch(err){
                	document.getElementById("loginResponse").innerHTML+=xmlhttp.responseText;
                }
                
                }
            }
        var statement = "username="+userInput+"&password="+passInput+"&action=trylogin";
        xmlhttp.open("POST", "http://twittercopy-1104.appspot.com", true);
        xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xmlhttp.send(statement);
	}
}
function tryRegister(userInput, passInput, passInput2){
	//attempt to create a new user login
	document.getElementById("registerResponse").innerHTML="";
	if(userInput == ""){
		document.getElementById("registerResponse").innerHTML+="Error: You must input a username.<br>";
	}
	else if(passInput ==""){
		document.getElementById("registerResponse").innerHTML+="Error: You must input a password.<br>";
	}
	else if(passInput != passInput2){
		document.getElementById("registerResponse").innerHTML+="Error: Passwords do not match.<br>";
	}
	else if(passInput != "" && userInput != ""){
		xmlhttp = new XMLHttpRequest();
		xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                try {
            		var JSONobject = JSON.parse(xmlhttp.responseText);
            		//output notification on successful creation
            		document.getElementById("registerResponse").innerHTML+="Username " + userInput + " successfully registered! You may now log in above.";
            	}
            	catch(err){
                	document.getElementById("registerResponse").innerHTML+=xmlhttp.responseText;
                }
            }
        }
        var statement = "username="+userInput+"&password="+passInput+"&action=adduser";
        xmlhttp.open("POST", "http://twittercopy-1104.appspot.com", true);
        xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xmlhttp.send(statement);
    }
}
</script>
</head>
<body>
	<?php
	//this fires if the user is sent back here from the child pages and logs the user out, otherwise it's ignored
	if(isset($_GET['logout']) && $_GET['logout']==true){
		$_SESSION = array();
		session_destroy(); 
		//echo "You have been logged out. <br>";

	}
	?>
	<div class ="title">
		<p><h1>Not Twitter!</h1></p>
	</div>

	<div id="loginbox">
		<div class="title"><p><h2>Login</h2></p></div>
		<form>
			<label for="username">Username:</label>
			<input type='text' name="userInput" maxlength="30" placeholder="Username" autocorrect=off autocapitalize=off>
			<br>
			<label for="password">Password:</label>
			<input type='password' name="passInput" placeholder="Password" maxlength="12">
			<br class="clear"/>
			<div id="loginbutton"><button type="button" onclick="tryLogin(userInput.value, passInput.value)">Login</button></div>
		</form>
	</div>

	<div id="loginResponse">
	</div>
	<p></p>

	<div id="loginbox">
		<p>
			<div class="title"><p><h2>Register New Account</h2></p></div>
			<form>
				<label for="newuser">Username:</label>
				<input type="text", name="newUserInput", maxlength="30" autocorrect=off autocapitalize=off placeholder="Username">
				<br>
				<label for="newpass">Password:</label>
				<input type="password", name="newPassInput", maxlength="12" placeholder="Password">
				<label for="newpass2">Confirm Password:</label>
				<input type="password", name="newPassInput2", maxlength="12" placeholder="Repeat Password">
				<br class="clear"/>
				<div id="loginbutton"><button type="button" onclick="tryRegister(newUserInput.value, newPassInput.value, newPassInput2.value)">Register</button></div>
			</form>
		</p>
	</div>

	<div id="registerResponse">
	</div>

</body>
</html>