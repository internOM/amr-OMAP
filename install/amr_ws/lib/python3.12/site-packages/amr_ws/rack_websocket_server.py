#!/usr/bin/env python3

import os
import yaml
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import asyncio
import websockets
import json
import threading
from datetime import datetime

# Path where last-known rack statuses are persisted between runs.
# webcam_line_follow.py reads this file at startup to pre-populate its
# rack_states dict, providing offline resilience when wifi is unavailable.
RACK_STATE_FILE = os.path.expanduser(
    '~/ros2_ws/src/amr_ws/params/rack_state.yaml'
)


class RackWebSocketBridge(Node):
    """
    ROS2 node that runs a WebSocket server to receive data from ESP32 rack sensors
    and publishes the data to a ROS2 topic.
    """
    
    def __init__(self):
        super().__init__('rack_websocket_bridge')
        
        # Declare parameters
        self.declare_parameter('ws_host', '0.0.0.0')
        self.declare_parameter('ws_port', 8000)
        
        # Get parameters
        self.ws_host = self.get_parameter('ws_host').value
        self.ws_port = self.get_parameter('ws_port').value
        
        # Create publisher for rack status
        # Using String for now - you can create custom message later
        self.rack_status_pub = self.create_publisher(
            String,
            '/rack_status',
            10
        )
        
        # Store latest rack data
        # Initialize all 12 slots as disconnected (-1) by default
        self.rack_data = {
            "Store-A1": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "Store-A2": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "Store-A3": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "Store-B1": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "Store-B2": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "Store-B3": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "CAPP-A1": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "CAPP-A2": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "CAPP-A3": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "CAPP-B1": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "CAPP-B2": {"status": -1, "distance_cm": 0.0, "timestamp": None},
            "CAPP-B3": {"status": -1, "distance_cm": 0.0, "timestamp": None},
        }
        
        # Track active WebSocket client connections (dashboards & sensors)
        self.connected_clients = set()
        
        # Track which WebSocket connection maps to which rack_id
        self.sensor_connections = {}
        
        self.get_logger().info('='*50)
        self.get_logger().info('Rack WebSocket Bridge Node Started')
        self.get_logger().info(f'WebSocket Server: {self.ws_host}:{self.ws_port}')
        self.get_logger().info('Publishing to: /rack_status')
        self.get_logger().info('='*50)
        
        # Start WebSocket server in separate thread
        self.ws_thread = threading.Thread(target=self._run_websocket_server, daemon=True)
        self.ws_thread.start()
        
    def _run_websocket_server(self):
        """Run WebSocket server in asyncio event loop"""
        asyncio.run(self._start_server())
        
    async def _start_server(self):
        """Start WebSocket server"""
        self.get_logger().info('Starting WebSocket server...')
        
        async with websockets.serve(
            self._handle_client,
            self.ws_host,
            self.ws_port,
            ping_interval=20,
            ping_timeout=10
        ):
            await asyncio.Future()  # Run forever
            
    async def _broadcast(self, message_str, exclude=None):
        """Broadcast a message to all connected clients (dashboards/sensors)"""
        if not self.connected_clients:
            return
        
        clients = list(self.connected_clients)
        tasks = []
        for client in clients:
            if client != exclude and client.open:
                tasks.append(client.send(message_str))
                
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _handle_client(self, websocket, path):
        """Handle incoming WebSocket connections from ESP32 racks or Web Dashboards"""
        
        client_address = websocket.remote_address
        self.get_logger().info(f'Client connected: {client_address[0]}:{client_address[1]}')
        self.connected_clients.add(websocket)
        
        try:
            # Immediately send the full state to the new client
            await websocket.send(json.dumps({
                "type": "all_states",
                "data": self.rack_data
            }))
            
            async for message in websocket:
                # Parse JSON message from ESP32 or other sources
                try:
                    data = json.loads(message)
                    if "rack_id" in data:
                        raw_rack_id = data.get("rack_id", "UNKNOWN")
                        # Standardize case to match ROS node & HTML dashboard expectations
                        # e.g., convert "STORE-A1" or "store-a1" to "Store-A1", and "capp-b2" to "CAPP-B2"
                        rack_id = raw_rack_id
                        if raw_rack_id.upper().startswith("STORE-"):
                            rack_id = "Store-" + raw_rack_id[6:].upper()
                        elif raw_rack_id.upper().startswith("CAPP-"):
                            rack_id = "CAPP-" + raw_rack_id[5:].upper()
                            
                        try:
                            status = int(data.get("status", 0))
                        except (ValueError, TypeError):
                            status = 0
                        try:
                            distance = float(data.get("distance_cm", 0.0))
                        except (ValueError, TypeError):
                            distance = 0.0
                        
                        if rack_id in self.rack_data:
                            # Map this connection to the rack_id
                            self.sensor_connections[websocket] = rack_id
                            
                            # Store latest data
                            timestamp_str = datetime.now().isoformat()
                            self.rack_data[rack_id] = {
                                "status": status,
                                "distance_cm": distance,
                                "timestamp": timestamp_str
                            }
                            
                            # Log received data
                            status_text = "FULL" if status == 1 else "EMPTY"
                            self.get_logger().info(
                                f'[{rack_id}] Status: {status_text} | Distance: {distance:.1f} cm'
                            )
                            
                            # Publish to ROS2 topic
                            self._publish_rack_status(rack_id, status, distance)

                            # Persist the full snapshot so AGV can read it at boot
                            self._save_rack_state()
                            
                            # Broadcast change to all other connected clients
                            broadcast_msg = json.dumps({
                                "type": "update",
                                "rack_id": rack_id,
                                "status": status,
                                "distance_cm": distance,
                                "timestamp": timestamp_str
                            })
                            await self._broadcast(broadcast_msg, exclude=websocket)
                        else:
                            self.get_logger().warn(f'Received message for unknown rack_id: {rack_id}')
                    
                except json.JSONDecodeError as e:
                    self.get_logger().error(f'Invalid JSON received: {message}')
                except Exception as e:
                    self.get_logger().error(f'Error processing message: {e}')
                    
        except websockets.exceptions.ConnectionClosedOK:
            self.get_logger().info(f'Client disconnected gracefully: {client_address}')
        except websockets.exceptions.ConnectionClosedError as e:
            self.get_logger().warn(f'Connection closed with error: {e}')
        except Exception as e:
            self.get_logger().error(f'Unexpected error: {e}')
        finally:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
                
            if websocket in self.sensor_connections:
                rack_id = self.sensor_connections[websocket]
                del self.sensor_connections[websocket]
                
                # Check if there is another active connection for this rack_id
                if rack_id not in self.sensor_connections.values():
                    timestamp_str = datetime.now().isoformat()
                    self.rack_data[rack_id] = {
                        "status": -1,  # -1 represents disconnected
                        "distance_cm": 0.0,
                        "timestamp": timestamp_str
                    }
                    self.get_logger().warn(f'[{rack_id}] Sensor DISCONNECTED')
                    
                    # Publish disconnected state to ROS2: "rack_id:-1:0.0"
                    self._publish_rack_status(rack_id, -1, 0.0)
                    
                    # Broadcast disconnected state to all other connected clients
                    disconnect_msg = json.dumps({
                        "type": "update",
                        "rack_id": rack_id,
                        "status": -1,
                        "distance_cm": 0.0,
                        "timestamp": timestamp_str
                    })
                    await self._broadcast(disconnect_msg)

                    # Persist the disconnected state so next boot reflects offline sensors
                    self._save_rack_state()
            
    def _publish_rack_status(self, rack_id, status, distance):
        """Publish rack status to ROS2 topic"""
        
        # Create message (using String for now)
        # Format: "rack_id:status:distance"
        msg = String()
        msg.data = f'{rack_id}:{status}:{distance:.1f}'
        
        self.rack_status_pub.publish(msg)

    def _save_rack_state(self):
        """
        Persist the current rack_data snapshot to rack_state.yaml.

        The file is structured so that webcam_line_follow.py can read it with
        a simple yaml.safe_load() call.  Only the integer 'status' field is
        written for each slot — that is the only value the AGV routing logic
        needs for offline resilience.

        Status values:
          1   → FULL   (slot occupied)
          0   → EMPTY  (slot vacant)
         -1   → DISCONNECTED (sensor offline)

        The rack_id keys in rack_data use the websocket casing (e.g. 'Store-A1',
        'CAPP-B3').  We normalise them to the uppercase form that webcam_line_follow
        expects ('STORE-A1', 'CAPP-B3') before writing.
        """
        try:
            # Build a normalised status dict keyed as STORE-XX / CAPP-XX
            rack_states = {}
            for rack_id, info in self.rack_data.items():
                # Normalise casing: 'Store-A1' → 'STORE-A1'
                normalised = rack_id.upper()  # 'CAPP-B2' stays, 'Store-A1'→'STORE-A1'
                rack_states[normalised] = info.get('status', 0)

            payload = {
                '# Rack sensor persistent state — written automatically by rack_websocket_server.py': None,
                '# Do not edit manually while the server is running.': None,
                '# Status values:  1=FULL  0=EMPTY  -1=DISCONNECTED': None,
                'last_updated': datetime.now().isoformat(),
                'rack_states': rack_states,
            }

            path = os.path.realpath(RACK_STATE_FILE)
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Write comment header manually, then dump the data portion
            with open(path, 'w') as f:
                f.write('# Rack sensor persistent state — written automatically by rack_websocket_server.py\n')
                f.write('# Do not edit manually while the server is running.\n')
                f.write('# Status values:  1=FULL  0=EMPTY  -1=DISCONNECTED\n')
                f.write('#\n')
                yaml.dump(
                    {'last_updated': datetime.now().isoformat(), 'rack_states': rack_states},
                    f,
                    default_flow_style=False,
                    sort_keys=True,
                )

        except Exception as e:
            self.get_logger().warn(f'[RackState] Could not save {RACK_STATE_FILE}: {e}')
        

def main(args=None):
    rclpy.init(args=args)
    
    node = RackWebSocketBridge()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down node...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()