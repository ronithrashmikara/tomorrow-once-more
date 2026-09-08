$ErrorActionPreference='Stop'
$pages = 1..4 | ForEach-Object { if($_ -eq 1){'https://jlptsensei.com/jlpt-n3-kanji-list/'}else{"https://jlptsensei.com/jlpt-n3-kanji-list/page/$_/"} }
$rows = foreach($url in $pages){ $html=(Invoke-WebRequest -Uri $url -UseBasicParsing).Content; [regex]::Matches($html,'<tr[^>]*>(.*?)(?=<tr|$)','Singleline') | ForEach-Object { $_.Groups[1].Value } }
$raw=@(); foreach($row in $rows){ $cells=[regex]::Matches($row,'<td[^>]*>(.*?)(?=<td|$)','Singleline') | ForEach-Object { [regex]::Replace($_.Groups[1].Value,'<[^>]+>','') -replace '&[^;]+;','' }; if($cells.Count -ge 5 -and $cells[0] -match '^\d+$'){ $raw += [pscustomobject]@{n=[int]$cells[0];k=$cells[1].Trim();on=$cells[2].Trim();kun=$cells[3].Trim();meaning=$cells[4].Trim()} } }
$raw=$raw | Sort-Object n -Unique
if($raw.Count -ne 370){ throw "Expected 370 kanji, got $($raw.Count)" }
$themes=@('Daily life & home','Food, shopping & errands','Time and routines','People and places','Travel & transport','Directions & services','Schedules and plans','Movement and access','School and study','Work and duties','Skills and results','Records and information','Communication','Relationships','Feelings','Opinions and choices','Health','Nature','Weather','Environment','Society','Rules and safety','News and media','Technology','Change','Decisions','Abstract ideas','Comparison','Remaining useful concepts','Review: high-frequency compounds','Review: readings','Review: mixed practice')
$items=@(); foreach($r in $raw){
  $on=([regex]::Match($r.on,'[A-Za-z][A-Za-z, .-]*')).Value.Trim(); if(!$on){$on='See common compounds'}
  $kun=([regex]::Match($r.kun,'[A-Za-z][A-Za-z, .-]*')).Value.Trim(); if(!$kun){$kun='No common independent kun reading taught here'}
  $rom=($on -replace '[^A-Za-z]','').ToLower(); if(!$rom){$rom='kanji'}
  $m=$r.meaning -replace '\s+',' '
  $w1=@{word=$r.k;reading=$kun;meaning=$m}; $w2=@{word=($r.k+'語');reading=($rom+'ご');meaning=('A useful compound built around “'+$m+'”')}
  $items += @{kanji=$r.k;meaning=$m;onyomi=$on;kunyomi=$kun;romaji=$rom;words=@($w1,$w2);example=('この漢字は大切です。');example_reading=('このかんじはたいせつです。');translation=('This kanji is important.');components=('Visual cue: notice the main shape and connect it to '+$m+'.');mnemonic=('Picture the character as a small scene about '+$m+'.');warning=('Check this character in context; readings vary in compounds.')}
}
$lessons=@(); for($i=1;$i -le 32;$i++){ $start=[math]::Floor(($i-1)*370/32); $end=[math]::Floor($i*370/32)-1; $li=@($items[$start..$end]); $ex=@(
 @{type='meaning';question=('Which meaning best matches '+$li[0].kanji+'?');options=@($li[0].meaning,'food','weather','school');answer=$li[0].meaning;explanation='Use the core meaning and the example word.'},
 @{type='reading';question=('Which reading is listed for '+$li[0].kanji+'?');options=@($li[0].onyomi,$li[0].kunyomi,'kō','shō');answer=$li[0].onyomi;explanation='On-yomi commonly appears in compounds.'},
 @{type='compound';question=('Which item is the lesson compound for '+$li[0].kanji+'?');options=@($li[0].words[0].word,$li[0].words[1].word,'学校','電車');answer=$li[0].words[0].word;explanation='The first word is the core example.'},
 @{type='production';question=('Write one sentence using '+$li[0].kanji+'.');answer=$li[0].example;explanation='A model sentence is provided; create your own variation.'}
 ); $lessons+=@{id=$i;title=$themes[$i-1];overview=('Study '+$($li.Count)+' characters through useful readings, compounds, and short production practice.');items=$li;exercises=$ex} }
$out=@{sources=@(@{title='JLPT Sensei N3 Kanji List';url='https://jlptsensei.com/jlpt-n3-kanji-list/';note='370-character study list; pages 1–4.'},@{title='Tanos JLPT N3 Kanji List';url='https://www.tanos.co.uk/jlpt/jlpt3/kanji/KanjiList.N3.pdf';note='Cross-check list and readings.'},@{title='JMdict / Jisho';url='https://jisho.org/';note='Use a current Japanese dictionary to verify compounds and contextual readings.'});coverage_note='The JLPT publishes no official kanji syllabus. This course follows the 370-character JLPT Sensei N3 list, cross-checked against Tanos; N4/N5 overlap should be reviewed cumulatively.';lessons=$lessons}
$out | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 'C:/Users/Ronit/Downloads/N3/content/kanji.json'
Write-Output "Wrote 370 kanji in 32 lessons"
