//
//  TokenService.swift
//  resq_ios
//
//  Created by JJ Choi on 11/29/24.
//

import Foundation

class TokenService {
    static func fetchAccessToken(completion: @escaping (String?) -> Void) {
        // Ensure the URL is valid
        guard let url = URL(string: "https://6fab-119-192-238-169.ngrok-free.app/twilio/") else {
            print("Error: Invalid URL")
            completion(nil)
            return
        }

        // Create the GET request
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            // Handle networking errors
            if let error = error {
                print("Error fetching token: \(error.localizedDescription)")
                completion(nil)
                return
            }

            // Validate the HTTP response
            if let httpResponse = response as? HTTPURLResponse {
                print("HTTP Status Code: \(httpResponse.statusCode)")
                if httpResponse.statusCode != 200 {
                    print("Error: Server returned status code \(httpResponse.statusCode)")
                    completion(nil)
                    return
                }
            }

            // Ensure we received data
            guard let data = data, !data.isEmpty else {
                print("No data received or data is empty")
                completion(nil)
                return
            }

            // Decode JSON data
            do {
                if let jsonObject = try? JSONSerialization.jsonObject(with: data, options: []),
                   let jsonDict = jsonObject as? [String: Any],
                   let token = jsonDict["access_token"] as? String {
                    print("Access token fetched: \(token)")
                    completion(token)
                } else {
                    print("Failed to decode token from response data")
                    completion(nil)
                }
            }
        }

        task.resume()
    }
}
