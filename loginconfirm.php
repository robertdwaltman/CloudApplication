<?php
session_start();
error_reporting(E_ALL);
ini_set('display_errors', 'On');

$_SESSION['username'] = $_POST['username'];
$_SESSION['password'] = $_POST['password'];
echo "Success"

?>