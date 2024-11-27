import SwiftUI
import AVFoundation
import UIKit
import TwilioVoice

struct ContentView: View {
    @StateObject private var callViewModel = CallViewModel()
    
    @State private var isRecording = false
    @State private var callID: Int?
    @State private var buttonText = "Call 119"
    @State private var gradientIntensity: Double = 0.35 // Initial gradient intensity
    @State private var isCalling = false
    @State private var isCallEnded = false
    @State private var timer: Timer?

    // Initialize the audio recorder
    private let audioRecorder = AudioRecorder()

    var body: some View {
        VStack(spacing: 100) {
            // App title
            Text("ResQ")
                .font(.system(size: 64, weight: .bold, design: .rounded))
                .foregroundColor(.red) // Red for urgency
                .shadow(color: .black.opacity(0.2), radius: 5, x: 0, y: 5)
                .padding()

            // Call button
            Button(action: {
                toggleEmergencyCall()
            }) {
                Text(buttonText)
                    .font(.title)
                    .frame(width: 350, height: 350)
                    .foregroundColor(.white)
                    .background(
                        Circle()
                            .fill(
                                RadialGradient(
                                    gradient: Gradient(colors: isCallEnded ? [Color.green.opacity(gradientIntensity), Color.green] : [Color.red.opacity(gradientIntensity), Color.red]),
                                    center: .center,
                                    startRadius: 0,
                                    endRadius: 200
                                )
                            )
                    )
            }

            // Yes/No buttons
            HStack(spacing: 30) {
                Button(action: {
                    sendResponse("yes")
                }) {
                    Text("Yes")
                        .font(.title)
                        .frame(width: 150, height: 79)
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(15)
                }

                Button(action: {
                    sendResponse("no")
                }) {
                    Text("No")
                        .font(.title)
                        .frame(width: 150, height: 79)
                        .background(Color.orange)
                        .foregroundColor(.white)
                        .cornerRadius(15)
                }
            }
            .padding(.top, 40)
        }
        .padding()
        .onAppear {
            setupAudioSession()
        }
    }

    // Toggle emergency call and mic recording
    func toggleEmergencyCall() {
        if isCalling {
            stopEmergencyCall()
        } else {
            startEmergencyCall()
        }
    }

    // Start emergency call and mic monitoring
    func startEmergencyCall() {
        buttonText = "Calling 119"
        isCalling = true
        isCallEnded = false
        startListening()
        audioRecorder.startRecording() // Start recording audio

        // Twilio call logic here
        
        fetchAccessToken() // Currently has error so that when app laucnhes the token is being fetched
        
        NetworkManager.shared.startEmergencyCall { result in
            switch result {
            case .success(let response):
                print("Emergency call started: \(response)")
            case .failure(let error):
                print("Failed to start emergency call: \(error)")
            }
        }
    }

    // Stop emergency call and mic monitoring
    func stopEmergencyCall() {
        buttonText = "Call Ended"
        isCalling = false
        isCallEnded = true
        stopListening()
        isCalling = false
        callViewModel.hangUpCall()
        audioRecorder.stopRecording() // Stop recording audio
    }

    func startListening() {
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
            if self.isCalling {
                // Update gradient intensity
                self.gradientIntensity = Double.random(in: 0.3...1.0)
            }
        }
    }

    func stopListening() {
        timer?.invalidate()
        timer = nil
        gradientIntensity = 0.3 // Reset gradient
    }

    func sendResponse(_ response: String) {
        guard let callID = callID else {
            print("Call ID not available")
            return
        }

        NetworkManager.shared.sendYesNoResponse(callID: callID, response: response) { result in
            switch result {
            case .success(let response):
                print("Response sent: \(response)")
            case .failure(let error):
                print("Failed to send response: \(error)")
            }
        }
    }

    func setupAudioSession() {
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker])
            try audioSession.setActive(true)
            print("Audio session is set up and active.")
        } catch {
            print("Failed to set up audio session: \(error)")
        }
    }
    
    func fetchAccessToken() {
        let url = URL(string: "https://5ffd-163-239-255-162.ngrok-free.app/api/get_access_token/")!

        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                print("Failed to fetch token: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    callViewModel.callStatus = "Failed to fetch token"
                }
                return
            }

            guard let data = data,
                  let token = String(data: data, encoding: .utf8) else {
                DispatchQueue.main.async {
                    callViewModel.callStatus = "Invalid token response"
                }
                return
            }

            DispatchQueue.main.async {
                callViewModel.accessToken = token
                callViewModel.callStatus = "Ready to call"
                print("Access token fetched: \(token)")
            }
        }
        task.resume()
    }// End fetchAcessToKen


}
