import pyaudio
p = pyaudio.PyAudio()
print("PyAudio version:", pyaudio.__version__)
print("Default input device info:")
try:
    print(p.get_default_input_device_info())
except IOError as e:
    print(f"Error getting default input device: {e}")
    print("This might indicate PyAudio cannot access any microphone.")

print("\nAvailable devices:")
for i in range(p.get_device_count()):
    try:
        info = p.get_device_info_by_index(i)
        print(f"  {i}: {info['name']} (Input Channels: {info['maxInputChannels']}, Output Channels: {info['maxOutputChannels']})")
    except Exception as e:
        print(f"  Could not get info for device {i}: {e}")
p.terminate()