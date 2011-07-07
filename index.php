<?php include("header.php"); ?>
  <p>Please provide the credentials that you will be using for this session.</p>

  <form action="upload.php" method="post">
    <input type="hidden" name="stage" value="login"/>
    <table>
      <tr>
        <td>Username: </td>
        <td><input type="text" name="username" width="20"/></td>
      </tr>
      <tr>
        <td>Password: </td>
        <td><input type="password" name="password" width="20"/></td>
      </tr>
      <tr>
        <td colspan="2"><input type="submit" value="Login"/></td>
      </tr>
    </table>
  </form>
<?php include("footer.php"); ?>
