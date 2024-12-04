//
//  MessageServer.swift
//  resq_ios
//
//  Created by JJ Choi on 11/1/24.
//

import Foundation

class MessageServer {
    static let shared = MessageServer()
    
    private init() {} // Prevent instantiation
    
    //Fetch Messages
    func fetchMessages(for callID: Int, completion: @escaping (Result<[String], Error>) -> Void) {
        let url = URL(string: "https://your-api-endpoint.com/getMessages?callID=\(callID)")!
        
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No Data", code: 0, userInfo: nil)))
                return
            }
            
            do {
                let messages = try JSONDecoder().decode([String].self, from: data)
                completion(.success(messages))
            } catch {
                completion(.failure(error))
            }
        }
        
        task.resume()
    }
    
    //Send Messages
    func sendMessage(to callID: Int, message: String, completion: @escaping (Result<String, Error>) -> Void) {
        let url = URL(string: "https://your-api-endpoint.com/sendMessage")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "callID": callID,
            "message": message
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])
        } catch {
            completion(.failure(error))
            return
        }
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data, let responseString = String(data: data, encoding: .utf8) else {
                completion(.failure(NSError(domain: "Invalid Response", code: 0, userInfo: nil)))
                return
            }
            
            completion(.success(responseString))
        }
        
        task.resume()
    }
}
