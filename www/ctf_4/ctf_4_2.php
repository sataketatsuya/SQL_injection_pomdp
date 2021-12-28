<?php
/*

FLAG_{EasySQLiForBeginners}

*/

require '../const.php';

ini_set('display_errors', 0);
$pdo = null;

try{
    $database = 'mysql:dbname=ctf;host='.$DBipaddress;
    $pdo = new PDO($database, $DBuser, $DBpass);
} catch(PDOException $e) {
    echo $e->getMessage();
}

if (isset($_POST["id"]) && $pdo) {
    $uq = $pdo->query("SELECT loginid,auth_bit FROM users WHERE (loginid = \"{$_POST['id']}\") AND (password = \"{$_POST['pw']}\")")->fetchAll();
    if(count($uq) > 0){$uq = $uq[0];}
    if(isset($uq["auth_bit"])){
        if($uq["auth_bit"] == "1023"){
            print "If you want to read the Flag. Read ME!";
            // phpinfo();
            exit();
        }

        printLoginForm($uq["loginid"] . " is Not Admin User.", $uq);
        exit();
    }
    printLoginForm($_POST["id"] . " Not Found", $uq);
} else {
    printLoginForm();
}


function printLoginForm($error = "", $uq = "") {
?>
<!doctype html>
<html>
<head>
<title>Login</title>
<style>
#wrapper {
    width: 800px;
    margin: 0 auto;
    text-align : center ;
    border:1px ridge;
}
fieldset {
    border:0px;
}
</style>
</head>
<body>
<div id="wrapper">
<?php if ($uq["loginid"] == 1) {echo 'collect column <br>';} ?>
<?php if($error != "") {print $error; } ?>
<form method="POST">
    <fieldset>
        <label>ID</label>
        <input type="text" name="id" size="30">
    </fieldset>
    <fieldset>
        <label>PW</label>
        <input type="password" name="pw" size="30">
    </fieldset>
    <input type="submit" value="Login">
</form>
</div>
</body>
</html>
<?php
}


function h($str){
    return htmlspecialchars($str,ENT_QUOTES,"UTF-8");
}

?>

