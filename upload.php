<?php

include("header.php");
include("language.php");

// Read username/password from form
if($_POST['stage'] == 'login') {
  $httpDigest = base64_encode($_POST['username'] . ':' . $_POST['password']);
  // Get SWORD service document
  $url = parse_url("http://cnx.org/sword");
  $host = 'cnx.org';
  $port = 80;
  $path = '/sword';

  $connection = fsockopen($host, $port, $errno, $errstr, 60);
  if($connection) {
    fputs($connection, "GET $path HTTP/1.1\r\n");
    fputs($connection, "Host: $host\r\n");
    fputs($connection, "Accept: */*\r\n");
    fputs($connection, "Authorization: Basic $httpDigest\r\n");
    fputs($connection, "Connection: close\r\n");
    fputs($connection, "\r\n");
 
    $response = ''; 
    while(!feof($connection)) {
      // receive the results of the request
      $response .= fgets($connection, 128);
    }
  }
  fclose($connection);
  
  // Read available collections from the service document
  $pos = 0;
  $swordCollections = array();
  while(true) {
    // Get url
    $substr = '<collection href="';
    $pos0 = stripos($response, $substr, $pos);
    if($pos0 === FALSE)
      break;
    $pos0 += strlen($substr);
    $pos1 = stripos($response, '">', $pos0);
    $url = substr($response, $pos0, $pos1-$pos0);
    $pos = $pos1;
    // Get collection entity extent
    $posCollectionEnd = stripos($response, '</collection>', $pos);
    // Get title
    $substr = '<atom:title>';
    $pos0 = stripos($response, $substr, $pos);
    if(($pos0 === FALSE) || ($pos0 > $posCollectionEnd))
      break;
    $pos0 += strlen($substr);
    $pos1 = stripos($response, '</atom:title>', $pos0);
    $title = substr($response, $pos0, $pos1-$pos0);
    $pos = $pos1;
    // Check that it accepts zip files
    $pos0 = stripos($response, '<accept>application/zip</accept>', $pos);
    if(($pos0 === FALSE) || ($pos0 > $posCollectionEnd))
      break;
    // Store
    $swordCollections[] = $url;
    $swordCollections[] = $title;
  }
} else {
  $httpDigest = $_POST['cred'];
  $swordCollections = $_POST['collections'];
}

$formFields = array(
  "url" => null,
  "title" => null,
  "abstract" => null,
  "keywords" => null,
  "language" => "en",

  "keepUrl" => TRUE,
  "keepTitle" => FALSE,
  "keepAbstract" => FALSE,
  "keepKeywords" => TRUE,
);

