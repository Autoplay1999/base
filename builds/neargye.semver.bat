@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/semver"
call utils PrepareDest "../bin/neargye/include/neargye/semver"
call utils CopyHeaders "../modules/semver/include" "../bin/neargye/include/neargye/semver"
