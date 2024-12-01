//
//  CallManager.swift
//  resq_ios
//
//  Created by JJ Choi on 11/29/24.
//

import TwilioVoice
import Foundation

class CallManager: NSObject {
    private var call: Call?
    var callStatus: String = "Ready"

    // Calls made by this hamsu
    func makeCall(to number: String, accessToken: String) {
        let connectOptions = ConnectOptions(accessToken: accessToken) { builder in
            builder.params = ["To": number]
        }

        call = TwilioVoiceSDK.connect(options: connectOptions, delegate: self)
        callStatus = "Connecting..."
    }

    func hangUp() {
        call?.disconnect()
        call = nil
        callStatus = "Call ended"
    }
}

extension CallManager: CallDelegate {
    func callDidConnect(call: Call) {
        print("Call connected")
    }

    func callDidDisconnect(call: Call, error: Error?) {
        print("Call disconnected: \(error?.localizedDescription ?? "No error")")
        self.call = nil
    }

    func callDidFailToConnect(call: Call, error: Error) {
        print("Failed to connect: \(error.localizedDescription)")
        self.call = nil
    }
}
