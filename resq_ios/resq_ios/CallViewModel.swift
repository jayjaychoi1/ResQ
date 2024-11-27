//
//  CallViewModel.swift
//  resq_ios
//
//  Created by JJ Choi on 11/27/24.
//

import TwilioVoice
import SwiftUI

class CallViewModel: NSObject, ObservableObject {
    @Published var callStatus: String = "Ready" // Updates UI with call status
    
    public var accessToken: String?
    
    
    private var call: Call?
    

    override init() {
        super.init()
        fetchAccessToken()
    }

    func fetchAccessToken() {
        let url = URL(string: "https://5616-163-239-255-174.ngrok-free.app/get_access_token/")!
        let task = URLSession.shared.dataTask(with: url) { data, _, error in
            if let error = error {
                print("Failed to fetch token: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    self.callStatus = "Failed to fetch token"
                }
                return
            }

            guard let data = data, let token = String(data: data, encoding: .utf8) else {
                DispatchQueue.main.async {
                    self.callStatus = "Invalid token response"
                }
                return
            }

            DispatchQueue.main.async {
                self.accessToken = token
                self.callStatus = "Ready to call"
            }
        }
        task.resume()
    }

    func makeCall(to number: String) {
        guard let accessToken = accessToken else {
            callStatus = "Token not available"
            return
        }

        let connectOptions = ConnectOptions(accessToken: accessToken) { builder in
            builder.params = ["To": number]
        }

        call = TwilioVoiceSDK.connect(options: connectOptions, delegate: self)
        callStatus = "Connecting..."
    }

    func hangUpCall() {
        call?.disconnect()
        callStatus = "Call ended"
        call = nil
    }
}

// MARK: - CallDelegate
extension CallViewModel: CallDelegate {
    func callDidConnect(call: Call) {
        DispatchQueue.main.async {
            self.callStatus = "Call connected"
        }
    }

    func callDidDisconnect(call: Call, error: Error?) {
        DispatchQueue.main.async {
            self.callStatus = error == nil ? "Call ended" : "Error: \(error!.localizedDescription)"
        }
        self.call = nil
    }

    func callDidFailToConnect(call: Call, error: Error) {
        DispatchQueue.main.async {
            self.callStatus = "Failed to connect: \(error.localizedDescription)"
        }
        self.call = nil
    }
}

