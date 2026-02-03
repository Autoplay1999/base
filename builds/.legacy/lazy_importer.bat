@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/lazy_importer"
call utils PrepareDest "../bin/lazy_importer/include"
call utils CopyHeaders "../modules/lazy_importer/include" "../bin/lazy_importer/include" "*.hpp"