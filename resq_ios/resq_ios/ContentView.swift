import SwiftUI
import AVFoundation

struct ContentView: View {
    @State private var isRecording = false
    @State private var callID: Int?
    @State private var buttonText = "Call 119"
    @State private var gradientIntensity: Double = 0.3 // Initial intensity value
    @State private var isCalling = false
    @State private var isCallEnded = false // New state for tracking if the call has ended
    @State private var timer: Timer?

    var body: some View {
        VStack(spacing: 100) {
            Text("ResQ")
                .font(.largeTitle)
                .padding()

            Button(action: {
                toggleEmergencyCall()
            }) {
                Text(buttonText)
                    .font(.title)
                    .frame(width: 400, height: 400)
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

    //Toggle emergency call and mic recording
    func toggleEmergencyCall() {
        if isCalling {
            stopEmergencyCall()
        } else {
            startEmergencyCall()
        }
    }

    //Start emergency call and mic monitoring
    func startEmergencyCall() {
        buttonText = "Calling 119"
        isCalling = true
        isCallEnded = false
        startListening() //Begin monitoring microphone volume
        
        NetworkManager.shared.startEmergencyCall { result in
            switch result {
            case .success(let response):
                print("Emergency call started: \(response)")
            case .failure(let error):
                print("Failed to start emergency call: \(error)")
            }
        }
    }

    //Stop emergency call and mic monitoring
    func stopEmergencyCall() {
        buttonText = "Call Ended"
        isCalling = false
        isCallEnded = true
        stopListening()
    }

    func startListening() {
        timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
            if self.isCalling {
                // Increase the range slightly to make the gradient stronger
                self.gradientIntensity = Double.random(in: 0.3...1.0) // Adjusted range
            }
        }
    }
    
    func stopListening() {
        timer?.invalidate()
        timer = nil // Ensure timer is set to nil to stop the instance
        gradientIntensity = 0.3 // Reset gradient to default intensity for initial color
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
        // Use AVAudioSession
    }
}
