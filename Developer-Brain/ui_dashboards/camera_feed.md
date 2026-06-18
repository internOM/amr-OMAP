# camera_feed

**Parent Node**: [[ui_dashboards]]

## Overview
A lightweight hardware debugging tool used exclusively to inspect what the AGV's vision system is seeing in real-time on the factory floor, ensuring lighting or physical alignment isn't causing faults.

## HTML/JS Components & Displayed Data
- **DOM Elements**: Relies on a hidden HTML5 `<canvas>` element and a visible `<img>` tag to display the frames.
- **Displayed Data**: Renders the live video feed. It also calculates and displays critical performance metrics on-screen, specifically frames per second (FPS) and stream latency (in milliseconds).

## Communication Layer
- **Protocol**: Connects via `rosbridge_websocket` (`roslibjs`).
- **Topics**: Subscribes directly to `/image_raw` or `/image_compressed`.
- **Decoding Logic**: Contains custom, highly optimized JavaScript to decode raw ROS image encodings (`yuyv`, `bgr8`, `mono8`) from base64 strings directly onto the HTML5 Canvas. This eliminates the need for a heavy backend video stream server like `web_video_server`.
- **Backend Node**: Pulls data directly from the `usb_cam_node_exe` (initiated in `bringup_launch`), providing a visual sanity check before the images are consumed and processed by the [[webcam_line_follow]] node in `core_node_architectures`.

## Integration
- Serves as the primary diagnostic tool mentioned in [[ui_integration_flow]] to ensure that physical floor lines fall squarely within the HSV masking thresholds.
