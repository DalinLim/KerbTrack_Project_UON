import paho.mqtt.client as mqtt
import json
import time

broker = "broker.hivemq.com"
topic = "test/kerbtrack/json_data"

client = mqtt.Client()
client.connect(broker, 1883)

sample_data = [
    {"ID": "1", "GPS": "32.9283° S, 151.7817° E", "Address": "Main St", "Message": "Kerbside Dump Detected", "ImageURL": "https://www.campbelltown.nsw.gov.au/files/sharedassets/public/v/2/services-and-facilities/waste-and-recycling/images/kerbsidecleanup2.jpg?dimension=pageimage&w=480"},
    {"ID": "2", "GPS": "32.9031° S, 151.6696° E", "Address": "North St", "Message": "Kerbside Dump Detected","ImageURL": "https://images.craigslist.org/00808_7iKiQqX0sru_0CI0t2_600x450.jpg"},
    {"ID": "3", "GPS": "32.9267° S, 151.7800° E", "Address": "Hunter St, Newcastle West", "Message": "Kerbside Dump Detected", "ImageURL": "https://images.craigslist.org/00W0W_i7ukNiwZ5VN_0CI0CI_600x450.jpg"},
    {"ID": "4", "GPS": "32.9352° S, 151.7501° E", "Address": "Darby St, Cooks Hill", "Message": "Kerbside Dump Detected", "ImageURL": "https://images.craigslist.org/00W0W_i7ukNiwZ5VN_0CI0CI_600x450.jpg"},
    {"ID": "5", "GPS": "32.9486° S, 151.7263° E", "Address": "Glebe Rd, The Junction", "Message": "Kerbside Dump Detected", "ImageURL": "https://live-production.wcms.abc-cdn.net.au/35bf5d7e6aeee5391a1f3ca84b68fb5a?impolicy=wcms_crop_resize&cropH=1125&cropW=2000&xPos=0&yPos=326&width=862&height=485"},
    {"ID": "6", "GPS": "32.9205° S, 151.7352° E", "Address": "Beaumont St, Hamilton", "Message": "Kerbside Dump Detected", "ImageURL": "https://images.squarespace-cdn.com/content/v1/6338330a337f6700f6f28fc9/aa8dae6e-0e5c-41a6-9646-c8bd36f8116e/wn_hardwaste-_banner.jpg"},
    {"ID": "7", "GPS": "32.9754° S, 151.7102° E", "Address": "John Parade, Merewether", "Message": "Kerbside Dump Detected", "ImageURL": "https://images.craigslist.org/00W0W_i7ukNiwZ5VN_0CI0CI_600x450.jpg"},
    {"ID": "8", "GPS": "32.9025° S, 151.7820° E", "Address": "Industrial Dr, Mayfield", "Message": "Kerbside Dump Detected", "ImageURL": "https://images.craigslist.org/00W0W_i7ukNiwZ5VN_0CI0CI_600x450.jpg"},
    {"ID": "9", "GPS": "32.9672° S, 151.6935° E", "Address": "Pacific Hwy, Charlestown", "Message": "Kerbside Dump Detected", "ImageURL": "https://images.craigslist.org/00W0W_i7ukNiwZ5VN_0CI0CI_600x450.jpg"},
    {"ID": "10", "GPS": "32.9078° S, 151.6679° E", "Address": "Cowper St, Wallsend", "Message": "Kerbside Dump Detected", "ImageURL": "https://images.craigslist.org/00W0W_i7ukNiwZ5VN_0CI0CI_600x450.jpg"}

]

try:
    for loop_num in range(5):  # Loop exactly 5 times (0-4)
        print(f"Starting loop {loop_num + 1}/5")
        for data in sample_data:
            payload = json.dumps(data)       # convert dict to JSON string
            client.publish(topic, payload)  # send to broker
            print("Published:", payload)
            time.sleep(1)  # send a new message every 1 second
        print(f"Completed loop {loop_num + 1}/5")
    
    print("All 5 loops completed! Stopping...")
        
except KeyboardInterrupt:
    print("Stopped sending")

client.disconnect()
print("Disconnected from broker")