FROM mcr.microsoft.com/windows:2004

# Install chocolatey
RUN @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
RUN choco feature enable -n allowGlobalConfirmation

WORKDIR C:\\tools

# Set driver/browser versions
ARG Selenium_Major_Version="3.141"
ARG Selenium_Version="3.141.59"
ARG MOZ_HEADLESS=1

ARG GeckoDriver_Version="0.26.0"
ARG Firefox_Version="66.0.3"

RUN choco install vcredist2015

# Install Java
RUN choco install jdk8

RUN choco install selenium-gecko-driver

# Download Selenium
RUN powershell Invoke-WebRequest \
    -Uri "https://selenium-release.storage.googleapis.com/$env:Selenium_Major_Version/selenium-server-standalone-$env:Selenium_Version.jar" \
    -OutFile ".\\selenium-server-standalone.jar"
	
# Install Firefox
RUN choco install firefox-nightly --pre

EXPOSE 4444

ENTRYPOINT java \
    -Dwebdriver.gecko.driver=C:\\tools\\selenium\\geckodriver.exe \
    -jar selenium-server-standalone.jar \
    -role standalone \
    -debug