cd %~dp0
scrapy crawl jav
set yy = %date:~3,4%
set mm = %date:~8,2%
set dd = %date:~11,2%
"c:\Program Files\7-Zip\7z.exe" a -pjav%yy%%mm%%dd% -mhe jav%yy%%mm%%dd% d:\jav-project\output\%yy%%mm%%dd% -o d:\jav-project\output\