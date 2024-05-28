import socket
import threading
import subprocess
import time

def run_script(script_name):
    subprocess.run(["python", script_name])

def send_message_to_server(client_socket):
    while True:
        # Send message to the server
        message = "receiver.running = True"
        try:
            client_socket.send(message.encode('utf-8'))
            print("Message sent to server")
        except Exception as e:
            print(f"Failed to send message to server: {e}")
            client_socket.close()
            exit(1)

        time.sleep(4)  # Wait for 6 seconds before sending the next message

if __name__ == "__main__":
    # Set the IP address and port of the server
    server_ip = '192.168.1.110'  # Replace with the IP address of the server
    server_port = 6000

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    try:
        client_socket.connect((server_ip, server_port))
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        client_socket.close()
        exit(1)

    # Start a thread to continuously send messages to the server
    send_thread = threading.Thread(target=send_message_to_server, args=(client_socket,))
    send_thread.start()

    # Start threads to run scripts
    script1_thread = threading.Thread(target=run_script, args=("6hz.py",))
    script2_thread = threading.Thread(target=run_script, args=("20hz.py",))

    script1_thread.start()
    script2_thread.start()

    # Wait for the threads to finish
    script1_thread.join()
    script2_thread.join()

    # Close the socket when done
    client_socket.close()

    print("Both scripts have finished executing.")
