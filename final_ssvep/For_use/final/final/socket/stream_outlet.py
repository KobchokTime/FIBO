import time
import pyxdf
from pylsl import StreamInfo, StreamOutlet

# Load the .xdf file
xdf_file_path = '../../../../../data_ssvep/Toey/SSVEP_data/test/20Hz/20hz_10'
data, header = pyxdf.load_xdf(xdf_file_path)

# Assume the first stream in the file is the one you want to stream
stream_data = data[0]['time_series']
stream_srate = data[0]['info']['effective_srate']
num_channels = stream_data.shape[1]

# Create LSL stream info
stream_name = data[0]['info']['name'][0]
print(stream_name)
stream_type = data[0]['info']['type'][0]
info = StreamInfo(stream_name, stream_type, num_channels, stream_srate, 'float32', 'myuid34234')

# Create LSL outlet
outlet = StreamOutlet(info)

# Stream the data in real-time
for sample in stream_data:
    outlet.push_sample(sample)
    time.sleep(1.0 / stream_srate)  # Sleep to match the sampling rate

print("Streaming complete.")