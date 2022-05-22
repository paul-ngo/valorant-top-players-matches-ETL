#!/usr/bin/sh

declare -A chrome_versions

# Enter the list of browsers to be downloaded
## Using Chromium as documented here - https://www.chromium.org/getting-involved/download-chromium
chrome_versions=( ['101.0.4951.67']='982481')
chrome_drivers=( "101.0.4951.41" )

# Download Chrome
for br in "${!chrome_versions[@]}"
do
    echo "Downloading Chrome version $br"
    mkdir -p "/tmp/"
    curl -Lo "/tmp/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F${chrome_versions[$br]}%2Fchrome-linux.zip?alt=media"
    unzip -q "/tmp/chrome-linux.zip" -d "/tmp/"
    mv /tmp/chrome-linux/* "/usr/local/bin/"
    rm -rf /tmp/chrome-linux/ "/tmp/chrome-linux.zip"
done

# Download Chromedriver
for dr in ${chrome_drivers[@]}
do
    echo "Downloading Chromedriver version $dr"
    mkdir -p "/tmp"
    curl -Lo "/tmp/chromedriver_linux64.zip" "https://chromedriver.storage.googleapis.com/$dr/chromedriver_linux64.zip"
    unzip -q "/tmp/chromedriver_linux64.zip" -d "/usr/local/bin/"
    chmod +x "/usr/local/bin/chromedriver"
    rm -rf "/tmp/chromedriver_linux64.zip"
done