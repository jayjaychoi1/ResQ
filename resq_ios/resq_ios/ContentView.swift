import Foundation
import AVFoundation
import SwiftUI
import UIKit
import TwilioVoice

struct ChatMessage: Hashable {
    let userId: String // "inbound" for user, "outbound" for operator
    let message: String // The actual message content
    let translated: String // Indicates if the message is translated
}

struct ContentView: View {
    @State private var isRecording = false
    @State private var callID: Int? = 123
    @State private var gradientIntensity: Double = 0.35
    @State private var isCalling = false
    @State private var isCallEnded = false
    @State private var showMessagingArea = false
    @State private var isButtonRectangular = false
    @State private var showCallOptions = false
    @State private var buttonText = "Call 119"
    @State private var callThisNumber = "+821063461851"
    @State private var customNumber: String = ""
    @State private var mostRecent = "119"
    @State private var enteredMessage: String = ""
    @State private var chatMessages: [ChatMessage] = []
    @State private var isLongPressing = false
    @State private var isTapped = false
    
    private let callManager = CallManager()
    private let webSocketManager = WebSocketManager(webSocketURL: "wss://6f86-163-239-255-167.ngrok-free.app/ws/chat/")
    
    var body: some View {
        VStack(spacing: 15) {
            titleView
            Spacer(minLength: 10)
            callButtonView
            Spacer(minLength: 5)
            if showMessagingArea {
                chatroomView
                messageInputView
            }
            yesNoButtonsView
            Spacer()
        }
        .padding()
        .onAppear { setupWebSocket() }
    }
    
    private var titleView: some View {
        Text("ResQ")
            .font(.system(size: 72, weight: .bold, design: .rounded))
            .foregroundColor(.red)
            .shadow(color: .black.opacity(0.2), radius: 5, x: 0, y: 5)
            .padding(.top, 50)
    }
    
    private var callButtonView: some View {
        Group {
            if showCallOptions {
                callOptionsView
            } else {
                callActionButtonView
            }
        }
    }
    
    private var callOptionsView: some View {
        VStack {
            ForEach(["119", "112", "911", "Custom"], id: \.self) { option in
                Button(action: { handleOptionSelection(option: option) }) {
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
    }
    
    private var callActionButtonView: some View {
        Button(action: {
            if isLongPressing { withAnimation { showCallOptions = true } }
            else if isTapped { toggleEmergencyCall() }
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
        .simultaneousGesture(LongPressGesture(minimumDuration: 1).onChanged { _ in isLongPressing = false }.onEnded { _ in isLongPressing = true })
        .highPriorityGesture(TapGesture().onEnded { _ in
            isTapped = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) { isTapped = false }
            toggleEmergencyCall()
        })
    }
    
    /*
    private var chatroomView: some View {
        VStack {
            ScrollView {
                ForEach(chatMessages, id: \.self) { message in
                    chatBubble(for: message)
                }
            }
            .frame(height: 375)
            .border(Color.gray.opacity(0.3), width: 2)
            .cornerRadius(10)
        }
    }
    */
    
    private var chatroomView: some View {
        ScrollViewReader { scrollViewProxy in
            ScrollView {
                ForEach(chatMessages, id: \.self) { message in
                    chatBubble(for: message)
                        .id(message) // Assign a unique ID for each message
                }
            }
            .onChange(of: chatMessages) { _ in
                // Scroll to the most recent message whenever chatMessages changes
                if let lastMessage = chatMessages.last {
                    scrollViewProxy.scrollTo(lastMessage, anchor: .bottom)
                }
            }
            .frame(height: 375) // Adjust height as needed
            .border(Color.gray.opacity(0.3), width: 2) // Added grey border
            .cornerRadius(10) // Optional: adds rounded corners to the border
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
        webSocketManager.disconnect()
        chatMessages.removeAll() //removes all msgs too
    }
    
    private func chatBubble(for message: ChatMessage) -> some View {
        HStack {
            if message.userId == "outbound" {
                operatorMessageBubble(for: message.message)
                Spacer()
            } else if message.userId == "inbound" {
                Spacer()
                userMessageBubble(for: message.message)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 2)
    }
    
    private func operatorMessageBubble(for text: String) -> some View {
        Text(text)
            .padding(7)
            .background(Color.blue.opacity(0.9))
            .cornerRadius(12)
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.blue.opacity(0.6), lineWidth: 1))
            .foregroundColor(.white)
            .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: .leading)
    }
    
    private func userMessageBubble(for text: String) -> some View {
        Text(text)
            .padding(7)
            .background(Color.green.opacity(0.9))
            .cornerRadius(12)
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.green.opacity(0.6), lineWidth: 1))
            .foregroundColor(.white)
            .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: .trailing)
    }
    
    private var messageInputView: some View {
        HStack {
            TextField("Enter message...", text: $enteredMessage)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
                .onSubmit { sendMessage() }
            Button(action: { sendMessage() }) {
                Image(systemName: "arrow.up.circle.fill")
                    .resizable()
                    .frame(width: 36, height: 36)
                    .foregroundColor(.blue)
            }
            .padding(.trailing)
        }
        .padding(.bottom)
    }
    
    private var yesNoButtonsView: some View {
        HStack(spacing: 25) {
            Button(action: { sendResponse("yes") }) {
                Text("Yes")
                    .font(.title)
                    .frame(width: 150, height: 79)
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(15)
            }
            Button(action: { sendResponse("no") }) {
                Text("No")
                    .font(.title)
                    .frame(width: 150, height: 79)
                    .background(Color.orange)
                    .foregroundColor(.white)
                    .cornerRadius(15)
            }
        }
        .padding(.bottom, 30)
    }
    
    private func setupWebSocket() {
        webSocketManager.onMessageReceived = { message, userID in
            DispatchQueue.main.async {
                let chatMessage = ChatMessage(userId: userID, message: message, translated: "yes")
                chatMessages.append(chatMessage)
            }
        }
        webSocketManager.connect()
    }
    
    private func sendMessage() {
        guard !enteredMessage.isEmpty else { return }
        chatMessages.append(ChatMessage(userId: "inbound", message: enteredMessage, translated: "yes"))
        webSocketManager.sendMessage(enteredMessage, userID: "inbound")
        enteredMessage = ""
    }
    
    /*
    private func sendResponse(_ response: String) {
        guard let callID = callID else { return }
        // Customnetwork response logic
    }
     */
    
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
        
}
