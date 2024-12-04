//
//  sendMessageToServer.swift
//  resq_ios
//
//  Created by JJ Choi on 12/3/24.
//

/*
func sendMessageToServer(message: String) {
    //TO WHERE
    guard let url = URL(string: "") else {
        print("Invalid URL")
        return
    }
    let body: [String: Any] = ["message": message]

    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.addValue("application/json", forHTTPHeaderField: "Content-Type")

    // Convert body dictionary to JSON
    do {
        let jsonData = try JSONSerialization.data(withJSONObject: body, options: [])
        request.httpBody = jsonData
    } catch {
        print("Error serializing JSON: \(error)")
        return
    }

    // Perform the network request
    URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            print("Error sending message: \(error.localizedDescription)")
            return
        }

        // Handle the response if needed
        if let data = data, let response = try? JSONDecoder().decode(ServerResponse.self, from: data) {
            print("Server Response: \(response)")
        } else {
            print("Error decoding response or no data received")
        }
    }.resume()
}
*/
