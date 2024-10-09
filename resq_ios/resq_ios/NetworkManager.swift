//
//  NetworkManager.swift
//  resq_ios
//
//  Created by soule n on 10/9/24.
//

import Foundation

class NetworkManager {
    static let shared = NetworkManager()
    private let baseURL = "http://127.0.0.1:8000"

    // Function to start an emergency call
    func startEmergencyCall(completion: @escaping (Result<String, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/start_call/") else {
            completion(.failure(NSError(domain: "Invalid URL", code: 1, userInfo: nil)))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = ["location": "User's location"]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            if let data = data, let responseString = String(data: data, encoding: .utf8) {
                completion(.success(responseString))
            } else {
                completion(.failure(NSError(domain: "No data received", code: 2, userInfo: nil)))
            }
        }.resume()
    }

    // Function to send yes/no response
    func sendYesNoResponse(callID: Int, response: String, completion: @escaping (Result<String, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/yes_no_response/\(callID)/") else {
            completion(.failure(NSError(domain: "Invalid URL", code: 1, userInfo: nil)))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = ["response": response]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            if let data = data, let responseString = String(data: data, encoding: .utf8) {
                completion(.success(responseString))
            } else {
                completion(.failure(NSError(domain: "No data received", code: 2, userInfo: nil)))
            }
        }.resume()
    }
}
