# utils/slack.py
import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class SlackManager:
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.channel = os.getenv("SLACK_CHANNEL")

    def list_accessible_channels(self):
        """List all channels the bot can access (public/private)."""
        try:
            public = self.client.conversations_list(types="public_channel")["channels"]
            private = self.client.conversations_list(types="private_channel")["channels"]
            return {"public": public, "private": private}
        except SlackApiError as e:
            return {"error": e.response["error"]}

    def send_message(self, text: str) -> dict:
        """Test message to verify channel access."""
        try:
            response = self.client.chat_postMessage(channel=self.channel, text=text)
            return {"success": True, "response": response}
        except SlackApiError as e:
            return {"success": False, "error": e.response["error"]}
        
    def send_file(self, text: str, file_path: str) -> dict:
        """Upload and send file to Slack channel with comment."""
        try:
            response = self.client.files_upload_v2(
                channel=self.channel,
                file=file_path,
                initial_comment=text
            )
            return {"success": True, "response": response}
        except SlackApiError as e:
            return {"success": False, "error": e.response["error"]}

    def send_daily_report(self, username: str) -> dict:
        """Wrapper for daily progress report with plot."""
        try:
            # Generate plot (assuming plot_progress exists in analysis.py)
            from utils.analysis import plot_progress
            plot_progress(username)
            
            # Send message with plot
            return self.send_file(
                text=f"Daily progress report for {username}",
                file_path=f"progress_{username}.png"
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

def test_slack_integration():
    """Diagnostic test for Slack connectivity."""
    sm = SlackManager()
    
    # Step 1: List accessible channels
    print("\n[1/3] Checking accessible channels...")
    channels = sm.list_accessible_channels()
    
    if "error" in channels:
        print(f"🚨 Error listing channels: {channels['error']}")
        return

    print("\nPublic Channels:")
    for ch in channels["public"]:
        print(f"  - #{ch['name']} (ID: {ch['id']})")

    print("\nPrivate Channels:")
    for ch in channels["private"]:
        print(f"  - {ch['name']} (ID: {ch['id']})")

    # Step 2: Verify target channel exists
    print(f"\n[2/3] Looking for target channel: {sm.channel}")
    all_channels = channels["public"] + channels["private"]
    target = next((ch for ch in all_channels if ch["name"] == sm.channel), None)
    
    if not target:
        print(f"🚨 Channel {sm.channel} not found in accessible channels!")
        print("Possible fixes:")
        print("1. Invite the bot to the channel with `/invite @YourBotName`")
        print("2. Use a channel ID instead of name in .env")
        return

    print(f"✅ Channel found: {target['name']} (ID: {target['id']})")

    # Step 3: Test message sending
    print(f"\n[3/3] Sending test message to {target['name']}...")
    result = sm.send_message("🚀 Slack connectivity test!")
    
    if result["success"]:
        print("✅ Test message sent successfully!")
    else:
        print(f"🚨 Failed to send message: {result['error']}")
        print("Possible fixes:")
        print("1. Reinstall the Slack app with correct scopes")
        print("2. Check OAuth scopes: chat:write, channels:read, groups:read")

if __name__ == "__main__":
    test_slack_integration()