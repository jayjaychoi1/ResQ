import Foundation
import AVFoundation

class AudioRecorder: NSObject, AVAudioRecorderDelegate {
    private var audioRecorder: AVAudioRecorder?
    private var recordingSession: AVAudioSession?
    private var audioURL: URL?

    override init() {
        super.init()
        recordingSession = AVAudioSession.sharedInstance()
    }

    func requestPermission() async -> Bool {
        do {
            return try await AVAudioApplication.requestRecordPermission()
        } catch {
            print("❌ Permission request error: \(error)")
            return false
        }
    }

    func startRecording() {
        guard let recordingSession = recordingSession else {
            print("❌ Unable to access recording session")
            return
        }
        
        do {
            // Configure audio session for recording
            try recordingSession.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .mixWithOthers])
            try recordingSession.setActive(true)

            // Create a unique filename with timestamp
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "yyyyMMdd_HHmmss"
            let timestamp = dateFormatter.string(from: Date())
            let filename = "recording_\(timestamp).m4a"
            
            audioURL = getDocumentsDirectory().appendingPathComponent(filename)
            
            guard let audioURL = audioURL else {
                print("❌ Failed to create audio file URL")
                return
            }

            let settings: [String: Any] = [
                AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                AVSampleRateKey: 44100.0,
                AVNumberOfChannelsKey: 1,
                AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue,
                AVEncoderBitRateKey: 128000
            ]

            // Ensure directory exists
            try FileManager.default.createDirectory(
                at: audioURL.deletingLastPathComponent(),
                withIntermediateDirectories: true
            )

            audioRecorder = try AVAudioRecorder(url: audioURL, settings: settings)
            audioRecorder?.delegate = self
            
            // Prepare the recorder
            if audioRecorder?.prepareToRecord() == true {
                if audioRecorder?.record() == true {
                    print("✅ Recording started, saving to \(audioURL)")
                } else {
                    print("❌ Failed to start recording")
                }
            } else {
                print("❌ Failed to prepare recording")
            }
        } catch {
            print("❌ Recording setup error: \(error)")
            // Print more details about the error
            print("Error details: \(error.localizedDescription)")
        }
    }

    func stopRecording() {
        audioRecorder?.stop()
        
        if let url = audioURL {
            print("✅ Recording stopped. File saved at: \(url)")
        }
        
        // Optional: Print file size to verify recording
        if let url = audioURL, let attributes = try? FileManager.default.attributesOfItem(atPath: url.path) {
            let fileSize = attributes[.size] as? Int64 ?? 0
            print("📦 Recording file size: \(fileSize) bytes")
        }
    }

    private func getDocumentsDirectory() -> URL {
        return FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }

    // AVAudioRecorderDelegate methods for additional error tracking
    func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        if flag {
            print("✅ Recording finished successfully")
        } else {
            print("❌ Recording did not finish successfully")
        }
    }

    func audioRecorderEncodeErrorDidOccur(_ recorder: AVAudioRecorder, error: Error?) {
        if let error = error {
            print("❌ Encoding error: \(error.localizedDescription)")
        }
    }
}
