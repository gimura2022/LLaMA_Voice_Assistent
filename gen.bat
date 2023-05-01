@echo off

chcp 1251>nul
for %%i in () do chcp 866>nul& echo %%i

(
chat -f input.txt > output.txt
)>nul 2>&1

exit