//
//  WebSocketManager.swift
//  resq_ios
//
//  Created by JJ Choi on 11/5/24.
//

import Foundation

/// A manager to handle WebSocket connections for real-time messaging.
class WebSocketManager: NSObject {
    private var webSocketTask: URLSessionWebSocketTask?
    private let webSocketURL: URL
    private let session: URLSession

    /// Callbacks for event handling
    var onMessageReceived: ((String, String) -> Void)? // Parameters: (message, user_id)
    var onError: ((Error) -> Void)?
    var onConnectionStatusChange: ((Bool) -> Void)? // True: Connected, False: Disconnected

    private var isConnected = false

    /// Initialize with the WebSocket URL.
    init(webSocketURL: String) {
        guard let url = URL(string: webSocketURL) else {
            fatalError("Invalid WebSocket URL")
        }
        self.webSocketURL = url
        self.session = URLSession(configuration: .default)
        super.init()
    }

    /// Connect to the WebSocket server.
    func connect() {
        webSocketTask = session.webSocketTask(with: webSocketURL)
        webSocketTask?.resume()

        // Notify about the connection attempt
        onConnectionStatusChange?(true)
        isConnected = true

        listenForMessages() // Start listening for incoming messages
    }

    /// Disconnect from the WebSocket server.
    func disconnect() {
        webSocketTask?.cancel(with: .normalClosure, reason: nil)
        isConnected = false
        onConnectionStatusChange?(false)
    }

    /// Send a message to the WebSocket server.
    /// - Parameters:
    ///   - message: The message to send.
    ///   - userID: Either "inbound" or "outbound".
    func sendMessage(_ message: String, userID: String) {
        guard isConnected else {
            print("WebSocket is not connected. Message not sent.")
            return
        }

        // Define the mediatype for this message
        let media_type = "text"  // Assuming this is a text message

        // Format the message as JSON with additional 'text' field
        let messageData: [String: String] = [
            "message": message,
            "user_id": userID,
            "text": media_type  // Add the 'text' field
        ]

        do {
            let jsonData = try JSONSerialization.data(withJSONObject: messageData, options: [])
            let messageString = String(data: jsonData, encoding: .utf8)
            let wsMessage = URLSessionWebSocketTask.Message.string(messageString ?? "")
            webSocketTask?.send(wsMessage) { error in
                if let error = error {
                    self.onError?(error)
                    print("Failed to send message: \(error.localizedDescription)")
                }
            }
        } catch {
            onError?(error)
            print("Failed to encode message: \(error.localizedDescription)")
        }
    }

    /// Listen for incoming messages.
    private func listenForMessages() {
        webSocketTask?.receive { [weak self] result in
            guard let self = self else { return }

            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    print(message)
                    
                    self.handleIncomingMessage(text)
                case .data(let data):
                    print("Received unexpected binary data: \(data)")
                @unknown default:
                    print("Received unknown message type.")
                }
            case .failure(let error):
                self.onError?(error)
                self.isConnected = false
                self.onConnectionStatusChange?(false)
                print("Error receiving message: \(error.localizedDescription)")
            }

            // Continue listening for messages if still connected
            if self.isConnected {
                self.listenForMessages()
            }
        }
    }

    /// Handle incoming messages.
    /// - Parameter message: The raw message received as a string.
    private func handleIncomingMessage(_ message: String) {
        guard let data = message.data(using: .utf8) else {
            print("Failed to convert message to Data.")
            return
        }

        do {
            if let messageData = try JSONSerialization.jsonObject(with: data, options: []) as? [String: String],
               let userID = messageData["user_id"],
               let chatMessage = messageData["message"],
               let translated = messageData["translated"]  {//(translated == "yes")
                       onMessageReceived?(chatMessage, userID)
                   } else {
                       
                       print("Invalid or unfiltered message received.")
                   }
        } catch {
            onError?(error)
            print("Failed to decode incoming message: \(error.localizedDescription)")
        }
    }

    /// Reconnect to the WebSocket server in case of an unexpected disconnection.
    func reconnect() {
        disconnect()
        DispatchQueue.global().asyncAfter(deadline: .now() + 2) { [weak self] in
            self?.connect()
        }
    }
}
