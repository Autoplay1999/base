@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/semver"
call utils PrepareDest "../bin/neargye/include/neargye/semver"
call utils CopyRecursive "../modules/semver/include/semver" "../bin/neargye/include/neargye/semver"
