@ECHO OFF
setlocal enabledelayedexpansion
cd /D %~dp0

set wifi=无线网络连接
set local=本地连接
set logfile=switch_interface_%random%.log
set step=0

:AUTO
if !step!==99 (
	GOTO go_local
)
if !step!==0 (
	netsh interface ipv4 show interface > %temp%\%logfile%
	findstr "%wifi%" %temp%\%logfile% >nul 2>&1 && (
		set step=local
		echo wifi > pre_network_status
	)
	findstr "%local%" %temp%\%logfile% >nul 2>&1 && (
		set step=wifi
		echo local > pre_network_status
	)
	::根据参数强行切换
	if "%1" neq "" (
		if "%1"=="local" (
			set step=local
		)
		if "%1"=="wifi" (
			set step=wifi
		)
	)
	set target=!step!
	echo 开始自动切换到!step!
	GOTO go_!step!
) else (
	@ping -n 10 127.1>nul
	GOTO go_!step!_after
)
GOTO AUTO

:go_wifi
::echo 关闭rtx..
::taskkill /F /FI "IMAGENAME eq RTX*"
echo 关闭foxmail..
taskkill /F /FI "IMAGENAME eq Foxmail*"
echo 关闭proxifier..
taskkill /F /FI "IMAGENAME eq Proxifier*"

echo 关闭本地网络...
netsh interface set interface %local% DISABLED
echo 打开无线网络...
netsh interface set interface %wifi% ENABLED

GOTO AUTO
 
:go_local
echo 关闭无线网络...
netsh interface set interface %wifi% DISABLED
echo 打开本地网络...
netsh interface set interface %local% ENABLED
GOTO AUTO

:go_wifi_after
set step=end
GOTO AUTO

:go_local_after
::start /min "" "%LOCALAPPDATA%\Tencent\RTXLite\Application\RtxLite.exe"
start /min "" "C:\foxmail 7.2\Foxmail.exe"
start /min "" "C:\Program Files (x86)\Proxifier\Proxifier.exe"
set step=end
GOTO AUTO

:go_end_after
netsh interface ipv4 show interface
if !target!==wifi (
	set check_string_open=%wifi%
	set check_string_close=%local%
)
if !target!==local (
	set check_string_open=%local%
	set check_string_close=%wifi%
)
set check_open_found=0
set check_close_found=0
set switch_success=0
netsh interface ipv4 show interface > %temp%\%logfile%
findstr "%check_string_open%" %temp%\%logfile% >nul 2>&1 && (set check_open_found=1)
findstr "%check_string_close%" %temp%\%logfile% >nul 2>&1 && (set check_close_found=1)

if "!check_open_found!"=="1" (
	if "!check_close_found!"=="0" (
		set switch_success=1
		echo 切换成功
		if "%2" neq "no_close" (
			echo ...60秒后自动关闭
			@ping -n 60 127.1>nul
			@exit
		)
	)
)
if !switch_success!==1 (
	GOTO go_quit
) else (
	echo 切换失败...默认恢复到local网络
	set step=0
	GOTO AUTO
)
GOTO AUTO
:go_quit