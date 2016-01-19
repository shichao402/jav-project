setlocal EnableDelayedExpansion
cd %~dp0
scrapy crawl jav

cd %~dp0\output
for /f "delims=" %%s in ('dir /a:d /b') do (
	set date1=%%s
	echo !date1:-=!
	"c:\Program Files\7-Zip\7z.exe" a -pjav!date1:-=! -mhe jav!date1:-=! %~dp0\output\!date1!\
	xcopy /S /Y %~dp0\output\jav!date1:-=!.7z D:\48822512\jav-project\archive\
	del %~dp0\output\jav!date1:-=!.7z
) 
xcopy /S /Y %~dp0\output\* D:\48822512\jav-project\
cd %~dp0