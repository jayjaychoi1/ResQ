import SwiftUI

struct ContentView: View {
    @State private var isRecording = false
    @State private var callID: Int?

    var body: some View {
        VStack(spacing: 100) {
            Text("ResQ")
                .font(.largeTitle)
                .padding()

            // Call 911/119 Button
            Button(action: {
                startEmergencyCall()
            }) {
                Text("Call 119")
                    .font(.title)
                    .frame(width: 300, height: 140)
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(15)
            }

            // Yes/No Buttons
            HStack(spacing: 40) {
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
    }

    // Function to start an emergency call
    func startEmergencyCall() {
        NetworkManager.shared.startEmergencyCall { result in
            switch result {
            case .success(let response):
                print("Emergency call started: \(response)")
                // Parse callID from response if needed
                // Example: self.callID = extractedCallID
            case .failure(let error):
                print("Failed to start emergency call: \(error)")
            }
        }
    }

    // Function to send Yes/No response
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
}