// Upload submission to Connexions
if($_POST['stage'] == 'upload') {

  // Parse form contents
  $formFields['url'] = $_POST['url'];
  $formFields['title'] = $_POST['title'];
  $formFields['abstract'] = $_POST['abstract'];
  $formFields['keywords'] = $_POST['keywords'];
  $formFields['language'] = $_POST['language'];

  $formFields['keepUrl'] = isset($_POST['keepUrl']);
  $formFields['keepTitle'] = isset($_POST['keepTitle']);
  $formFields['keepAbstract'] = isset($_POST['keepAbstract']);
  $formFields['keepKeywords'] = isset($_POST['keepKeywords']);

  $url = $formFields['url']; //"http://localhost:8080/Members/user1/sword";
  $title = $formFields['title']; //"TITLE";
  $abstract = $formFields['abstract']; //"ABSTRACT LINE 1\nABSTRACT LINE 2";
  $language = $formFields['language']; //"af";
  $keywords = $formFields['keywords']; //"KEYWORD1\nKEYWORD2\nKEYWORD3\n";

  $keywordArray = explode("\n", trim($keywords));
  $newKeywordArray = array();
  foreach($keywordArray as $keyword) {
    $keyword = trim($keyword);
    if($keyword != '')
      $newKeywordArray[] = "<bib:keywords>$keyword</bib:keywords>";
  }
  $keywordArray = $newKeywordArray;

  // Process uploaded files
  $uploadFiles = array();
  foreach(array('file1','file2','file3') as $fileRef) {
    if(isset($_FILES[$fileRef]) and ($_FILES[$fileRef]['error'] == 0)) {
      $zipName = basename($_FILES[$fileRef]['name']); // The name of the file inside the zip archive
      $inputName = $_FILES[$fileRef]['tmp_name']; // The uploaded file to zip
      $uploadFiles[] = array('inputName' => $inputName, 'zipName' => $zipName);
    }
  }

  // Create and zip METS file
  $zipFile = tempnam("tmp", "zip");
  $zipArchive = new ZipArchive();
  $zipArchive->open($zipFile, ZipArchive::OVERWRITE);
  $zipArchive->addFromString('mets.xml', '<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<mets ID="sort-mets_mets" OBJID="sword-mets" LABEL="DSpace SWORD Item" PROFILE="DSpace METS SIP Profile 1.0" xmlns="http://www.loc.gov/METS/" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd">

  <metsHdr CREATEDATE="2008-09-04T00:00:00">
    <agent ROLE="CUSTODIAN" TYPE="ORGANIZATION">
      <name>Unknown</name>
    </agent>
  </metsHdr>

  <dmdSec ID="sword-mets-dmd-1" GROUPID="sword-mets-dmd-1_group-1">
    <mdWrap LABEL="SWAP Metadata" MDTYPE="OTHER" OTHERMDTYPE="EPDCX" MIMETYPE="text/xml">
      <xmlData>
        <epdcx:descriptionSet xmlns:epdcx="http://purl.org/eprint/epdcx/2006-11-16/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://purl.org/eprint/epdcx/2006-11-16/ http://purl.org/eprint/epdcx/xsd/2006-11-16/epdcx.xsd">
          <epdcx:description epdcx:resourceId="sword-mets-epdcx-1">
            <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/title">
              <epdcx:valueString>' . $title . '</epdcx:valueString>
            </epdcx:statement>
            <epdcx:statement epdcx:propertyURI="http://purl.org/dc/terms/abstract">
              <epdcx:valueString>' . $abstract . '</epdcx:valueString>
            </epdcx:statement>
            <epdcx:statement epdcx:propertyURI="http://purl.org/eprint/terms/isExpressedAs" epdcx:valueRef="sword-mets-expr-1" />
          </epdcx:description>
          <epdcx:description epdcx:resourceId="sword-mets-expr-1">
            <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/type" epdcx:valueURI="http://purl.org/eprint/entityType/Expression" />
            <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/type" epdcx:vesURI="http://purl.org/eprint/terms/Type" epdcx:valueURI="http://purl.org/eprint/entityType/Expression" />
          </epdcx:description>
	  <epdcx:description epdcx:resourceId="sword-mets-expr-1">
	    <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/type" epdcx:valueURI="http://purl.org/eprint/entityType/Expression" />
	    <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/language" epdcx:vesURI="http://purl.org/dc/terms/RFC3066">
	      <epdcx:valueString>' . $language . '</epdcx:valueString>
	    </epdcx:statement>
	    <epdcx:statement epdcx:propertyURI="http://purl.org/dc/elements/1.1/type" epdcx:vesURI="http://purl.org/eprint/terms/Type" epdcx:valueURI="http://purl.org/eprint/entityType/Expression" />
	    <epdcx:statement epdcx:propertyURI="http://purl.org/eprint/terms/bibliographicCitation">
	      <epdcx:valueString>
		<bib:file xmlns:bib="http://bibtexml.sf.net/">
		  <bib:entry>
                    ' . implode("", $keywordArray) . '
		  </bib:entry>
		</bib:file>
	      </epdcx:valueString>
	    </epdcx:statement>
	  </epdcx:description>
	</epdcx:descriptionSet>
      </xmlData>
    </mdWrap>
  </dmdSec>
</mets>
');

  // Zip uploaded files
  foreach($uploadFiles as $file)
    $zipArchive->addFile($file['inputName'], $file['zipName']);
  $zipArchive->close();

  // Send zip file to SWORD interface
  $url = parse_url($url);
  $host = $url['host'];
  if(!isset($url['port'])) {
    $port = 80;
    $hostPort = $host;
  } else {
    $port = $url['port'];
    $hostPort = $host . ':' . $port;
  }
  $path = $url['path'];

  $connection = fsockopen($host, $port, $errno, $errstr, 60);
  if($connection) {
    fputs($connection, "POST $path HTTP/1.1\r\n");
    fputs($connection, "Host: $hostPort\r\n");
    fputs($connection, "Accept: */*\r\n");
    fputs($connection, "Authorization: Basic $httpDigest\r\n");
    fputs($connection, "Connection: close\r\n");
    fputs($connection, "Content-type: application/zip\r\n");
    fputs($connection, "Content-length: ". filesize($zipFile) ."\r\n");
    fputs($connection, "\r\n");

    $zipHandle = fopen($zipFile, "rb");
    $data = fread($zipHandle, filesize($zipFile));
    fclose($zipHandle);
    fputs($connection, $data);
 
    $result = ''; 
    while(!feof($connection)) {
      // receive the results of the request
      $result .= fgets($connection, 128);
    }
    echo "Success: $result\n";
  } else { 
    echo "Error: $errstr ($errno)\n";
  }
  fclose($connection);

  // Remove temporary zip file
  unlink($zipFile); 
 }

?>
  <p>Please enter the title, etc. below and select the file or files to upload.</p>
  <form enctype="multipart/form-data" action="upload.php" method="POST">
    <input type="hidden" name="stage" value="upload"/>
    <input type="hidden" name="cred" value="<?php echo $httpDigest; ?>"/>
    <input type="hidden" name="MAX_FILE_SIZE" value="2000000"/>
<?php
  for($i = 0; $i < count($swordCollections); $i++)
    echo '    <input type="hidden" name="collections[]" value="' . htmlspecialchars($swordCollections[$i]) . '"/>' . "\n";
?>
    <table cellpadding="4">
      <tr>
        <td></td>
        <td></td>
        <td align="center">Remember?</td>
      </tr>
      <tr>
        <td>Deposit location:</td>
        <td><select name="url" tabindex="1">
<?php
  for($i = 0; $i < count($swordCollections); $i+=2) {
    echo '<option value="' . $swordCollections[$i] . '"';
    if(isset($formFields['url']) and ($swordCollections[$i] == $formFields['url']))
      echo ' selected="selected"';
    echo  '>' . htmlentities($swordCollections[$i+1]) . '</option>' . "\n";
  }
?>
        </select></td>
	<td align="center"><input type="checkbox" disabled="disabled" checked="checked"/></td>
      </tr>
      <tr>
        <td>Title:</td>
        <td><input type="text" name="title" size="50" value="<?php echo ($formFields["keepTitle"] and isset($formFields["title"]))?$formFields["title"]:"";?>" tabindex="2"/></td>
	<td align="center"><input type="checkbox" name="keepTitle" <?php echo $formFields["keepTitle"]?"checked":"";?>/></td>
      </tr>
      <tr>
        <td>Summary:</td>
        <td><textarea name="abstract" rows="10" cols="50" tabindex="3"><?php echo ($formFields["keepAbstract"] and isset($formFields["abstract"]))?$formFields["abstract"]:"";?></textarea></td>
	<td align="center"><input type="checkbox" name="keepAbstract" <?php echo $formFields["keepAbstract"]?"checked":"";?>/></td>
      </tr>
      <tr>
        <td>Keywords:<br/>(one per line)</td>
        <td><textarea name="keywords" rows="5" cols="50" tabindex="4"><?php echo ($formFields["keepKeywords"] and isset($formFields["keywords"]))?$formFields["keywords"]:"";?></textarea></td>
	<td align="center"><input type="checkbox" name="keepKeywords" <?php echo $formFields["keepKeywords"]?"checked":"";?>/></td>
      </tr>
      <tr>
        <td>Language:</td>
        <td><select name="language" tabindex="5">
<?php
foreach($languageOptions as $opt) {
  $code = substr($opt, 15, 2);
  if($code == $formFields["language"]) {
    echo substr($opt, 0, 18) . ' selected="selected"' . substr($opt, 18) . "\n";
  } else {
    echo "$opt\n";
  }
}
?>
        </select></td>
	<td align="center"><input type="checkbox" disabled="disabled" checked="checked"/></td>
      </tr>
      <tr>
        <td>Files:</td>
        <td><input type="file" name="file1" size="50" tabindex="6"/></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td><input type="file" name="file2" size="50" tabindex="7"/></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td><input type="file" name="file3" size="50" tabindex="8"/></td>
        <td></td>
      </tr>
      <tr>
        <td colspan="3" align="right"><input type="submit" value="Upload" tabindex="9"/></td>
      </tr>
    </table>
  </form>
<?php
