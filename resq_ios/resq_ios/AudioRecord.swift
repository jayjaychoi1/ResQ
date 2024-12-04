import Foundation
import AVFoundation

class AudioRecorder: NSObject, AVAudioRecorderDelegate {
    private var audioRecorder: AVAudioRecorder?
    private var recordingSession: AVAudioSession?
    private var audioURL: URL?

    override init() {
            super.init()
            recordingSession = AVAudioSession.sharedInstance()
    }// More inits

    func requestPermission(completion: @escaping (Bool) -> Void) {
        AVAudioApplication.requestRecordPermission(completionHandler: { granted in
            DispatchQueue.main.async {
                completion(granted)
            }
        })
    }// get ya per mis222

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
            audioRecorder?.prepareToRecord()
            audioRecorder?.record()
            
            print("✅ Recording started, saving to \(audioURL)")
        } catch {
            print("❌ Recording setup error: \(error)")
        }
    }

    func stopRecording() -> URL? {
        audioRecorder?.stop()
        
        guard let url = audioURL else { return nil }
        
        // Optional: Print file size to verify recording
        if let attributes = try? FileManager.default.attributesOfItem(atPath: url.path) {
            let fileSize = attributes[.size] as? Int64 ?? 0
            print("📦 Recording file size: \(fileSize) bytes")
        }
        
        return url
    }

    private func getDocumentsDirectory() -> URL {
        return FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
}
