import UIKit
import Firebase

class ViewController: UIViewController {

    @IBOutlet weak var videoImageView: UIImageView!

    var storageRef: StorageReference!
    var databaseRef: DatabaseReference!
    var currentFrame: UIImage?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Initialize Firebase
        FirebaseApp.configure()

        // Initialize Firebase references
        storageRef = Storage.storage().reference()
        databaseRef = Database.database().reference()

        // Start observing changes in the Firebase Realtime Database
        databaseRef.child("metadata").observe(.value) { (snapshot) in
            // Handle metadata updates (e.g., timestamp)
            // You can use this data for synchronization or control
        }

        // Start observing changes in Firebase Cloud Storage (video frames)
        let frameRef = storageRef.child("video_frames/frame.jpg")
        frameRef.getData(maxSize: 5 * 1024 * 1024) { [weak self] (data, error) in
            if let error = error {
                print("Error downloading frame: \(error.localizedDescription)")
            } else {
                if let data = data {
                    // Convert data to UIImage
                    self?.currentFrame = UIImage(data: data)
                    
                    // Update UI with the latest frame
                    DispatchQueue.main.async {
                        self?.videoImageView.image = self?.currentFrame
                    }
                }
            }
        }
    }
}
