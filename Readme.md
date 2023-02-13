# mqtt_respeaker_pixel_ring
***A python mqtt <-> Respeaker pixel ring***

This project will allow you to read and write messages on an MQTT broker and to interact with a [Respeaker module](https://wiki.seeedstudio.com/ReSpeaker_6-Mic_Circular_Array_kit_for_Raspberry_Pi/)

# How to run
I'd suggest using docker; please have a look at the docker-compose.yaml file in the root of the main folder for details.  
If you want to try it out of the box (provided you have installed both docker and docker-compose) just run:
```
mkdir mqtt_respeaker_pixel_ring
cd mqtt_respeaker_pixel_ring
wget https://raw.githubusercontent.com/jacopomaroli/mqtt_respeaker_pixel_ring/master/docker-compose.yml
wget https://raw.githubusercontent.com/jacopomaroli/mqtt_respeaker_pixel_ring/master/config.example.yaml
wget https://raw.githubusercontent.com/jacopomaroli/mqtt_respeaker_pixel_ring/master/env.example
cp config.example.yaml config.yaml
cp env.example .env
# edit the .env file with your mqtt broker informations
docker-compose up -d
```

# Configuration
The configuration system relies on [rule-engine](https://zerosteiner.github.io/rule-engine/). Please refer to their docs for a more complex ruleset

# Limitations
For now only button up/down events are supported. Implementing long-presses and doubleclicks should be fairly trivial and support for it might be added in the future should there be any interest for it.

## Donations
If this project makes your life better in any way and you feel like showing appreciation you can buy me a coffee here  
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=MNGDSC849AS6A)
