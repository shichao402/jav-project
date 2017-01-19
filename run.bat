setlocal EnableDelayedExpansion
cd /D %~dp0

:: 无论怎样, 切换到wifi
call "switch.bat" wifi no_close

::读取之前的网络状态
for /f  %%i  in (pre_network_status) do (
	set prenetwork=%%i
)

echo start scrapy
scrapy crawl jav

if "!prenetwork!" neq "wifi" (
	:: 切换之前是local,才需要恢复成local
	call "D:\Program Files\switch.bat" local no_close
)

call sync.ffs_batch
