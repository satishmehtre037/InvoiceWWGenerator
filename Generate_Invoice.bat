@echo off
title Wanderworld Holidays - Invoice Generator
cd /d "%~dp0"
python generate_invoice.py
pause
