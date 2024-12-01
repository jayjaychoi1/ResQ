import SwiftUI
import AVFoundation
import UIKit
import TwilioVoice

struct ContentView: View {
    @State private var isRecording = false
    @State private var callID: Int?
    @State private var buttonText = "Call 119"
    @State private var gradientIntensity: Double = 0.35 // Initial gradient intensity
    @State private var isCalling = false
    @State private var isCallEnded = false
    @State private var timer: Timer?
    
    // 전화 걸기 위해서
    private let callManager = CallManager()
    
    //do i need this?
    private let networkManger = NetworkManager()
    
    
    @State private var accessToken: String?
    @State private var callStatus = "Ready"
    
    // Initialize the audio recorder
    //private let audioRecorder = AudioRecorder()
    
    var body: some View {
        VStack(spacing: 100) {
            // Button name
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
            
            // Yes & No buttons
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
    
    // Toggle Call
    func toggleEmergencyCall() {
        if isCalling {
            stopEmergencyCall() // STOP
        } else {
            startEmergencyCall() // START
        }
    }
    
    func startEmergencyCall() {
        buttonText = "Calling 119"
        isCalling = true
        isCallEnded = false
        
        // For pretties
        startListening()
        
        // For recording
        //audioRecorder.startRecording()
        
        // Fetch and call
        initiateEmergencyCall()
    }
    
    //PART 1
    func initiateEmergencyCall() {
        TokenService.fetchAccessToken { accessToken in
            guard let accessToken = accessToken else {
                callManager.callStatus = "Failed to fetch token"
                return
            }
            
            DispatchQueue.main.async {
                callManager.makeCall(to: "+821063461851", accessToken: accessToken)
                
                NetworkManager.shared.startEmergencyCall { result in
                    switch result {
                    case .success(let response):
                        print("Emergency call started: \(response)")
                    case .failure(let error):
                        print("Failed to start emergency call: \(error)")
                    }//end result
                }
            }
        }
    }//end init call
    

    func stopEmergencyCall() {
        buttonText = "Call Ended"
        isCalling = false
        isCallEnded = true

        // Stop gradient and microphone recording
        stopListening()
        //audioRecorder.stopRecording()

        // End Twilio call
        callManager.hangUp()
    }

    func startListening() {
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
            if self.isCalling {
                // Gradient Intensity
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

}//end of content view
