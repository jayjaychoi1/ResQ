import Foundation
import AVFoundation
import SwiftUI
import UIKit
import TwilioVoice

struct ContentView: View {
    @State private var isRecording = false
    @State private var callID: Int? = 123 // Example Call ID (replace with actual logic)
    
    @State private var gradientIntensity: Double = 0.35
    @State private var isCalling = false
    @State private var isCallEnded = false
    @State private var timer: Timer?
    
    @State private var showMessagingArea = false // Chat area toggle
    @State private var isButtonRectangular = false // Button shape tracker
    @State private var showCallOptions = false // Dropdown list toggle
    @State private var buttonText = "Call 119" // Button text
    @State private var callThisNumber = "+821063461851" // Default endpoint
    @State private var customNumber: String = "" // Custom number input
    
    @State private var mostRecent = "119"
    
    @State private var enteredMessage: String = "" // For user input in the chat field
    @State private var chatMessages: [String] = [] // Stores messages for chat
    
    private let callManager = CallManager()
    private let networkManager = NetworkManager()
    
    @State private var isLongPressing = false // Track long press gesture
    @State private var isTapped = false // Track tap gesture
    
    var body: some View {
        VStack(spacing: 15) {
            // Title
            Text("ResQ")
                .font(.system(size: 72, weight: .bold, design: .rounded))
                .foregroundColor(.red)
                .shadow(color: .black.opacity(0.2), radius: 5, x: 0, y: 5)
                .padding(.top, 50)
            
            Spacer(minLength: 10)
            
            // Call Button or Dropdown
            if showCallOptions {
                VStack {
                    ForEach(["119", "112", "911", "Custom"], id: \.self) { option in
                        Button(action: {
                            handleOptionSelection(option: option)
                        }) {
                            HStack {
                                Text(option == "Custom" ? "Add Custom Number" : "Call \(option)")
                                    .font(.title3)
                                    .padding()
                                Spacer()
                            }
                            .frame(maxWidth: .infinity)
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(10)
                            .padding(.horizontal)
                        }
                    }
                    if customNumber != "" {
                        Text("Custom Number: \(customNumber)")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
                .transition(.move(edge: .top).combined(with: .opacity))
            } else {
                Button(action: {
                    if isLongPressing {
                        withAnimation {
                            showCallOptions = true
                        }
                    } else if isTapped {
                        toggleEmergencyCall()
                    }
                }) {
                    Text(buttonText)
                        .font(.title)
                        .frame(width: isButtonRectangular ? 366 : 350, height: isButtonRectangular ? 50 : 350)
                        .foregroundColor(.white)
                        .background(
                            RoundedRectangle(cornerRadius: isButtonRectangular ? 45 : 250)
                                .fill(
                                    RadialGradient(
                                        gradient: Gradient(colors: isCallEnded ? [Color.green.opacity(gradientIntensity), Color.green] : [Color.red.opacity(gradientIntensity), Color.red]),
                                        center: .center,
                                        startRadius: 0,
                                        endRadius: isButtonRectangular ? 100 : 200
                                    )
                                )
                        )
                }
                .simultaneousGesture(
                    LongPressGesture(minimumDuration: 1)
                        .onChanged { _ in
                            isLongPressing = false
                        }
                        .onEnded { _ in
                            isLongPressing = true
                        }
                )
                .highPriorityGesture(
                    TapGesture()
                        .onEnded { _ in
                            isTapped = true
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                                isTapped = false
                            }
                            toggleEmergencyCall()  // Trigger the call when tapped
                        }
                )
            }
            
            Spacer(minLength: 5)
            
            // Chatroom Placeholder (Always show when call is initiated)
            if showMessagingArea {
                VStack {
                    //display the "Help is coming!" message without extra padding
                    //add or nah
                    Text("Help is coming!")
                        .italic()
                        .foregroundColor(.gray)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .offset(x: 5, y: 5)
                    
                    // Chat messages section
                    ScrollView {
                        ForEach(chatMessages, id: \.self) { message in
                            HStack {
                                // If the message starts with "You:", align it to the right
                                if message.starts(with: "You:") {
                                    Spacer() // Push user's message to the right
                                    Text(message.replacingOccurrences(of: "You: ", with: "")) // Remove "You:" from message
                                        .padding(3)
                                        .background(Color.green.opacity(0.9))
                                        .cornerRadius(12)
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 12)
                                                .stroke(Color.green.opacity(0.6), lineWidth: 1)
                                        )
                                        .foregroundColor(.white)
                                        .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: .trailing)
                                } else {
                                    // If it's not from the user (assumed to be the operator), align it to the left
                                    Text(message)
                                        .padding(3)
                                        .background(Color.blue.opacity(0.9))
                                        .cornerRadius(12)
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 12)
                                                .stroke(Color.blue.opacity(0.6), lineWidth: 1)
                                        )
                                        .foregroundColor(.white)
                                        .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: .leading)
                                    Spacer() // Push operator's message to the left
                                }
                            }
                            .padding(.horizontal)
                            .padding(.vertical, 2) // Add spacing between messages
                        }
                    }
                    .frame(height: 400) // Adjust height as needed
                    .border(Color.gray, width: 1) // Border for the entire chatroom (including "Help is coming!")
                    
                    HStack {
                        TextField("Enter message...", text: $enteredMessage)  // Binding the input field
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .padding(.horizontal)
                        
                        Button(action: {
                            sendMessage()  // Send the message when button is clicked
                        }) {
                            Image(systemName: "arrow.up.circle.fill")
                                .resizable()
                                .frame(width: 36, height: 36)
                                .foregroundColor(.blue)
                        }
                        .padding(.trailing)
                    }
                    .padding(.bottom)
                }
                .border(Color.gray, width: 1)
            }
            
            // Yes & No Buttons
            HStack(spacing: 25) {
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
            .padding(.bottom, 30)
            
            Spacer()
        }
        .padding()
        .onAppear {
            // Timer to fetch messages periodically
            Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { _ in
                fetchMessages()
            }
            //showMessagingArea = true
        }
    }
    
    // Toggle Call (Tap Gesture)
    func toggleEmergencyCall() {
        if isCalling {
            stopEmergencyCall()
        } else {
            startEmergencyCall()
        }
    }
    
    func startEmergencyCall() {
        buttonText = "Calling \(buttonText.split(separator: " ").last ?? "119")"
        isCalling = true
        isCallEnded = false
        
        // Show messaging area when call starts
        withAnimation {
            showMessagingArea = true
        }
        
        // Make the button rectangular after the call is initiated
        withAnimation {
            isButtonRectangular = true
        }
        
        initiateEmergencyCall()
    }
    
    func initiateEmergencyCall() {
        buttonText = "Calling " + mostRecent
        TokenService.fetchAccessToken { accessToken in
            guard let accessToken = accessToken else {
                callManager.callStatus = "Failed to fetch token"
                return
            }
            DispatchQueue.main.async {
                callManager.makeCall(to: callThisNumber, accessToken: accessToken)
            }
        }
    }
    
    func stopEmergencyCall() {
        buttonText = "Call Ended"
        isCalling = false
        isCallEnded = true
        
        // Hide messaging area when call ends
        withAnimation {
            showMessagingArea = false
            isButtonRectangular = false // Reset the button to circular
        }
        callManager.hangUp()
        chatMessages.removeAll() //removes all msgs too
    }
    
    func handleOptionSelection(option: String) {
        if option == "Custom" {
            setCustomNumber()
        } else {
            switch option {
            case "119":
                mostRecent = "119"
                callThisNumber = "+821063461851"
            case "112":
                mostRecent = "112"
                callThisNumber = "+821076223417"
            case "911":
                mostRecent = "911"
                callThisNumber = "+821073877475"
            default:
                break
            }
            buttonText = "Call \(option)"
        }
        
        isCalling = false
        isCallEnded = false
        
        // Hide dropdown list
        withAnimation {
            showCallOptions = false
        }
    }
    
    func setCustomNumber() {
        let alert = UIAlertController(title: "Enter Custom Number", message: nil, preferredStyle: .alert)
        alert.addTextField { textField in
            textField.placeholder = "Enter phone number"
            textField.keyboardType = .numberPad // Set the numpad keyboard
        }
        
        let submitAction = UIAlertAction(title: "OK", style: .default) { _ in
            if let inputNumber = alert.textFields?.first?.text, !inputNumber.isEmpty {
                // Update values with the custom number
                customNumber = inputNumber
                buttonText = "Calling \(customNumber)"
                mostRecent = customNumber
                callThisNumber = customNumber
            }
        }
        
        let cancelAction = UIAlertAction(title: "Cancel", style: .cancel, handler: nil)
        
        alert.addAction(submitAction)
        alert.addAction(cancelAction)
        
        // Present the alert (You may need to use the top-most view controller for this)
        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let rootVC = windowScene.windows.first?.rootViewController {
            rootVC.present(alert, animated: true, completion: nil)
        }
    }

    
    func sendMessage() {
        guard !enteredMessage.isEmpty else { return }
        
        // Append the message to the chat
        chatMessages.append("You: \(enteredMessage)")
        enteredMessage = "" // Clear the input field
        
        // Send the message to the backend or display it
        print("Sent message: \(chatMessages.last ?? "")")
    }
    
    func sendResponse(_ response: String) {
        guard let callID = callID else {
            print("Call ID not available")
            return
        }
        
        NetworkManager.shared.sendYesNoResponse(callID: callID, response: response) { result in
            switch result {
            case .success:
                print("Response sent: \(response)")
            case .failure(let error):
                print("Failed to send response: \(error)")
            }
        }
    }
    
    func fetchMessages() {
        guard let callID = callID else { return }
        
        MessageFetcher.shared.fetchMessages(for: callID) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let messages):
                    self.chatMessages = messages // Update chat messages
                case .failure(let error):
                    print("Failed to fetch messages: \(error)")
                }
            }
        }
    }
}
