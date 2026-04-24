[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$fichier, # fichier ou dossier a parcourir
    [int]$padding = 12, # le nombre de sous repertoires retenu lors de la creation du fichier de fichiers
  	[switch]$plus10ans,
  	[switch]$plus5ans,
    [Parameter(Mandatory=$true)][string]$pathOutput,
    [Parameter(Mandatory=$true)][string]$xanPath
    )

          
$fichierSortie = "output.csv"
$maxDepth = 30 # pour la commande Get-ChildItem, "garde fou" contre des niveaux d'imbrications delirants...

$fieldSep = ','

# le fichier est a priori un dossier(repertoire)
# l'arborescence decouverte est entierement embarquee dans la variable suivante
  $results = @()
  
  $maxPathLength = 0
  $overallLength = 0	
	
#Get all files in $dossier (Recursive)
  #Write-Host "Acquisition des fichiers..."
  if ($plus10ans) {
    $Files = Get-childitem -Path "$fichier" -File -Recurse -Force -Depth $maxDepth -ErrorAction SilentlyContinue | Where-Object {$_.lastwritetime -lt (get-date).addDays(-3650)}   
	  
  } elseif ($plus5ans) {
    $Files = Get-childitem -Path "$fichier" -File -Recurse -Force -Depth $maxDepth -ErrorAction SilentlyContinue | Where-Object {$_.lastwritetime -lt (get-date).addDays(-1825)}   
	  
  } else {
    $Files = Get-childitem -Path "$fichier" -File -Recurse -Force -Depth $maxDepth -ErrorAction SilentlyContinue   
	  
  }
  
#pour suivi progression
  $NumberofFiles = $Files.Length
  $NumberLength = $NumberofFiles.ToString().Length;$NumberLengthString = ""
  for($i=0;$i -lt $NumberLength;$i++){$NumberLengthString = $NumberLengthString + "0"}

#Get longest path (not most characters but deepest path)
    #Write-Host "Calcul du chemin le plus long..."
    foreach ($file in $Files) {
      $fullname = $file.FullName
      $onlypath = Split-Path -Path "$fullname" -Parent
      $pathArray = $onlypath -split "\\"
      if($pathArray.Length -gt $maxPathLength){$maxPathLength = $pathArray.Length}
    }
    $fullname = "";$onlypath="";$pathArray=@()
#Compare le chemin le plus long avec le padding choisi
    if($maxPathLength -gt $padding){
      $padding=$maxPathLength
    }
  $index = 1
#Get Date, path, name and size of all files in a .csv
  foreach ($file in $Files) {
    $Year = $file.LastWriteTime.Year
    $fullname = $file.FullName;$onlypath = Split-Path -Path "$fullname" -Parent;
    #Separate the path (by \) in an array
    $pathArray = $onlypath -split "\\"
    $overallLength = $overallLength + $file.Length
    $details = [ordered] @{
            timestamp = $Year
        }
    $stringpath = ""
    for($i=0;$i -lt $padding;$i++) {
        $details["path"+$i.ToString()] = $pathArray[0..$i] -join "/"
    }
    $details["Name"] = $file;$details["Size"] = $file.Length
    $results += New-Object PSObject -Property $details
    $percentDone = [math]::Round(100*$index/$NumberofFiles,2).ToString('00.00')
    $shortfilename = $file.Name[0..59] -join '';$indexpadded = $index.ToString($NumberLengthString) 
    #Write-Host $shortfilename.PadRight(64) "$indexpadded/$NumberofFiles $percentDone% Done"
    Write-Host $percentDone
    $index++
  }
  
  $onlydossier = Split-Path -Path $fichier -leaf 
  #Write-Host $onlydossier "=" $overallLength Bytes "|"([math]::Round([double]$overallLength/1kb,2)) kB "|"([math]::Round([double]$overallLength/1Mb,2)) MB "|"([math]::Round([double]$overallLength/1Gb,2)) GB -ForegroundColor Green

  $results | export-csv -Path "$pathOutput\temp.csv" -NoTypeInformation -Encoding UTF8
  &$xanPath\xan.exe sort -s 0 -o "$pathOutput\$fichierSortie" "$pathOutput\temp.csv"
  #Write-Host "Fichier ecrit: " $pathOutput"\"$fichierSortie
  #$npipeClient.Dispose()
  
  del "$pathOutput\temp.csv"
  

### Etienne THOMAS & Alain THOMAS... DGFIP 2025
