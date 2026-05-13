#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import asyncio
import websockets
import json
import threading
from datetime import datetime


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
        self.rack_data = {}
        
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
            
    async def _handle_client(self, websocket, path):
        """Handle incoming WebSocket connections from ESP32 racks"""
        
        client_address = websocket.remote_address
        self.get_logger().info(f'Client connected: {client_address[0]}:{client_address[1]}')
        
        try:
            async for message in websocket:
                # Parse JSON message from ESP32
                try:
                    data = json.loads(message)
                    rack_id = data.get("rack_id", "UNKNOWN")
                    status = data.get("status", 0)
                    distance = data.get("distance_cm", 0.0)
                    
                    # Store latest data
                    self.rack_data[rack_id] = {
                        "status": status,
                        "distance_cm": distance,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Log received data
                    status_text = "FULL" if status == 1 else "EMPTY"
                    self.get_logger().info(
                        f'[{rack_id}] Status: {status_text} | Distance: {distance:.1f} cm'
                    )
                    
                    # Publish to ROS2 topic
                    self._publish_rack_status(rack_id, status, distance)
                    
                except json.JSONDecodeError as e:
                    self.get_logger().error(f'Invalid JSON received: {message}')
                except Exception as e:
                    self.get_logger().error(f'Error processing message: {e}')
                    
        except websockets.exceptions.ConnectionClosedOK:
            self.get_logger().info(f'Client disconnected: {client_address}')
        except websockets.exceptions.ConnectionClosedError as e:
            self.get_logger().warn(f'Connection closed with error: {e}')
        except Exception as e:
            self.get_logger().error(f'Unexpected error: {e}')
            
    def _publish_rack_status(self, rack_id, status, distance):
        """Publish rack status to ROS2 topic"""
        
        # Create message (using String for now)
        # Format: "rack_id:status:distance"
        msg = String()
        msg.data = f'{rack_id}:{status}:{distance:.1f}'
        
        self.rack_status_pub.publish(msg)
        

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