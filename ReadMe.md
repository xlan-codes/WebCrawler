### For some reason, Mozilla decided [not to be helpful][mozilla] in hiding the WebDriver flag. Notice the deleted comment. So, we are using Chromium

# RPi
```bash
sudo apt-get update
sudo apt-get install python-pip chromium-browser chromium-chromedriver xvfb
pip3 install -r requirements.txt
python3 main.py
```

[mozilla]: https://github.com/mozilla/geckodriver/issues/1680