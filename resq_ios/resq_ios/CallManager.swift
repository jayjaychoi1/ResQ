//
//  CallManager.swift
//  resq_ios
//
//  Created by JJ Choi on 11/29/24.
//

import TwilioVoice
import Foundation

class CallManager: NSObject, ObservableObject {
    @Published var callStatus: String = "Ready"  // Using @Published to automatically notify ContentView
    
    private var call: Call?

    // To Call
    func makeCall(to number: String, accessToken: String) {
        let connectOptions = ConnectOptions(accessToken: accessToken) { builder in
            builder.params = ["To": number]
            //builder.edge = "tokyo"
        }

        //TwilioVoiceSDK.audioDevice = DefaultAudioDevice()
        // Initiating the call via Twilio Voice SDK
        call = TwilioVoiceSDK.connect(options: connectOptions, delegate: self)
        DispatchQueue.main.async {
            self.callStatus = "Connecting..."
        }
    }

    // To Hang Up
    func hangUp() {
        call?.disconnect()
        call = nil
        DispatchQueue.main.async {
            self.callStatus = "Call ended"
        }
    }
}

extension CallManager: CallDelegate {
    // Called when the call successfully connects
    func callDidConnect(call: Call) {
        print("Call connected")
        DispatchQueue.main.async {
            self.callStatus = "Call in Progress"
        }
    }

    // Called when the call disconnects (either by you or the callee)
    func callDidDisconnect(call: Call, error: Error?) {
        print("Call disconnected: \(error?.localizedDescription ?? "No error")")
        
        // Handle call disconnect by callee or error
        DispatchQueue.main.async {
            if let error = error {
                // If there's an error, log it
                self.callStatus = "Call ended with error: \(error.localizedDescription)"
            } else {
                // Call ended successfully
                self.callStatus = "Call ended"
            }
        }

        self.call = nil
    }

    // Called when the call fails to connect
    func callDidFailToConnect(call: Call, error: Error) {
        print("Failed to connect: \(error.localizedDescription)")
        DispatchQueue.main.async {
            self.callStatus = "Failed to connect"
        }
        self.call = nil
    }
}
