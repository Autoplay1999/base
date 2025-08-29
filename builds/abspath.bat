@echo off
set "_index=0"
:loop
if "%~1"=="" goto :done
set /a "_index+=1"
call set "_result%%_index%%=%%~dpn1"
shift
goto :loop
:done
::set "_result_count=%_index%"
exit /b 0