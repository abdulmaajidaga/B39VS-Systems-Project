import rclpy
from rclpy.node import Node
from pydub import AudioSegment
from pydub.playback import play
from std_srvs.srv import Empty
from hazmat_msgs.srv import String
import threading

# Global variable to control playback
playback_thread = None
stop_flag = threading.Event()

class AudioService(Node):
    def __init__(self):
        super().__init__('audio_player')
        self.start_service = self.create_service(String, 'start_audio', self.start_audio_callback)
        self.stop_service = self.create_service(Empty, 'stop_audio', self.stop_audio_callback)
        self.get_logger().info("Audio player services are ready.")

    def play_audio(self, file_path):
        global stop_flag
        stop_flag.clear()
        try:
            audio = AudioSegment.from_file(file_path, format="mp3")
            chunk_length = 100  # milliseconds
            for i in range(0, len(audio), chunk_length):
                if stop_flag.is_set():
                    break
                play(audio[i:i + chunk_length])
        except Exception as e:
            self.get_logger().error(f"Error playing audio: {e}")

    def start_audio_callback(self, request, response):
        global playback_thread
        
        if playback_thread and playback_thread.is_alive():
            self.get_logger().warn("Audio is already playing!")
            return String.Response(data="Audio is already playing")
        
        playback_thread = threading.Thread(target=self.play_audio, args=(request.data,))
        playback_thread.start()
        return String.Response(data="Playing audio")

    def stop_audio_callback(self, request, response):
        global stop_flag, playback_thread
        
        stop_flag.set()
        
        if playback_thread:
            playback_thread.join()
        
        return Empty.Response()

def main(args=None):
    rclpy.init(args=args)
    node = AudioService()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
