// Record a USB-connected iPhone/iPad screen to a movie file via AVFoundation.
//
// Usage:
//   swift research/tools/record_device.swift list
//   swift research/tools/record_device.swift record <device-name-substring> <seconds> <out.mov>
//
// iOS screens only appear as capture devices after the process opts in through
// CoreMediaIO, so ffmpeg's avfoundation input cannot see them on its own.

import AVFoundation
import CoreMediaIO
import Foundation

func allowScreenCaptureDevices() {
    var address = CMIOObjectPropertyAddress(
        mSelector: CMIOObjectPropertySelector(kCMIOHardwarePropertyAllowScreenCaptureDevices),
        mScope: CMIOObjectPropertyScope(kCMIOObjectPropertyScopeGlobal),
        mElement: CMIOObjectPropertyElement(kCMIOObjectPropertyElementMain))
    var allow: UInt32 = 1
    CMIOObjectSetPropertyData(CMIOObjectID(kCMIOObjectSystemObject), &address, 0, nil,
                              UInt32(MemoryLayout<UInt32>.size), &allow)
}

func screenDevices() -> [AVCaptureDevice] {
    AVCaptureDevice.DiscoverySession(
        deviceTypes: [.external], mediaType: .muxed, position: .unspecified
    ).devices
}

// Screen devices show up a few seconds after opting in, so poll until one matches.
func waitForDevices(matching name: String = "", timeout: TimeInterval = 20) -> [AVCaptureDevice] {
    let deadline = Date().addingTimeInterval(timeout)
    while Date() < deadline {
        let devices = screenDevices().filter { name.isEmpty || $0.localizedName.contains(name) }
        if !devices.isEmpty { return devices }
        RunLoop.current.run(until: Date().addingTimeInterval(0.5))
    }
    return []
}

final class Recorder: NSObject, AVCaptureFileOutputRecordingDelegate {
    var finished = false
    var error: Error?

    func fileOutput(_ output: AVCaptureFileOutput, didFinishRecordingTo url: URL,
                    from connections: [AVCaptureConnection], error: Error?) {
        self.error = error
        finished = true
    }
}

allowScreenCaptureDevices()
let args = CommandLine.arguments.dropFirst()

switch args.first {
case "list":
    for device in waitForDevices() {
        print("\(device.localizedName)\t\(device.uniqueID)")
    }
case "record" where args.count == 4:
    let parts = Array(args)
    let name = parts[1], seconds = Double(parts[2])!, out = URL(fileURLWithPath: parts[3])
    guard let device = waitForDevices(matching: name).first else {
        FileHandle.standardError.write("no screen capture device matching \(name)\n".data(using: .utf8)!)
        exit(1)
    }
    let session = AVCaptureSession()
    let input = try AVCaptureDeviceInput(device: device)
    let output = AVCaptureMovieFileOutput()
    session.addInput(input)
    session.addOutput(output)
    session.startRunning()
    // The muxed screen device needs a moment before its connection can record.
    RunLoop.current.run(until: Date().addingTimeInterval(2))
    try? FileManager.default.removeItem(at: out)
    let recorder = Recorder()
    output.startRecording(to: out, recordingDelegate: recorder)
    print("recording \(device.localizedName) for \(seconds)s -> \(out.path)")
    RunLoop.current.run(until: Date().addingTimeInterval(seconds))
    output.stopRecording()
    while !recorder.finished { RunLoop.current.run(until: Date().addingTimeInterval(0.1)) }
    session.stopRunning()
    if let error = recorder.error { print("finished with: \(error.localizedDescription)") }
default:
    print("usage: record_device.swift list | record <name> <seconds> <out.mov>")
    exit(2)
}
