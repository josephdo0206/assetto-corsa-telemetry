import socket
import struct

# --- QA TEST PROFILES ---
CAR_REDLINES = {
    'p3_mitsubishi_evo8': 7700,
    'some1_honda_nsx_1991': 8700,
}

# 1. Create the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Set a timeout so the script doesn't hang forever if the game isn't running
sock.settimeout(5.0) 

server_address = ('127.0.0.1', 9996)

# 2. Pack and send the initial handshake (Identifier: 1, Version: 1, Operation: 0)
handshake_message = struct.pack('3i', 1, 1, 0)
print("Sending handshake to Assetto Corsa...")
sock.sendto(handshake_message, server_address)

# 3. Listen for the server's response
try:
    # Buffer size of 4096 is more than enough for the response
    data, address = sock.recvfrom(4096)
    
    # 4. Unpack the handshakerResponse (Adjusted for 408 bytes)
    # Format: 100-byte string, 100-byte string, integer, integer, 100-byte string, 100-byte string
    unpacked_data = struct.unpack('100s 100s i i 100s 100s', data)
    
    # Decode the binary strings using utf-16 and remove null characters
    car_name = unpacked_data[0].decode('utf-16-le', errors='ignore').split('%')[0]
    driver_name = unpacked_data[1].decode('utf-16-le', errors='ignore').split('%')[0]
    track_name = unpacked_data[4].decode('utf-16-le', errors='ignore').split('%')[0]
    track_config = unpacked_data[5].decode('utf-16-le', errors='ignore').split('%')[0]

    print("\n--- Connection Successful! ---")
    print(f"Driver: {driver_name}")
    print(f"Car: {car_name}")
    print(f"Track: {track_name} ({track_config})")

    # --- DYNAMIC BVA SETUP ---
    # Look up the car_name in the dictionary. 
    # The second argument (9000) is a fallback default just in case you load a car 
    # that isn't in your dictionary yet, preventing the script from crashing.
    REDLINE_LIMIT = CAR_REDLINES.get(car_name, 9000)
    is_over_revving = False
    peak_rpm = 0
    gear_at_breach = 0
    defect_count = 0

    print(f"Active QA Profile Loaded: {car_name} | Max RPM: {REDLINE_LIMIT}\n")

    # 5. Subscribe to the continuous physics update stream
    # Identifier: 1, Version: 1, Operation ID: 1 (SUBSCRIBE_UPDATE)
    subscribe_message = struct.pack('3i', 1, 1, 1)
    sock.sendto(subscribe_message, server_address)
    print("Subscribed to live telemetry stream...\n")

    # 6. Catch and unpack the continuous data stream
    try:
        while True:
            physics_data, _ = sock.recvfrom(4096)
            
            # 12x skips the identifier and size. 
            # f reads mph (4 bytes). 
            # 40x skips the rest of the speeds, boolean flags, and coordinates to reach byte 56.
            unpacked_physics = struct.unpack_from('< 12x f 40x f f f f f i', physics_data)
        
            speed_mph = unpacked_physics[0]
            gas = unpacked_physics[1]
            brake = unpacked_physics[2]
            engine_rpm = unpacked_physics[4]
            gear = unpacked_physics[6] - 1 

            # --- QA TEST EXECUTOR: REDLINE BVA ---
        # If RPM crosses the invalid boundary (7700+) and we haven't already flagged it
            if engine_rpm > REDLINE_LIMIT:
                if not is_over_revving:
                    # The exact millisecond the boundary is broken
                    is_over_revving = True
                    peak_rpm = engine_rpm
                    gear_at_breach = gear
                else:
                    # The boundary is still broken. Continuously update the maximum value.
                    if engine_rpm > peak_rpm:
                        peak_rpm = engine_rpm
                    
        # The engine dropped back into the safe zone. The event is over. Log it.
            elif engine_rpm <= REDLINE_LIMIT and is_over_revving:
                is_over_revving = False
                defect_count += 1
                print(f"\n[DEFECT {defect_count}] Redline Exceeded in Gear {gear_at_breach}! Max RPM: {int(peak_rpm)} (Limit: {REDLINE_LIMIT})")

            print(f"Gear: {gear} | Speed: {int(speed_mph)} mph | RPM: {int(engine_rpm)} | Gas: {gas:.2f} | Brake: {brake:.2f}      ", end='\r')

    except KeyboardInterrupt:
        # 7. Gracefully disconnect when you press Ctrl+C
        print("\n\nDisconnecting from telemetry server...")
        # Identifier: 1, Version: 1, Operation ID: 3 (DISMISS)
        dismiss_message = struct.pack('3i', 1, 1, 3)
        sock.sendto(dismiss_message, server_address)
        sock.close()
        print("Disconnected cleanly. Port is free.")

except socket.timeout:
    print("Connection timed out. Make sure Assetto Corsa is actively running a session.")