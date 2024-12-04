import Foundation

class MessageSender {
    static let shared = MessageSender()
    
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
