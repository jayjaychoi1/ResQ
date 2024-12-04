//
//  fetchMessagesFromServer.swift
//  resq_ios
//
//  Created by JJ Choi on 12/3/24.
//

import Foundation

class MessageFetcher {
    static let shared = MessageFetcher()
    
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
}
