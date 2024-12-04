import Foundation
import AVFoundation
import SwiftUI
import UIKit
import TwilioVoice

struct ContentView: View {
    @State private var isRecording = false
    @State private var callID: Int?
    
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

                /*
                .highPriorityGesture(
                    TapGesture()
                        .onEnded { _ in
                            if isLongPressing {  // Ensure tap only works if long press is not active
                                isTapped = true
                                DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                                    isTapped = false
                                }
                                toggleEmergencyCall()  // Trigger the call when tapped
                            }
                        }
                )//end if hPG
                 */
            }
            
            Spacer(minLength: 5)
            
            // Chatroom Placeholder (Always show when call is initiated)
            if showMessagingArea {
                VStack {
                    ScrollView {
                        Text("Help is coming!")
                            .italic()
                            .foregroundColor(.gray)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(EdgeInsets(top: 20, leading: 10, bottom: 20, trailing: 10))
                    }
                    .frame(height: 400)
                    .border(Color.gray, width: 1)
                    
                    HStack {
                        TextField("Enter message...", text: .constant(""))
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .padding(.horizontal)
                        
                        Button(action: {
                            print("Message sent!")
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
        }
        .padding()
        .onAppear {
            // Setup or additional configurations
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
    }
    
    
    // Handle Option Selection (Dropdown List)
    func handleOptionSelection(option: String) {
        if option == "Custom" {
            // Show input dialog for custom number
            customNumber = "+821012345678" // Example; prompt for user input
            callThisNumber = customNumber
            buttonText = customNumber // Update the button text
        } else {
            // Update the callThisNumber and button text based on selected option
            switch option {
            case "119":
                callThisNumber = "+821063461851"
            case "112":
                callThisNumber = "+821076223417"
            case "911":
                callThisNumber = "+821073877475"
            default:
                break
            }
            buttonText = "Call \(option)"
        }
        
        isCalling = false
        isCallEnded = false
        
        //Hide dropdown list
        withAnimation {
            showCallOptions = false
        }
    }
    
    // Send Yes or No Response
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
    }//end of sendResponse
}
