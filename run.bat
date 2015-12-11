setlocal EnableDelayedExpansion
cd %~dp0
scrapy crawl jav

cd d:\jav-project\output
for /f "delims=" %%s in ('dir /a:d /b') do (
	set date1=%%s
	echo !date1:-=!
	"c:\Program Files\7-Zip\7z.exe" a -pjav!date1:-=! -mhe jav!date1:-=! d:\jav-project\output\!date1!\
	copy jav!date1:-=!.7z %~dp0\jav-project\
) 
cd %~dp0