//
//  fetchMessagesFromServer.swift
//  resq_ios
//
//  Created by JJ Choi on 12/3/24.
//

/*
func fetchMessagesFromServer() {
    //TO WHER AGAIN
    guard let url = URL(string: "https:TO WHERE SMART BRO") else {
        print("Invalid URL")
        return
    }

    // Perform the network request to fetch messages
    URLSession.shared.dataTask(with: url) { data, response, error in
        if let error = error {
            print("Error fetching messages: \(error.localizedDescription)")
            return
        }

        // Handle the response if needed
        if let data = data, let messages = try? JSONDecoder().decode([Message].self, from: data) {
            DispatchQueue.main.async {
                // Update the UI with the messages
                self.messages = messages  // Assume you have a `@State private var messages: [Message]` array
            }
        } else {
            print("Error decoding response or no data received")
        }
    }.resume()
}
*/
