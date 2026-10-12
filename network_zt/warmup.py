packet = {"src_port": 51234, "dst_port": 443, "flags": ["SYN", "ACK"]}
print("ACK" in packet["flags"])
print(packet["flags"] == "ACK")
print(packet["dst_port"])
